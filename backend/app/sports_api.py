"""
ESPN public sports API client with in-memory TTL caching.

ESPN exposes an undocumented but widely used JSON API under
`site.api.espn.com` that returns team lists, team records with real
performance stats, and per-team schedules. We use it as the source of
truth for all real-world data in the analyzer.

Results are cached in-process with a configurable TTL so we do not hit
ESPN on every request; team data changes at most a few times per day.
"""

from __future__ import annotations

import asyncio
import logging
import os
import time
from typing import Any, Dict, List, Optional, Tuple

import httpx

logger = logging.getLogger(__name__)

ESPN_BASE = "https://site.api.espn.com/apis/site/v2/sports"
CACHE_TTL_SECONDS = int(os.environ.get("SPORTS_API_CACHE_TTL", "3600"))
HTTP_TIMEOUT = float(os.environ.get("SPORTS_API_TIMEOUT", "8.0"))


# Mapping from our internal sport ids to the ESPN (sport, league) pairs we
# pull teams from. The order of leagues determines the order teams appear
# in the combined list per sport.
SPORT_LEAGUES: Dict[str, List[Tuple[str, str, str]]] = {
    # (espn_sport, espn_league, display_league)
    "soccer": [
        ("soccer", "eng.1", "Premier League"),
        ("soccer", "esp.1", "La Liga"),
        ("soccer", "ger.1", "Bundesliga"),
        ("soccer", "ita.1", "Serie A"),
        ("soccer", "fra.1", "Ligue 1"),
    ],
    "basketball": [
        ("basketball", "nba", "NBA"),
    ],
    "american_football": [
        ("football", "nfl", "NFL"),
    ],
}


# ---------------------------------------------------------------------------
# Simple async-safe TTL cache
# ---------------------------------------------------------------------------


class _TTLCache:
    def __init__(self, ttl_seconds: int) -> None:
        self._ttl = ttl_seconds
        self._store: Dict[str, Tuple[float, Any]] = {}
        self._locks: Dict[str, asyncio.Lock] = {}

    def _lock_for(self, key: str) -> asyncio.Lock:
        lock = self._locks.get(key)
        if lock is None:
            lock = asyncio.Lock()
            self._locks[key] = lock
        return lock

    async def get_or_fetch(self, key: str, fetch):
        entry = self._store.get(key)
        now = time.time()
        if entry is not None and now - entry[0] < self._ttl:
            return entry[1]
        async with self._lock_for(key):
            # Re-check after acquiring the lock
            entry = self._store.get(key)
            if entry is not None and time.time() - entry[0] < self._ttl:
                return entry[1]
            value = await fetch()
            self._store[key] = (time.time(), value)
            return value

    def clear(self) -> None:
        self._store.clear()


_cache = _TTLCache(CACHE_TTL_SECONDS)


# ---------------------------------------------------------------------------
# HTTP layer
# ---------------------------------------------------------------------------


async def _get_json(url: str) -> Dict[str, Any]:
    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT, follow_redirects=True) as client:
        resp = await client.get(url, headers={"User-Agent": "ai-tactical-analyzer/1.0"})
        resp.raise_for_status()
        return resp.json()


# ---------------------------------------------------------------------------
# ESPN fetchers (cached)
# ---------------------------------------------------------------------------


async def _fetch_league_teams(espn_sport: str, espn_league: str) -> List[Dict[str, Any]]:
    """Return the raw list of team objects for a league."""
    async def do_fetch() -> List[Dict[str, Any]]:
        url = f"{ESPN_BASE}/{espn_sport}/{espn_league}/teams"
        data = await _get_json(url)
        sports = data.get("sports") or []
        if not sports:
            return []
        leagues = sports[0].get("leagues") or []
        if not leagues:
            return []
        return [entry.get("team", {}) for entry in leagues[0].get("teams", [])]

    return await _cache.get_or_fetch(f"teams:{espn_sport}:{espn_league}", do_fetch)


