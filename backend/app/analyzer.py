"""
AI Tactical Analyzer Engine - Provides deep tactical analysis for sports teams.
Uses statistical modeling, pattern recognition, and tactical frameworks.
"""

import random
from typing import Dict, Any, List, Tuple


def _calculate_overall_rating(stats: Dict[str, int]) -> float:
    """Calculate weighted overall rating from stats."""
    values = list(stats.values())
    return round(sum(values) / len(values), 1)


def _get_stat_tier(value: int) -> str:
    """Classify a stat value into a tier."""
    if value >= 93:
        return "Elite"
    elif value >= 88:
        return "Excellent"
    elif value >= 83:
        return "Very Good"
    elif value >= 78:
        return "Good"
    elif value >= 73:
        return "Average"
    else:
        return "Below Average"


def _identify_tactical_identity(team: Dict[str, Any]) -> str:
    """Generate a tactical identity description."""
    stats = team["stats"]
    sport = team["sport"]

    if sport == "soccer":
        if stats.get("possession", 0) >= 90 and stats.get("pressing", 0) >= 90:
            return "Dominant Possession Controller - This team dictates the tempo of every match, suffocating opponents with relentless ball retention and coordinated pressing."
        elif stats.get("pressing", 0) >= 93:
            return "High-Intensity Presser - An aggressive team that wins the ball high and transitions rapidly. Opponents are given no time on the ball."
        elif stats.get("pace", 0) >= 90 and stats.get("finishing", 0) >= 90:
            return "Lethal Counter-Attacker - Devastating on the break with elite pace and clinical finishing. Thrives against teams that overcommit."
        elif stats.get("set_pieces", 0) >= 90:
            return "Set-Piece Specialist - A team that has mastered dead-ball situations, turning every corner and free-kick into a genuine scoring opportunity."
        else:
            return "Balanced Tactical Operator - A well-rounded team capable of adapting to different game situations."

    elif sport == "basketball":
        if stats.get("three_point", 0) >= 93:
            return "3-Point Artillery - This team lives and dies by the three. When the shots fall, they're virtually unstoppable from beyond the arc."
        elif stats.get("post_play", 0) >= 93:
            return "Interior Dominator - Built around elite post play, this team punishes smaller lineups and controls the paint on both ends."
        elif stats.get("fast_break", 0) >= 90:
            return "Transition Tornado - Gets out and runs at every opportunity. Their pace and athleticism overwhelm slower teams."
        elif stats.get("defense", 0) >= 90:
            return "Defensive Fortress - Defense wins championships, and this team embodies that philosophy with elite versatility on that end."
        else:
            return "Balanced Contender - A well-constructed team with no glaring weaknesses."

    elif sport == "american_football":
        if stats.get("rushing_offense", 0) >= 93:
            return "Ground-and-Pound Machine - This team establishes the run and imposes its physical will. When the rushing attack gets rolling, they're nearly impossible to stop."
        elif stats.get("passing_offense", 0) >= 93:
            return "Air Raid Operator - A pass-first offense that stretches defenses horizontally and vertically. The quarterback is the engine of everything."
        elif stats.get("coaching", 0) >= 95:
            return "Coaching Masterclass - Schematic superiority defines this team. They consistently outprepare and outadjust opponents."
        else:
            return "Complete Football Team - Balanced on both sides of the ball with a clear identity."

    return "Tactical Unit"


