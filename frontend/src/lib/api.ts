const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export interface Sport {
  id: string;
  name: string;
  icon: string;
}

export interface TeamSummary {
  id: string;
  name: string;
  sport: string;
  league: string;
  country: string;
  logo_color: string;
  formation: string;
  style: string;
  recent_form: string[];
}

export interface TeamDetails extends TeamSummary {
  stats: Record<string, number>;
  key_players: string[];
  tactical_notes: string;
  strengths: string[];
  weaknesses: string[];
  season_record: Record<string, number>;
}

export interface StatAttribute {
  name: string;
  value: number;
  tier: string;
}

export interface TeamAnalysis {
  team_id: string;
  team_name: string;
  sport: string;
  overall_rating: number;
  tactical_identity: string;
  formation: string;
  style: string;
  stats: Record<string, number>;
  top_attributes: StatAttribute[];
  weak_attributes: StatAttribute[];
  key_insights: string[];
  strengths: string[];
  weaknesses: string[];
  key_players: string[];
  tactical_notes: string;
  tactical_recommendations: string[];
  season_record: Record<string, number>;
  recent_form: string[];
}

export interface MatchupTeam {
  id: string;
  name: string;
  overall_rating: number;
  formation: string;
  style: string;
  stats: Record<string, number>;
  strengths: string[];
  weaknesses: string[];
  key_players: string[];
}

export interface StatComparison {
  team1_value: number;
  team2_value: number;
  difference: number;
  advantage: string;
}

export interface KeyBattle {
  battle: string;
  description: string;
}

export interface Prediction {
  favorite: string;
  confidence: string;
  score_prediction: string;
  narrative: string;
}

export interface MatchupAnalysis {
  team1: MatchupTeam;
  team2: MatchupTeam;
  stat_comparison: Record<string, StatComparison>;
  team1_advantages: { stat: string; margin: number }[];
  team2_advantages: { stat: string; margin: number }[];
  win_probability: { team1: number; team2: number };
  key_battles: KeyBattle[];
  tactical_analysis: string[];
  prediction: Prediction;
}

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${url}`, options);
  if (!res.ok) {
    throw new Error(`API error: ${res.status}`);
  }
  return res.json();
}

export async function getSports(): Promise<Sport[]> {
  const data = await fetchJson<{ sports: Sport[] }>("/api/sports");
  return data.sports;
}

export async function getTeams(sport?: string): Promise<TeamSummary[]> {
  const url = sport ? `/api/teams?sport=${sport}` : "/api/teams";
  const data = await fetchJson<{ teams: TeamSummary[]; count: number }>(url);
  return data.teams;
}

export async function getTeamDetails(teamId: string): Promise<TeamDetails> {
  const data = await fetchJson<{ team: TeamDetails }>(`/api/teams/${teamId}`);
  return data.team;
}

export async function analyzeTeam(teamId: string): Promise<TeamAnalysis> {
  const data = await fetchJson<{ analysis: TeamAnalysis }>("/api/analyze/team", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ team_id: teamId }),
  });
  return data.analysis;
}

export async function analyzeMatchup(
  team1Id: string,
  team2Id: string
): Promise<MatchupAnalysis> {
  const data = await fetchJson<{ matchup: MatchupAnalysis }>(
    "/api/analyze/matchup",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ team1_id: team1Id, team2_id: team2Id }),
    }
  );
  return data.matchup;
}