async def _fetch_team_detail(
    espn_sport: str, espn_league: str, espn_team_id: str
) -> Dict[str, Any]:
    """Return the ESPN team detail including record and stats."""
    async def do_fetch() -> Dict[str, Any]:
        url = f"{ESPN_BASE}/{espn_sport}/{espn_league}/teams/{espn_team_id}"
        data = await _get_json(url)
        return data.get("team", {})

    return await _cache.get_or_fetch(
        f"team:{espn_sport}:{espn_league}:{espn_team_id}", do_fetch
    )


async def _fetch_team_schedule(
    espn_sport: str, espn_league: str, espn_team_id: str
) -> List[Dict[str, Any]]:
    """Return a list of events for a team's current season schedule."""
    async def do_fetch() -> List[Dict[str, Any]]:
        url = (
            f"{ESPN_BASE}/{espn_sport}/{espn_league}/teams/{espn_team_id}/schedule"
        )
        data = await _get_json(url)
        return data.get("events") or []

    return await _cache.get_or_fetch(
        f"schedule:{espn_sport}:{espn_league}:{espn_team_id}", do_fetch
    )


# ---------------------------------------------------------------------------
# Public, sport-agnostic API
# ---------------------------------------------------------------------------


def _team_id(sport: str, espn_league: str, espn_team_id: str) -> str:
    """Build our internal stable team id from the ESPN pair."""
    league_slug = espn_league.replace(".", "")
    return f"{sport}_{league_slug}_{espn_team_id}"


def _parse_internal_id(team_id: str) -> Optional[Tuple[str, str, str]]:
    """Inverse of `_team_id`: returns (sport, espn_league, espn_team_id)."""
    parts = team_id.split("_")
    if len(parts) < 3:
        return None
    if parts[0] == "american" and len(parts) >= 4 and parts[1] == "football":
        sport = "american_football"
        league_slug = parts[2]
        espn_team_id = "_".join(parts[3:])
    else:
        sport = parts[0]
        league_slug = parts[1]
        espn_team_id = "_".join(parts[2:])
    # Restore dotted league (e.g. "eng1" -> "eng.1"). Only soccer uses dots.
    if sport == "soccer" and len(league_slug) >= 4 and league_slug[-1].isdigit():
        espn_league = f"{league_slug[:-1]}.{league_slug[-1]}"
    else:
        espn_league = league_slug
    return sport, espn_league, espn_team_id


def _espn_sport_for(sport: str) -> str:
    if sport == "american_football":
        return "football"
    return sport


def _pick_logo(team: Dict[str, Any]) -> Optional[str]:
    logos = team.get("logos") or []
    for l in logos:
        href = l.get("href")
        if href:
            return href
    return None


def _normalize_color(color: Optional[str]) -> str:
    if not color:
        return "#64748b"
    color = color.strip().lstrip("#")
    if len(color) == 6:
        return f"#{color.upper()}"
    return "#64748b"


def _record_items(team_detail: Dict[str, Any]) -> Dict[str, Any]:
    """Pull out the primary "Overall Record" stats dict."""
    rec = team_detail.get("record") or {}
    items = rec.get("items") or []
    if not items:
        return {}
    overall = None
    for it in items:
        if it.get("type") == "total":
            overall = it
            break
    if overall is None:
        overall = items[0]
    stats = {}
    for s in overall.get("stats") or []:
        name = s.get("name")
        value = s.get("value")
        if name is not None:
            stats[name] = value
    stats["_summary"] = overall.get("summary", "")
    return stats


async def list_teams_for_sport(sport: str) -> List[Dict[str, Any]]:
    """Return lightweight team summaries for a sport."""
    leagues = SPORT_LEAGUES.get(sport)
    if not leagues:
        return []

    teams: List[Dict[str, Any]] = []
    for espn_sport, espn_league, display_league in leagues:
        try:
            raw_teams = await _fetch_league_teams(espn_sport, espn_league)
        except httpx.HTTPError as exc:
            logger.warning("Failed to fetch %s/%s teams: %s", espn_sport, espn_league, exc)
            continue
        for t in raw_teams:
            espn_id = t.get("id")
            if not espn_id:
                continue
            teams.append(
                {
                    "_espn": {
                        "sport": espn_sport,
                        "league": espn_league,
                        "team_id": espn_id,
                    },
                    "id": _team_id(sport, espn_league, espn_id),
                    "name": t.get("displayName") or t.get("name") or "Unknown",
                    "short_name": t.get("shortDisplayName") or t.get("abbreviation"),
                    "abbreviation": t.get("abbreviation"),
                    "sport": sport,
                    "league": display_league,
                    "logo_color": _normalize_color(t.get("color")),
                    "logo_url": _pick_logo(t),
                    "location": t.get("location"),
                }
            )
    return teams