def _generate_key_insights(team: Dict[str, Any]) -> List[str]:
    """Generate specific tactical insights."""
    stats = team["stats"]
    sport = team["sport"]
    insights = []

    if sport == "soccer":
        if stats.get("possession", 0) >= 90:
            insights.append(f"With a possession rating of {stats['possession']}/100, {team['name']} controls the ball for extended periods, forcing opponents into reactive defending. This creates fatigue in the opposition and opens gaps in the final third.")
        if stats.get("pressing", 0) >= 90:
            insights.append(f"Their pressing intensity ({stats['pressing']}/100) means opponents average significantly fewer passes before losing possession. The high press recovers the ball in dangerous areas.")
        if stats.get("finishing", 0) >= 88:
            insights.append(f"Clinical finishing ({stats['finishing']}/100) means they convert a high percentage of chances. Low xG overperformance suggests elite individual quality in the final third.")
        if stats.get("defense", 0) >= 87:
            insights.append(f"Defensively solid ({stats['defense']}/100) with a well-organized backline. They concede few high-quality chances per game.")
        if stats.get("set_pieces", 0) >= 85:
            insights.append(f"Set pieces ({stats['set_pieces']}/100) are a genuine weapon. They score from dead-ball situations at a rate well above league average.")
        if stats.get("pace", 0) >= 88:
            insights.append(f"Exceptional pace ({stats['pace']}/100) in transition allows them to exploit high defensive lines and capitalize on turnover situations.")

    elif sport == "basketball":
        if stats.get("three_point", 0) >= 90:
            insights.append(f"Elite 3-point shooting ({stats['three_point']}/100) stretches defenses to their limit. They generate the most wide-open 3s in the league through ball movement.")
        if stats.get("playmaking", 0) >= 90:
            insights.append(f"Outstanding playmaking ({stats['playmaking']}/100) means they rarely waste possessions. Ball movement creates high-quality looks consistently.")
        if stats.get("defense", 0) >= 90:
            insights.append(f"Defensive rating ({stats['defense']}/100) puts them among the league's best. Their switching scheme eliminates easy baskets.")
        if stats.get("athleticism", 0) >= 90:
            insights.append(f"Superior athleticism ({stats['athleticism']}/100) allows them to play a disruptive, high-energy style that wears down opponents.")
        if stats.get("post_play", 0) >= 90:
            insights.append(f"Dominant post play ({stats['post_play']}/100) creates mismatches that opponents cannot solve. The paint is their domain.")
        if stats.get("clutch", 0) >= 88:
            insights.append(f"Clutch performance ({stats['clutch']}/100) indicates this team elevates in high-pressure moments. They have the closer mentality needed for playoff success.")

    elif sport == "american_football":
        if stats.get("passing_offense", 0) >= 90:
            insights.append(f"Elite passing offense ({stats['passing_offense']}/100) creates explosive plays. The quarterback can dissect any coverage scheme.")
        if stats.get("rushing_offense", 0) >= 90:
            insights.append(f"Dominant rushing attack ({stats['rushing_offense']}/100) controls time of possession and wears down defenses. Play-action becomes devastating.")
        if stats.get("coaching", 0) >= 90:
            insights.append(f"Superior coaching ({stats['coaching']}/100) means they consistently make better halftime adjustments and game plans than opponents.")
        if stats.get("clutch", 0) >= 90:
            insights.append(f"Exceptional clutch performance ({stats['clutch']}/100) - this team has ice in their veins in pressure situations. Fourth-quarter comeback ability is elite.")
        if stats.get("red_zone", 0) >= 88:
            insights.append(f"Red zone efficiency ({stats['red_zone']}/100) means they convert scoring opportunities into touchdowns rather than settling for field goals.")

    return insights


def analyze_team(team: Dict[str, Any]) -> Dict[str, Any]:
    """Generate comprehensive tactical analysis for a single team."""
    stats = team["stats"]
    overall = _calculate_overall_rating(stats)
    identity = _identify_tactical_identity(team)
    insights = _generate_key_insights(team)

    sorted_stats = sorted(stats.items(), key=lambda x: x[1], reverse=True)
    top_attributes = [(k, v, _get_stat_tier(v)) for k, v, in sorted_stats[:3]]
    weak_attributes = [(k, v, _get_stat_tier(v)) for k, v in sorted_stats[-3:]]

    tactical_recommendations = _generate_recommendations(team)

    return {
        "team_id": team["id"],
        "team_name": team["name"],
        "sport": team["sport"],
        "overall_rating": overall,
        "tactical_identity": identity,
        "formation": team["formation"],
        "style": team["style"],
        "stats": stats,
        "top_attributes": [{"name": a[0], "value": a[1], "tier": a[2]} for a in top_attributes],
        "weak_attributes": [{"name": a[0], "value": a[1], "tier": a[2]} for a in weak_attributes],
        "key_insights": insights,
        "strengths": team["strengths"],
        "weaknesses": team["weaknesses"],
        "key_players": team["key_players"],
        "tactical_notes": team["tactical_notes"],
        "tactical_recommendations": tactical_recommendations,
        "season_record": team.get("season_record", {}),
        "recent_form": team["recent_form"],
    }


