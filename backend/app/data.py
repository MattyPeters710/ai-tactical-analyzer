"""
Real-world sports data layer.

Teams, standings, and form are fetched live from ESPN's public JSON API
via `sports_api`. This module exposes the same async helpers the rest of
the app expects, returning dicts that slot directly into `analyzer.py`.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from app import sports_api

SPORTS = [
    {"id": "soccer", "name": "Soccer", "icon": "goal"},
    {"id": "basketball", "name": "Basketball", "icon": "basketball"},
    {"id": "american_football", "name": "American Football", "icon": "football"},
    {"id": "cricket", "name": "Cricket", "icon": "cricket"},
]


async def get_all_teams() -> List[Dict[str, Any]]:
    teams = await sports_api.list_all_teams()
    return [_team_summary(t) for t in teams]


async def get_teams_by_sport(sport: str) -> List[Dict[str, Any]]:
    teams = await sports_api.list_teams_for_sport(sport)
    return [_team_summary(t) for t in teams]


async def get_team(team_id: str) -> Optional[Dict[str, Any]]:
    full = await sports_api.get_team_full(team_id)
    if not full:
        return None
    stats = sports_api.compute_stats(full["sport"], full["record"])
    form = full.get("recent_form") or []
    stats["form"] = sports_api.form_rating(form)
    return {
        "id": full["id"],
        "name": full["name"],
        "sport": full["sport"],
        "league": full["league"],
        "country": full.get("location") or "",
        "logo_color": full.get("logo_color") or "#64748b",
        "alt_color": full.get("alt_color"),
        "logo_url": full.get("logo_url"),
        "abbreviation": full.get("abbreviation"),
        "short_name": full.get("short_name"),
        "record_summary": full.get("record_summary", ""),
        "standing_summary": full.get("standing_summary", ""),
        "stats": stats,
        "recent_form": form,
        "season_record": full.get("season_record", {}),
        "raw_record": full.get("record", {}),
        "source": full.get("source", "ESPN"),
    }


def _team_summary(team: Dict[str, Any]) -> Dict[str, Any]:
    """Shape an entry from sports_api.list_* into our TeamSummary dict."""
    return {
        "id": team["id"],
        "name": team["name"],
        "sport": team["sport"],
        "league": team["league"],
        "country": team.get("location") or "",
        "logo_color": team.get("logo_color") or "#64748b",
        "logo_url": team.get("logo_url"),
        "abbreviation": team.get("abbreviation"),
        "short_name": team.get("short_name"),
    }
