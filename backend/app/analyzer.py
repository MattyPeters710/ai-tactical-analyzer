"""
AI Tactical Analyzer Engine.

Generates narrative tactical analysis from real-world performance data
(season record, goal/point differentials, recent form) returned by the
ESPN-backed `data` layer. Ratings are derived, not invented.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

# Human-readable labels for the derived performance stats.
STAT_LABELS: Dict[str, str] = {
    "attack": "Attack",
    "defense": "Defense",
    "efficiency": "Efficiency",
    "differential": "Point Differential",
    "consistency": "Consistency",
    "form": "Recent Form",
}


def _calculate_overall_rating(stats: Dict[str, int]) -> float:
    if not stats:
        return 0.0
    values = list(stats.values())
    return round(sum(values) / len(values), 1)


def _get_stat_tier(value: int) -> str:
    if value >= 88:
        return "Elite"
    if value >= 78:
        return "Excellent"
    if value >= 68:
        return "Very Good"
    if value >= 55:
        return "Average"
    if value >= 40:
        return "Below Average"
    return "Poor"


def _sport_noun(sport: str) -> str:
    if sport == "soccer":
        return "goal"
    if sport == "american_football":
        return "point"
    return "point"


def _sport_noun_plural(sport: str) -> str:
    return _sport_noun(sport) + "s"


def _per_game(record: Dict[str, Any], key: str) -> float:
    total = record.get(key)
    gp = record.get("gamesPlayed") or 0
    try:
        if total is None or not gp:
            return 0.0
        return round(float(total) / float(gp), 2)
    except (TypeError, ValueError):
        return 0.0


def _record_string(team: Dict[str, Any]) -> str:
    sr = team.get("season_record") or {}
    summary = team.get("record_summary")
    if summary:
        return summary
    if not sr:
        return ""
    if team["sport"] == "soccer":
        return f"{sr.get('wins', 0)}-{sr.get('draws', 0)}-{sr.get('losses', 0)}"
    return f"{sr.get('wins', 0)}-{sr.get('losses', 0)}"


def _identify_tactical_identity(team: Dict[str, Any]) -> str:
    stats = team["stats"]
    sport = team["sport"]
    atk = stats.get("attack", 0)
    dfn = stats.get("defense", 0)
    eff = stats.get("efficiency", 0)
    form = stats.get("form", 0)
    diff = stats.get("differential", 0)

    if atk >= 80 and dfn >= 80:
        if sport == "soccer":
            return (
                f"Complete Side — {team['name']} excels at both ends of the pitch, "
                f"creating chances freely while suffocating opponents in defense."
            )
        return (
            f"Two-Way Juggernaut — {team['name']} dominates on both offense and "
            f"defense, overwhelming opponents with balanced excellence."
        )
    if atk >= 80 and dfn < 65:
        if sport == "soccer":
            return (
                f"Relentless Attacker — {team['name']} plays wide-open, high-scoring "
                f"football. They outscore rather than outlast their opponents."
            )
        return (
            f"Offensive Powerhouse — {team['name']} leans on elite scoring output. "
            f"Their formula: force opponents into a shootout."
        )
    if dfn >= 80 and atk < 65:
        if sport == "soccer":
            return (
                f"Defensive Stalwart — {team['name']} grinds out results on the back "
                f"of a miserly, well-organized backline."
            )
        return (
            f"Defensive Fortress — {team['name']} wins games with suffocating defense "
            f"and disciplined execution."
        )
    if form >= 80 and eff < 65:
        return (
            f"Surging Underdog — {team['name']} is peaking at the right time, "
            f"riding a recent hot streak that has outpaced their season-long profile."
        )
    if eff >= 75 and diff >= 70:
        return (
            f"Efficient Winner — {team['name']} wins the games they are supposed to. "
            f"Rarely blown out, consistently on the right side of close contests."
        )
    if form < 40 and eff >= 55:
        return (
            f"Slumping Contender — {team['name']} has the talent of a contender but "
            f"is struggling for form at a critical stretch of the season."
        )
    return (
        f"Balanced Operator — {team['name']} does not overwhelm in any single area but "
        f"stays competitive through a well-rounded profile."
    )


def _generate_key_insights(team: Dict[str, Any]) -> List[str]:
    stats = team["stats"]
    sport = team["sport"]
    record = team.get("raw_record") or {}
    form: List[str] = team.get("recent_form") or []
    insights: List[str] = []
    name = team["name"]

    avg_for = _per_game(record, "pointsFor")
    avg_against = _per_game(record, "pointsAgainst")
    gp = int(record.get("gamesPlayed") or 0) or None
    wins = int(record.get("wins") or 0)
    losses = int(record.get("losses") or 0)
    ties = int(record.get("ties") or 0)
    point_diff = record.get("pointDifferential")

    if avg_for and gp:
        noun = _sport_noun_plural(sport)
        insights.append(
            f"{name} averages {avg_for} {noun} per game over {gp} matches — "
            f"their scoring output translates to an attack rating of "
            f"{stats.get('attack', 0)}/100."
        )
    if avg_against and gp:
        noun = _sport_noun_plural(sport)
        insights.append(
            f"Opponents average {avg_against} {noun} per game against {name}, "
            f"yielding a defensive rating of {stats.get('defense', 0)}/100."
        )
    if gp:
        if sport == "soccer":
            insights.append(
                f"Season record: {wins}W-{ties}D-{losses}L across {gp} matches. "
                f"Points per game: {round((wins * 3 + ties) / gp, 2)}."
            )
        else:
            win_pct = round(wins / gp * 100, 1) if gp else 0
            insights.append(
                f"Season record: {wins}-{losses} ({win_pct}% win rate) over {gp} games."
            )
    if point_diff is not None:
        try:
            pd = int(float(point_diff))
            if pd > 0:
                insights.append(
                    f"Positive {_sport_noun(sport)} differential of +{pd} indicates they "
                    f"consistently outplay opponents on the scoreboard."
                )
            elif pd < 0:
                insights.append(
                    f"{_sport_noun(sport).capitalize()} differential of {pd} signals "
                    f"they are getting outplayed more often than not this season."
                )
        except (TypeError, ValueError):
            pass
    if form:
        wins_5 = form.count("W")
        losses_5 = form.count("L")
        draws_5 = form.count("D")
        form_str = "-".join(form)
        if wins_5 >= 4:
            insights.append(
                f"Red-hot recent form ({form_str}). Momentum is firmly on their side."
            )
        elif losses_5 >= 4:
            insights.append(
                f"Alarming recent form ({form_str}). Confidence and cohesion are question marks."
            )
        else:
            insights.append(
                f"Recent form: {form_str} ({wins_5}W-{draws_5}D-{losses_5}L in last {len(form)})."
            )
    if team.get("standing_summary"):
        insights.append(f"League position: {team['standing_summary']}.")

    if not insights:
        insights.append(
            f"Limited performance data is available for {name} this season. "
            f"Ratings are based on what has been recorded to date."
        )
    return insights


def _derive_strengths(team: Dict[str, Any]) -> List[str]:
    stats = team["stats"]
    out: List[str] = []
    if stats.get("attack", 0) >= 75:
        out.append("Potent scoring output")
    if stats.get("defense", 0) >= 75:
        out.append("Stingy defense")
    if stats.get("efficiency", 0) >= 70:
        out.append("Converts talent into wins")
    if stats.get("differential", 0) >= 70:
        out.append("Controls games on the scoreboard")
    if stats.get("form", 0) >= 70:
        out.append("Strong recent form")
    if stats.get("consistency", 0) >= 75:
        out.append("Avoids bad losses")
    if not out:
        out.append("Balanced profile without glaring flaws")
    return out


def _derive_weaknesses(team: Dict[str, Any]) -> List[str]:
    stats = team["stats"]
    out: List[str] = []
    if stats.get("attack", 0) < 55:
        out.append("Struggles to generate offense")
    if stats.get("defense", 0) < 55:
        out.append("Leaky defense")
    if stats.get("efficiency", 0) < 50:
        out.append("Poor win rate relative to opportunities")
    if stats.get("differential", 0) < 45:
        out.append("Frequently outscored")
    if stats.get("form", 0) < 40:
        out.append("Cold recent stretch")
    if stats.get("consistency", 0) < 55:
        out.append("Prone to losses in clusters")
    if not out:
        out.append("No clear statistical weakness")
    return out


def _generate_recommendations(team: Dict[str, Any]) -> List[str]:
    stats = team["stats"]
    sport = team["sport"]
    recs: List[str] = []
    if stats.get("attack", 0) < 60:
        if sport == "soccer":
            recs.append(
                "Generating more high-quality chances should be the top priority. "
                "Consider investing in a proven finisher or increasing attacking risk in build-up."
            )
        else:
            recs.append(
                "Scoring output is below par. Explore pace/volume-of-possession increases "
                "or target a reliable offensive contributor."
            )
    if stats.get("defense", 0) < 60:
        if sport == "soccer":
            recs.append(
                "Conceding too readily. Tightening defensive shape and improving ball-winning "
                "in midfield would reduce opponents' high-quality chances."
            )
        else:
            recs.append(
                "Opponents are scoring too easily. Focus on defensive scheme discipline and shoring "
                "up transition defense."
            )
    if stats.get("form", 0) < 50:
        recs.append(
            "Recent form is a concern. Short-term tactical adjustments and player rotation "
            "could arrest the slide before it calcifies into a pattern."
        )
    if stats.get("consistency", 0) < 55:
        recs.append(
            "Losses are coming in clusters. Addressing effort/focus issues and tightening "
            "pre-match preparation could smooth out performance."
        )
    if not recs:
        recs.append(
            f"This is a well-constructed side with no obvious areas of underperformance. "
            f"Focus on managing workload and sustaining current levels across the remainder of the season."
        )
    return recs


def analyze_team(team: Dict[str, Any]) -> Dict[str, Any]:
    stats = team["stats"]
    overall = _calculate_overall_rating(stats)
    identity = _identify_tactical_identity(team)
    insights = _generate_key_insights(team)
    strengths = _derive_strengths(team)
    weaknesses = _derive_weaknesses(team)

    sorted_stats = sorted(stats.items(), key=lambda x: x[1], reverse=True)
    top_attributes = [
        {"name": k, "value": v, "tier": _get_stat_tier(v), "label": STAT_LABELS.get(k, k)}
        for k, v in sorted_stats[:3]
    ]
    weak_attributes = [
        {"name": k, "value": v, "tier": _get_stat_tier(v), "label": STAT_LABELS.get(k, k)}
        for k, v in sorted_stats[-3:]
    ]

    tactical_recommendations = _generate_recommendations(team)

    return {
        "team_id": team["id"],
        "team_name": team["name"],
        "sport": team["sport"],
        "league": team.get("league", ""),
        "country": team.get("country", ""),
        "logo_color": team.get("logo_color", "#64748b"),
        "logo_url": team.get("logo_url"),
        "overall_rating": overall,
        "tactical_identity": identity,
        "record_summary": _record_string(team),
        "standing_summary": team.get("standing_summary", ""),
        "stats": stats,
        "stat_labels": STAT_LABELS,
        "top_attributes": top_attributes,
        "weak_attributes": weak_attributes,
        "key_insights": insights,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "tactical_recommendations": tactical_recommendations,
        "season_record": team.get("season_record", {}),
        "recent_form": team.get("recent_form", []),
        "source": team.get("source", "ESPN"),
    }


def _identify_key_battles(team1: Dict[str, Any], team2: Dict[str, Any]) -> List[Dict[str, str]]:
    battles: List[Dict[str, str]] = []
    sport = team1["sport"]
    s1 = team1["stats"]
    s2 = team2["stats"]
    noun = _sport_noun_plural(sport)

    battles.append({
        "battle": "Attack vs Defense",
        "description": (
            f"{team1['name']}'s attack ({s1.get('attack', 0)}/100) meets "
            f"{team2['name']}'s defense ({s2.get('defense', 0)}/100). "
            f"Whichever side wins this matchup typically wins the game."
        ),
    })
    battles.append({
        "battle": "Defense vs Attack",
        "description": (
            f"Conversely, {team2['name']}'s attack ({s2.get('attack', 0)}/100) "
            f"tests {team1['name']}'s defense ({s1.get('defense', 0)}/100). "
            f"Expect the team with the edge here to keep more {noun} off the board."
        ),
    })
    battles.append({
        "battle": "Momentum Check",
        "description": (
            f"{team1['name']} enters with form {s1.get('form', 0)}/100, "
            f"{team2['name']} with {s2.get('form', 0)}/100. Short-term momentum "
            f"often tips tight contests."
        ),
    })
    battles.append({
        "battle": "Efficiency Battle",
        "description": (
            f"Win-rate efficiency: {team1['name']} {s1.get('efficiency', 0)}/100 vs "
            f"{team2['name']} {s2.get('efficiency', 0)}/100. The team that converts "
            f"more advantages into results has the edge on paper."
        ),
    })
    return battles


def _generate_matchup_analysis(
    team1: Dict[str, Any],
    team2: Dict[str, Any],
    t1_advantages: List[Tuple[str, int]],
    t2_advantages: List[Tuple[str, int]],
) -> List[str]:
    analysis: List[str] = []
    if len(t1_advantages) > len(t2_advantages):
        analysis.append(
            f"{team1['name']} holds the statistical edge in "
            f"{len(t1_advantages)} categories compared to {team2['name']}'s "
            f"{len(t2_advantages)}, suggesting more avenues to victory."
        )
    elif len(t2_advantages) > len(t1_advantages):
        analysis.append(
            f"{team2['name']} holds the statistical edge in "
            f"{len(t2_advantages)} categories compared to {team1['name']}'s "
            f"{len(t1_advantages)}, entering with the broader set of advantages."
        )
    else:
        analysis.append(
            f"An evenly matched contest. Both teams hold advantages in "
            f"{len(t1_advantages)} categories each — expect a tight affair."
        )

    # Record-based narrative
    for team in (team1, team2):
        record = team.get("raw_record") or {}
        gp = record.get("gamesPlayed")
        point_diff = record.get("pointDifferential")
        if gp and point_diff is not None:
            analysis.append(
                f"{team['name']}'s season profile: "
                f"{_record_string(team)} record with a "
                f"{int(float(point_diff)):+d} {_sport_noun(team['sport'])} differential over {int(gp)} games."
            )

    # Contrasting strengths
    for stat, margin in t1_advantages[:1]:
        analysis.append(
            f"{team1['name']} is materially better in {STAT_LABELS.get(stat, stat)} "
            f"(margin of {margin}) — expect them to lean on this edge."
        )
    for stat, margin in t2_advantages[:1]:
        analysis.append(
            f"{team2['name']} is materially better in {STAT_LABELS.get(stat, stat)} "
            f"(margin of {margin}) — a natural avenue for them to control the game."
        )
    return analysis


def _generate_prediction(team1: Dict[str, Any], team2: Dict[str, Any], t1_prob: float) -> Dict[str, Any]:
    sport = team1["sport"]

    if t1_prob > 60:
        favorite, underdog, confidence = team1["name"], team2["name"], "High"
    elif t1_prob > 52:
        favorite, underdog, confidence = team1["name"], team2["name"], "Moderate"
    elif t1_prob > 48:
        favorite, underdog, confidence = "Toss-up", "", "Low"
    elif t1_prob > 40:
        favorite, underdog, confidence = team2["name"], team1["name"], "Moderate"
    else:
        favorite, underdog, confidence = team2["name"], team1["name"], "High"

    r1 = team1.get("raw_record") or {}
    r2 = team2.get("raw_record") or {}

    def _ppg(record: Dict[str, Any], key: str) -> float:
        avg = record.get(f"avg{key.capitalize()}")
        try:
            if avg is not None:
                return float(avg)
        except (TypeError, ValueError):
            pass
        total = record.get(key)
        gp = record.get("gamesPlayed") or 0
        try:
            return float(total) / float(gp) if total is not None and gp else 0.0
        except (TypeError, ValueError):
            return 0.0

    atk1 = _ppg(r1, "pointsFor")
    def1 = _ppg(r1, "pointsAgainst")
    atk2 = _ppg(r2, "pointsFor")
    def2 = _ppg(r2, "pointsAgainst")

    exp_t1 = max(0.0, (atk1 + def2) / 2)
    exp_t2 = max(0.0, (atk2 + def1) / 2)

    if sport == "soccer":
        s1 = max(0, round(exp_t1))
        s2 = max(0, round(exp_t2))
        score_pred = f"{team1['name']} {s1}-{s2} {team2['name']}"
    else:
        s1 = max(0, int(round(exp_t1)))
        s2 = max(0, int(round(exp_t2)))
        score_pred = f"{team1['name']} {s1}-{s2} {team2['name']}"

    if favorite == "Toss-up":
        narrative = (
            f"A genuine coin-flip. Both {team1['name']} and {team2['name']} have the "
            f"profile to win — the result will hinge on execution and key-moment performance."
        )
    else:
        t1_str = team1.get("strengths") or []
        t2_str = team2.get("strengths") or []
        narrative = (
            f"{favorite} enters as the favorite with {confidence.lower()} confidence, "
            f"based on season-long production and recent form. {underdog} can swing the "
            f"contest by leaning on their strengths "
            f"({', '.join(_derive_strengths(team1)[:2]) if underdog == team1['name'] else ', '.join(_derive_strengths(team2)[:2])})."
        )
        # suppress unused vars warning (kept for potential future use)
        _ = t1_str, t2_str

    return {
        "favorite": favorite,
        "confidence": confidence,
        "score_prediction": score_pred,
        "narrative": narrative,
    }


def analyze_matchup(team1: Dict[str, Any], team2: Dict[str, Any]) -> Dict[str, Any]:
    stats1 = team1["stats"]
    stats2 = team2["stats"]
    overall1 = _calculate_overall_rating(stats1)
    overall2 = _calculate_overall_rating(stats2)

    stat_comparison: Dict[str, Any] = {}
    t1_adv: List[Tuple[str, int]] = []
    t2_adv: List[Tuple[str, int]] = []
    for key in stats1:
        if key not in stats2:
            continue
        diff = stats1[key] - stats2[key]
        stat_comparison[key] = {
            "team1_value": stats1[key],
            "team2_value": stats2[key],
            "difference": diff,
            "advantage": team1["name"] if diff > 0 else team2["name"] if diff < 0 else "Even",
            "label": STAT_LABELS.get(key, key),
        }
        if diff >= 5:
            t1_adv.append((key, diff))
        elif diff <= -5:
            t2_adv.append((key, abs(diff)))

    total_diff = overall1 - overall2
    base_prob = 50 + total_diff * 2.0
    team1_win_prob = max(15.0, min(85.0, base_prob))
    team2_win_prob = 100.0 - team1_win_prob

    key_battles = _identify_key_battles(team1, team2)
    tactical_analysis = _generate_matchup_analysis(team1, team2, t1_adv, t2_adv)
    prediction = _generate_prediction(team1, team2, team1_win_prob)

    def _matchup_team(team: Dict[str, Any], overall: float) -> Dict[str, Any]:
        return {
            "id": team["id"],
            "name": team["name"],
            "overall_rating": overall,
            "league": team.get("league", ""),
            "country": team.get("country", ""),
            "logo_color": team.get("logo_color", "#64748b"),
            "logo_url": team.get("logo_url"),
            "stats": team["stats"],
            "strengths": _derive_strengths(team),
            "weaknesses": _derive_weaknesses(team),
            "season_record": team.get("season_record", {}),
            "record_summary": _record_string(team),
            "recent_form": team.get("recent_form", []),
        }

    return {
        "team1": _matchup_team(team1, overall1),
        "team2": _matchup_team(team2, overall2),
        "stat_comparison": stat_comparison,
        "stat_labels": STAT_LABELS,
        "team1_advantages": [
            {"stat": a[0], "margin": a[1], "label": STAT_LABELS.get(a[0], a[0])}
            for a in sorted(t1_adv, key=lambda x: x[1], reverse=True)
        ],
        "team2_advantages": [
            {"stat": a[0], "margin": a[1], "label": STAT_LABELS.get(a[0], a[0])}
            for a in sorted(t2_adv, key=lambda x: x[1], reverse=True)
        ],
        "win_probability": {
            "team1": round(team1_win_prob, 1),
            "team2": round(team2_win_prob, 1),
        },
        "key_battles": key_battles,
        "tactical_analysis": tactical_analysis,
        "prediction": prediction,
    }