def _generate_recommendations(team: Dict[str, Any]) -> List[str]:
    """Generate tactical recommendations for a team."""
    recs = []
    stats = team["stats"]
    sport = team["sport"]

    if sport == "soccer":
        if stats.get("set_pieces", 0) < 80:
            recs.append("Invest in set-piece coaching. Dead-ball situations account for ~30% of goals in top leagues, and this area is underperforming.")
        if stats.get("pace", 0) < 82:
            recs.append("Consider adding pace in wide areas or up front to provide a counter-attacking outlet and stretch opposition defenses.")
        if stats.get("pressing", 0) < 85:
            recs.append("Improving pressing coordination could recover the ball higher up the pitch, creating more scoring opportunities from turnovers.")
        if stats.get("crossing", 0) < 80:
            recs.append("Wide delivery quality could be improved. Better crossing would unlock more chances from open play.")

    elif sport == "basketball":
        if stats.get("three_point", 0) < 83:
            recs.append("Improving 3-point shooting volume and efficiency would space the floor better and open up driving lanes.")
        if stats.get("fast_break", 0) < 82:
            recs.append("Pushing pace in transition could generate easier scoring opportunities before defenses set up.")
        if stats.get("depth", 0) < 82:
            recs.append("Roster depth is a concern for playoff rotations. Adding reliable bench contributors would help manage minutes.")

    elif sport == "american_football":
        if stats.get("rushing_offense", 0) < 80:
            recs.append("Establishing a more consistent ground game would take pressure off the quarterback and control time of possession.")
        if stats.get("pass_defense", 0) < 83:
            recs.append("Secondary coverage needs improvement. Elite passing teams will exploit this weakness in critical matchups.")
        if stats.get("discipline", 0) < 82:
            recs.append("Penalty discipline needs attention. Self-inflicted mistakes extend drives and kill momentum.")

    if not recs:
        recs.append(f"This is an elite, well-rounded squad. Focus on maintaining consistency and managing workload for key players across the season.")

    return recs


def analyze_matchup(team1: Dict[str, Any], team2: Dict[str, Any]) -> Dict[str, Any]:
    """Generate comprehensive head-to-head matchup analysis."""
    stats1 = team1["stats"]
    stats2 = team2["stats"]
    overall1 = _calculate_overall_rating(stats1)
    overall2 = _calculate_overall_rating(stats2)

    # Calculate advantages
    stat_comparison = {}
    team1_advantages = []
    team2_advantages = []

    for key in stats1:
        if key in stats2:
            diff = stats1[key] - stats2[key]
            stat_comparison[key] = {
                "team1_value": stats1[key],
                "team2_value": stats2[key],
                "difference": diff,
                "advantage": team1["name"] if diff > 0 else team2["name"] if diff < 0 else "Even",
            }
            if diff >= 3:
                team1_advantages.append((key, diff))
            elif diff <= -3:
                team2_advantages.append((key, abs(diff)))

    # Win probability
    total_diff = overall1 - overall2
    base_prob = 50 + (total_diff * 2.5)
    team1_win_prob = max(15, min(85, base_prob))
    team2_win_prob = 100 - team1_win_prob

    # Key battles
    key_battles = _identify_key_battles(team1, team2)

    # Tactical analysis
    tactical_analysis = _generate_matchup_analysis(team1, team2, team1_advantages, team2_advantages)

    # Prediction narrative
    prediction = _generate_prediction(team1, team2, team1_win_prob)

    return {
        "team1": {
            "id": team1["id"],
            "name": team1["name"],
            "overall_rating": overall1,
            "formation": team1["formation"],
            "style": team1["style"],
            "stats": stats1,
            "strengths": team1["strengths"],
            "weaknesses": team1["weaknesses"],
            "key_players": team1["key_players"],
        },
        "team2": {
            "id": team2["id"],
            "name": team2["name"],
            "overall_rating": overall2,
            "formation": team2["formation"],
            "style": team2["style"],
            "stats": stats2,
            "strengths": team2["strengths"],
            "weaknesses": team2["weaknesses"],
            "key_players": team2["key_players"],
        },
        "stat_comparison": stat_comparison,
        "team1_advantages": [{"stat": a[0], "margin": a[1]} for a in sorted(team1_advantages, key=lambda x: x[1], reverse=True)],
        "team2_advantages": [{"stat": a[0], "margin": a[1]} for a in sorted(team2_advantages, key=lambda x: x[1], reverse=True)],
        "win_probability": {
            "team1": round(team1_win_prob, 1),
            "team2": round(team2_win_prob, 1),
        },
        "key_battles": key_battles,
        "tactical_analysis": tactical_analysis,
        "prediction": prediction,
    }