async def list_all_teams() -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    for sport in SPORT_LEAGUES:
        results.extend(await list_teams_for_sport(sport))
    return results


async def get_team_full(team_id: str) -> Optional[Dict[str, Any]]:
    """Return a full team dict (metadata + real stats + recent form)."""
    parsed = _parse_internal_id(team_id)
    if not parsed:
        return None
    sport, espn_league, espn_team_id = parsed
    espn_sport = _espn_sport_for(sport)

    # Find matching summary + detail + schedule in parallel.
    try:
        detail_task = asyncio.create_task(
            _fetch_team_detail(espn_sport, espn_league, espn_team_id)
        )
        schedule_task = asyncio.create_task(
            _fetch_team_schedule(espn_sport, espn_league, espn_team_id)
        )
        detail, schedule = await asyncio.gather(detail_task, schedule_task)
    except httpx.HTTPError as exc:
        logger.warning("ESPN fetch failed for %s: %s", team_id, exc)
        return None

    if not detail:
        return None

    # Find display league name from our mapping.
    display_league = espn_league
    for _, lslug, display in SPORT_LEAGUES.get(sport, []):
        if lslug == espn_league:
            display_league = display
            break

    record = _record_items(detail)
    form = _compute_form(schedule, espn_team_id)
    season_record = _build_season_record(sport, record)

    return {
        "id": team_id,
        "name": detail.get("displayName") or detail.get("name") or "Unknown",
        "short_name": detail.get("shortDisplayName") or detail.get("abbreviation"),
        "abbreviation": detail.get("abbreviation"),
        "sport": sport,
        "league": display_league,
        "location": detail.get("location"),
        "logo_color": _normalize_color(detail.get("color")),
        "alt_color": _normalize_color(detail.get("alternateColor")),
        "logo_url": _pick_logo(detail),
        "record_summary": record.get("_summary", ""),
        "standing_summary": detail.get("standingSummary", ""),
        "record": record,
        "recent_form": form,
        "season_record": season_record,
        "source": "ESPN",
    }


def _compute_form(events: List[Dict[str, Any]], espn_team_id: str) -> List[str]:
    """Compute last-5 form (W/D/L) from a team's schedule."""
    played: List[str] = []
    for event in events:
        comp = (event.get("competitions") or [{}])[0]
        status = comp.get("status", {}).get("type", {})
        if not status.get("completed"):
            continue
        competitors = comp.get("competitors", [])
        if len(competitors) < 2:
            continue
        team_side = None
        other_side = None
        for c in competitors:
            if c.get("id") == espn_team_id:
                team_side = c
            else:
                other_side = c
        if team_side is None or other_side is None:
            continue
        winner = team_side.get("winner")
        try:
            team_score = int(float(team_side.get("score", {}).get("value") or team_side.get("score", {}).get("displayValue") or 0))
            other_score = int(float(other_side.get("score", {}).get("value") or other_side.get("score", {}).get("displayValue") or 0))
        except (TypeError, ValueError):
            team_score = other_score = 0
        if winner is True:
            played.append("W")
        elif winner is False and team_score != other_score:
            played.append("L")
        elif team_score == other_score and team_score > 0:
            played.append("D")
        else:
            played.append("L")
    return played[-5:]