def _identify_key_battles(team1: Dict[str, Any], team2: Dict[str, Any]) -> List[Dict[str, str]]:
    """Identify key tactical battles in the matchup."""
    battles = []
    sport = team1["sport"]

    if sport == "soccer":
        battles.append({
            "battle": "Midfield Control",
            "description": f"{team1['name']}'s midfield (rated {team1['stats'].get('midfield', 'N/A')}) vs {team2['name']}'s midfield (rated {team2['stats'].get('midfield', 'N/A')}). Whoever controls the middle of the park will dictate the tempo and create chances.",
        })
        battles.append({
            "battle": "Press vs Possession",
            "description": f"{team1['name']}'s pressing ({team1['stats'].get('pressing', 'N/A')}) against {team2['name']}'s ball retention ({team2['stats'].get('possession', 'N/A')}). Can the press disrupt the build-up, or will composure on the ball prevail?",
        })
        battles.append({
            "battle": "Attack vs Defense",
            "description": f"{team1['name']}'s attack ({team1['stats'].get('attack', 'N/A')}) meets {team2['name']}'s defense ({team2['stats'].get('defense', 'N/A')}). The team that wins this battle will likely win the match.",
        })

    elif sport == "basketball":
        battles.append({
            "battle": "Perimeter vs Interior",
            "description": f"{team1['name']}'s 3PT shooting ({team1['stats'].get('three_point', 'N/A')}) vs {team2['name']}'s post play ({team2['stats'].get('post_play', 'N/A')}). A classic clash of offensive philosophies.",
        })
        battles.append({
            "battle": "Star Power Duel",
            "description": f"{team1['key_players'][0]} vs {team2['key_players'][0]}. The marquee individual matchup that could swing the series.",
        })
        battles.append({
            "battle": "Pace Control",
            "description": f"{team1['name']}'s fast break ({team1['stats'].get('fast_break', 'N/A')}) vs {team2['name']}'s half-court game. Which team imposes its preferred tempo?",
        })

    elif sport == "american_football":
        battles.append({
            "battle": "Quarterback Duel",
            "description": f"{team1['key_players'][0]} vs {team2['key_players'][0]}. The quarterback matchup often determines the outcome in the NFL.",
        })
        battles.append({
            "battle": "Run Game vs Run Defense",
            "description": f"{team1['name']}'s rushing offense ({team1['stats'].get('rushing_offense', 'N/A')}) against {team2['name']}'s rush defense ({team2['stats'].get('rush_defense', 'N/A')}). Establishing the run changes everything.",
        })
        battles.append({
            "battle": "Coaching Chess Match",
            "description": f"Coaching ratings: {team1['name']} ({team1['stats'].get('coaching', 'N/A')}) vs {team2['name']} ({team2['stats'].get('coaching', 'N/A')}). In-game adjustments and game plans will be crucial.",
        })

    return battles


def _generate_matchup_analysis(
    team1: Dict[str, Any],
    team2: Dict[str, Any],
    t1_advantages: List[Tuple[str, int]],
    t2_advantages: List[Tuple[str, int]],
) -> List[str]:
    """Generate narrative matchup analysis."""
    analysis = []

    if len(t1_advantages) > len(t2_advantages):
        analysis.append(
            f"{team1['name']} holds the statistical edge in {len(t1_advantages)} categories compared to {team2['name']}'s {len(t2_advantages)}. "
            f"This suggests {team1['name']} has more avenues to victory."
        )
    elif len(t2_advantages) > len(t1_advantages):
        analysis.append(
            f"{team2['name']} holds the statistical edge in {len(t2_advantages)} categories compared to {team1['name']}'s {len(t1_advantages)}. "
            f"This suggests {team2['name']} enters with more advantages."
        )
    else:
        analysis.append(
            f"This is an incredibly evenly matched contest. Both teams hold advantages in {len(t1_advantages)} statistical categories each. Expect a tightly contested affair."
        )

    # Style clash analysis
    analysis.append(
        f"Style clash: {team1['name']} ({team1['style']}) vs {team2['name']} ({team2['style']}). "
        f"This creates a fascinating tactical battle of contrasting philosophies."
    )

    # Weakness exploitation
    for weakness in team2["weaknesses"][:2]:
        for strength in team1["strengths"][:2]:
            analysis.append(
                f"{team1['name']} can exploit {team2['name']}'s weakness in '{weakness}' using their strength in '{strength}'."
            )
            break

    for weakness in team1["weaknesses"][:2]:
        for strength in team2["strengths"][:2]:
            analysis.append(
                f"Conversely, {team2['name']} can target {team1['name']}'s vulnerability: '{weakness}' through their '{strength}'."
            )
            break

    return analysis


def _generate_prediction(team1: Dict[str, Any], team2: Dict[str, Any], t1_prob: float) -> Dict[str, Any]:
    """Generate match prediction with narrative."""
    sport = team1["sport"]

    if t1_prob > 60:
        favorite = team1["name"]
        underdog = team2["name"]
        confidence = "High"
    elif t1_prob > 52:
        favorite = team1["name"]
        underdog = team2["name"]
        confidence = "Moderate"
    elif t1_prob > 48:
        favorite = "Toss-up"
        underdog = ""
        confidence = "Low"
    elif t1_prob > 40:
        favorite = team2["name"]
        underdog = team1["name"]
        confidence = "Moderate"
    else:
        favorite = team2["name"]
        underdog = team1["name"]
        confidence = "High"

    if sport == "soccer":
        if t1_prob > 55:
            score_pred = f"{team1['name']} 2-1 {team2['name']}"
        elif t1_prob < 45:
            score_pred = f"{team1['name']} 0-2 {team2['name']}"
        else:
            score_pred = f"{team1['name']} 1-1 {team2['name']}"
    elif sport == "basketball":
        if t1_prob > 55:
            score_pred = f"{team1['name']} 112-104 {team2['name']}"
        elif t1_prob < 45:
            score_pred = f"{team1['name']} 101-115 {team2['name']}"
        else:
            score_pred = f"{team1['name']} 108-106 {team2['name']}"
    else:
        if t1_prob > 55:
            score_pred = f"{team1['name']} 27-20 {team2['name']}"
        elif t1_prob < 45:
            score_pred = f"{team1['name']} 17-24 {team2['name']}"
        else:
            score_pred = f"{team1['name']} 24-21 {team2['name']}"

    narrative = ""
    if favorite == "Toss-up":
        narrative = (
            f"This is a genuine coin-flip matchup. Both {team1['name']} and {team2['name']} have the quality to win. "
            f"The result will likely come down to which team executes their game plan better on the day and which key players step up in crucial moments."
        )
    else:
        narrative = (
            f"{favorite} enters as the favorite with a {confidence.lower()} confidence edge. "
            f"However, {underdog} has the tools to cause an upset, particularly through their strengths in "
            f"{', '.join(team1['strengths'][:2]) if underdog == team1['name'] else ', '.join(team2['strengths'][:2])}. "
            f"The key to the game will be whether {favorite} can impose their preferred style of play."
        )

    return {
        "favorite": favorite,
        "confidence": confidence,
        "score_prediction": score_pred,
        "narrative": narrative,
    }