def _build_season_record(sport: str, record: Dict[str, Any]) -> Dict[str, Any]:
    """Extract a normalized season record dict from raw ESPN stats."""
    def _num(key: str) -> Optional[float]:
        v = record.get(key)
        if v is None:
            return None
        try:
            return float(v)
        except (TypeError, ValueError):
            return None

    wins = _num("wins")
    losses = _num("losses")
    ties = _num("ties") or 0
    games_played = _num("gamesPlayed")
    points_for = _num("pointsFor")
    points_against = _num("pointsAgainst")
    avg_for = _num("avgPointsFor")
    avg_against = _num("avgPointsAgainst")

    result: Dict[str, Any] = {}
    if wins is not None:
        result["wins"] = int(wins)
    if losses is not None:
        result["losses"] = int(losses)
    if sport == "soccer":
        result["draws"] = int(ties)
        if points_for is not None:
            result["goals_for"] = int(points_for)
        if points_against is not None:
            result["goals_against"] = int(points_against)
    else:
        if avg_for is not None:
            result["points_per_game"] = round(avg_for, 1)
        if avg_against is not None:
            result["points_allowed"] = round(avg_against, 1)
    if games_played is not None:
        result["games_played"] = int(games_played)
    return result


def compute_stats(sport: str, record: Dict[str, Any]) -> Dict[str, int]:
    """Derive analyzer-friendly 0-100 stat ratings from real performance data.

    All six ratings are defined for every sport so the matchup comparator
    and the radar chart work uniformly.
    """
    def _f(key: str, default: float = 0.0) -> float:
        v = record.get(key)
        try:
            return float(v) if v is not None else default
        except (TypeError, ValueError):
            return default

    gp = max(_f("gamesPlayed"), 1)
    wins = _f("wins")
    losses = _f("losses")
    ties = _f("ties")
    pf = _f("pointsFor")
    pa = _f("pointsAgainst")
    avg_for = _f("avgPointsFor") or (pf / gp if gp else 0)
    avg_against = _f("avgPointsAgainst") or (pa / gp if gp else 0)
    point_diff = _f("pointDifferential") or (pf - pa)
    per_game_diff = point_diff / gp if gp else 0

    if sport == "soccer":
        # Scoring 2.5 goals per match = elite (100). 0 goals = 0.
        attack = _clamp(avg_for * 40)
        # Conceding 0 = elite (100). 2.5 gpg conceded = 0.
        defense = _clamp(100 - avg_against * 40)
        # Points percentage in a 3-for-a-win league.
        points = wins * 3 + ties
        pts_pct = points / (gp * 3) if gp else 0
        efficiency = _clamp(pts_pct * 100)
        # +2 goal diff/game = elite (100). 0 = 50. -2 = 0.
        differential = _clamp(50 + per_game_diff * 25)
    elif sport == "basketball":
        attack = _clamp((avg_for - 95) * 4 + 65)  # 95 ppg → 65, 120 → 165→clamped
        defense = _clamp((115 - avg_against) * 4 + 60)
        win_pct = wins / gp if gp else 0
        efficiency = _clamp(win_pct * 100)
        differential = _clamp(50 + per_game_diff * 5)
    else:  # american_football
        attack = _clamp((avg_for - 17) * 6 + 55)
        defense = _clamp((24 - avg_against) * 6 + 55)
        win_pct = wins / gp if gp else 0
        efficiency = _clamp(win_pct * 100)
        differential = _clamp(50 + per_game_diff * 3)

    # Form rating from recent streak/results is added elsewhere via form list.
    # Consistency inversely tracks losses.
    loss_rate = losses / gp if gp else 0
    consistency = _clamp(100 - loss_rate * 120)

    return {
        "attack": int(round(attack)),
        "defense": int(round(defense)),
        "efficiency": int(round(efficiency)),
        "differential": int(round(differential)),
        "consistency": int(round(consistency)),
    }


def _clamp(v: float, lo: float = 0.0, hi: float = 100.0) -> float:
    if v != v:  # NaN
        return 50.0
    return max(lo, min(hi, v))


def form_rating(form: List[str]) -> int:
    """Convert a W/D/L form list into a 0-100 rating."""
    if not form:
        return 50
    points = 0
    for r in form:
        if r == "W":
            points += 3
        elif r == "D":
            points += 1
    return int(round(points / (len(form) * 3) * 100))


def clear_cache() -> None:
    _cache.clear()
