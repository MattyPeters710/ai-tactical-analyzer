import { useState, useEffect, useCallback } from "react";
import {
  getSports,
  getTeams,
  analyzeTeam,
  analyzeMatchup,
} from "./lib/api";
import type {
  Sport,
  TeamSummary,
  TeamAnalysis,
  MatchupAnalysis,
} from "./lib/api";
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";
import {
  Trophy,
  Swords,
  Target,
  Shield,
  Zap,
  Users,
  ChevronRight,
  ArrowLeft,
  Loader2,
  Activity,
  Star,
  AlertTriangle,
  Lightbulb,
  BarChart3,
} from "lucide-react";

type Page = "home" | "teams" | "analysis" | "matchup" | "matchup-result";

function App() {
  const [page, setPage] = useState<Page>("home");
  const [sports, setSports] = useState<Sport[]>([]);
  const [selectedSport, setSelectedSport] = useState<string>("");
  const [teams, setTeams] = useState<TeamSummary[]>([]);
  const [loading, setLoading] = useState(false);
  const [teamAnalysis, setTeamAnalysis] = useState<TeamAnalysis | null>(null);
  const [matchupResult, setMatchupResult] = useState<MatchupAnalysis | null>(null);
  const [matchupTeam1, setMatchupTeam1] = useState<string>("");
  const [matchupTeam2, setMatchupTeam2] = useState<string>("");

  useEffect(() => {
    getSports().then(setSports);
  }, []);

  const loadTeams = useCallback(async (sport: string) => {
    setSelectedSport(sport);
    setLoading(true);
    const t = await getTeams(sport);
    setTeams(t);
    setLoading(false);
  }, []);

  const handleAnalyzeTeam = useCallback(async (teamId: string) => {
    setLoading(true);
    const a = await analyzeTeam(teamId);
    setTeamAnalysis(a);
    setPage("analysis");
    setLoading(false);
  }, []);

  const handleMatchup = useCallback(async () => {
    if (!matchupTeam1 || !matchupTeam2 || matchupTeam1 === matchupTeam2) return;
    setLoading(true);
    const m = await analyzeMatchup(matchupTeam1, matchupTeam2);
    setMatchupResult(m);
    setPage("matchup-result");
    setLoading(false);
  }, [matchupTeam1, matchupTeam2]);

  const goHome = useCallback(() => {
    setPage("home");
    setTeamAnalysis(null);
    setMatchupResult(null);
    setSelectedSport("");
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-emerald-400 animate-spin mx-auto mb-4" />
          <p className="text-gray-400 text-lg">Analyzing tactical data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950 text-white">
      {/* Header */}
      <header className="border-b border-gray-800 bg-gray-950/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <button onClick={goHome} className="flex items-center gap-3 hover:opacity-80 transition-opacity">
            <div className="w-10 h-10 bg-emerald-500 rounded-lg flex items-center justify-center">
              <Target className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">
                AI Tactical Analyzer
              </h1>
              <p className="text-xs text-gray-500">Precision Sports Intelligence</p>
            </div>
          </button>
          <nav className="flex gap-2">
            <button
              onClick={goHome}
              className="px-4 py-2 text-sm rounded-lg hover:bg-gray-800 transition-colors text-gray-300"
            >
              Home
            </button>
            {selectedSport && (
              <button
                onClick={() => { setPage("matchup"); setMatchupTeam1(""); setMatchupTeam2(""); }}
                className="px-4 py-2 text-sm rounded-lg bg-emerald-600 hover:bg-emerald-700 transition-colors flex items-center gap-2"
              >
                <Swords className="w-4 h-4" /> Matchup
              </button>
            )}
          </nav>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {page === "home" && <HomePage sports={sports} onSelectSport={(s) => { loadTeams(s); setPage("teams"); }} />}
        {page === "teams" && (
          <TeamsPage
            teams={teams}
            sport={selectedSport}
            onAnalyze={handleAnalyzeTeam}
            onBack={goHome}
            onMatchup={() => { setPage("matchup"); setMatchupTeam1(""); setMatchupTeam2(""); }}
          />
        )}
        {page === "analysis" && teamAnalysis && (
          <AnalysisPage analysis={teamAnalysis} onBack={() => setPage("teams")} />
        )}
        {page === "matchup" && (
          <MatchupPage
            teams={teams}
            team1={matchupTeam1}
            team2={matchupTeam2}
            onTeam1Change={setMatchupTeam1}
            onTeam2Change={setMatchupTeam2}
            onAnalyze={handleMatchup}
            onBack={() => setPage("teams")}
          />
        )}
        {page === "matchup-result" && matchupResult && (
          <MatchupResultPage matchup={matchupResult} onBack={() => setPage("matchup")} />
        )}
      </main>

      <footer className="border-t border-gray-800 py-6 mt-12">
        <p className="text-center text-gray-600 text-sm">
          AI Tactical Analyzer - Precision Sports Intelligence Engine
        </p>
      </footer>
    </div>
  );
}

/* ============ HOME PAGE ============ */
function HomePage({ sports, onSelectSport }: { sports: Sport[]; onSelectSport: (s: string) => void }) {
  const sportIcons: Record<string, React.ReactNode> = {
    soccer: <Trophy className="w-8 h-8" />,
    basketball: <Activity className="w-8 h-8" />,
    american_football: <Shield className="w-8 h-8" />,
  };

  return (
    <div className="space-y-12">
      <div className="text-center py-16">
        <div className="w-20 h-20 bg-gradient-to-br from-emerald-500 to-cyan-500 rounded-2xl flex items-center justify-center mx-auto mb-6">
          <Target className="w-10 h-10 text-white" />
        </div>
        <h2 className="text-5xl font-bold mb-4 bg-gradient-to-r from-emerald-400 via-cyan-400 to-blue-400 bg-clip-text text-transparent">
          AI Tactical Analyzer
        </h2>
        <p className="text-gray-400 text-lg max-w-2xl mx-auto">
          Deep tactical analysis powered by advanced statistical modeling. Analyze team strengths,
          compare head-to-head matchups, and get precision insights for Soccer, Basketball, and American Football.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {sports.map((sport) => (
          <button
            key={sport.id}
            onClick={() => onSelectSport(sport.id)}
            className="group bg-gray-900/50 border border-gray-800 rounded-2xl p-8 hover:border-emerald-500/50 hover:bg-gray-900/80 transition-all duration-300 text-left"
          >
            <div className="w-16 h-16 bg-gradient-to-br from-emerald-500/20 to-cyan-500/20 rounded-xl flex items-center justify-center mb-4 text-emerald-400 group-hover:scale-110 transition-transform">
              {sportIcons[sport.id] || <Trophy className="w-8 h-8" />}
            </div>
            <h3 className="text-xl font-semibold mb-2">{sport.name}</h3>
            <p className="text-gray-500 text-sm">
              Analyze teams, compare tactics, and get matchup predictions
            </p>
            <div className="flex items-center gap-1 mt-4 text-emerald-400 text-sm group-hover:gap-2 transition-all">
              Explore <ChevronRight className="w-4 h-4" />
            </div>
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
        <div className="bg-gray-900/30 border border-gray-800 rounded-xl p-6 text-center">
          <BarChart3 className="w-8 h-8 text-emerald-400 mx-auto mb-3" />
          <h4 className="font-semibold mb-1">Deep Statistics</h4>
          <p className="text-gray-500 text-sm">10+ tactical attributes per team with tier classifications</p>
        </div>
        <div className="bg-gray-900/30 border border-gray-800 rounded-xl p-6 text-center">
          <Swords className="w-8 h-8 text-cyan-400 mx-auto mb-3" />
          <h4 className="font-semibold mb-1">Matchup Analysis</h4>
          <p className="text-gray-500 text-sm">Head-to-head comparison with win probability and key battles</p>
        </div>
        <div className="bg-gray-900/30 border border-gray-800 rounded-xl p-6 text-center">
          <Lightbulb className="w-8 h-8 text-yellow-400 mx-auto mb-3" />
          <h4 className="font-semibold mb-1">AI Insights</h4>
          <p className="text-gray-500 text-sm">Tactical recommendations and predictive analysis</p>
        </div>
      </div>
    </div>
  );
}

/* ============ TEAMS PAGE ============ */
function TeamsPage({
  teams,
  sport,
  onAnalyze,
  onBack,
  onMatchup,
}: {
  teams: TeamSummary[];
  sport: string;
  onAnalyze: (id: string) => void;
  onBack: () => void;
  onMatchup: () => void;
}) {
  const sportName = sport === "soccer" ? "Soccer" : sport === "basketball" ? "Basketball" : "American Football";

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button onClick={onBack} className="p-2 hover:bg-gray-800 rounded-lg transition-colors">
            <ArrowLeft className="w-5 h-5" />
          </button>
          <h2 className="text-2xl font-bold">{sportName} Teams</h2>
          <span className="text-sm text-gray-500 bg-gray-800 px-3 py-1 rounded-full">{teams.length} teams</span>
        </div>
        <button
          onClick={onMatchup}
          className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 rounded-lg text-sm font-medium flex items-center gap-2 transition-colors"
        >
          <Swords className="w-4 h-4" /> Compare Matchup
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {teams.map((team) => (
          <div
            key={team.id}
            className="bg-gray-900/50 border border-gray-800 rounded-xl p-5 hover:border-gray-700 transition-all group"
          >
            <div className="flex items-start gap-4">
              {team.logo_url ? (
                <img
                  src={team.logo_url}
                  alt={team.name}
                  className="w-12 h-12 rounded-lg shrink-0 object-contain bg-white/5 p-1"
                />
              ) : (
                <div
                  className="w-12 h-12 rounded-lg flex items-center justify-center text-white font-bold text-lg shrink-0"
                  style={{ backgroundColor: team.logo_color + "33", borderColor: team.logo_color, borderWidth: 2 }}
                >
                  {team.name.charAt(0)}
                </div>
              )}
              <div className="flex-1 min-w-0">
                <h3 className="font-semibold text-lg truncate">{team.name}</h3>
                <p className="text-gray-500 text-sm truncate">
                  {team.league}{team.country ? ` \u00b7 ${team.country}` : ""}
                </p>
              </div>
            </div>
            <div className="mt-4 space-y-2">
              <div className="flex items-center gap-2 text-sm">
                <Users className="w-4 h-4 text-gray-500" />
                <span className="text-gray-400">Code:</span>
                <span className="text-emerald-400 font-mono">{team.abbreviation || team.short_name || "—"}</span>
              </div>
            </div>
            <button
              onClick={() => onAnalyze(team.id)}
              className="mt-4 w-full py-2 bg-gray-800 hover:bg-emerald-600 rounded-lg text-sm font-medium transition-colors flex items-center justify-center gap-2"
            >
              <Target className="w-4 h-4" /> Analyze
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ============ ANALYSIS PAGE ============ */
function AnalysisPage({ analysis, onBack }: { analysis: TeamAnalysis; onBack: () => void }) {
  const labelFor = (key: string): string =>
    analysis.stat_labels?.[key] ||
    key.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
  const radarData = Object.entries(analysis.stats).map(([key, value]) => ({
    stat: labelFor(key),
    value,
    fullMark: 100,
  }));

  return (
    <div className="space-y-8">
      <div className="flex items-center gap-3">
        <button onClick={onBack} className="p-2 hover:bg-gray-800 rounded-lg transition-colors">
          <ArrowLeft className="w-5 h-5" />
        </button>
        {analysis.logo_url && (
          <img
            src={analysis.logo_url}
            alt={analysis.team_name}
            className="w-14 h-14 rounded-lg object-contain bg-white/5 p-1"
          />
        )}
        <div>
          <h2 className="text-3xl font-bold">{analysis.team_name}</h2>
          <p className="text-gray-500">
            {analysis.league}{analysis.country ? ` \u00b7 ${analysis.country}` : ""}
            {analysis.record_summary ? ` \u00b7 Record ${analysis.record_summary}` : ""}
          </p>
          {analysis.standing_summary && (
            <p className="text-xs text-gray-600 mt-0.5">{analysis.standing_summary}</p>
          )}
        </div>
      </div>

      {/* Overall Rating & Identity */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-gradient-to-br from-emerald-500/10 to-cyan-500/10 border border-emerald-500/30 rounded-xl p-6 text-center">
          <p className="text-sm text-emerald-400 mb-1">Overall Rating</p>
          <p className="text-5xl font-bold text-emerald-400">{analysis.overall_rating}</p>
          <p className="text-xs text-gray-500 mt-1">out of 100</p>
        </div>
        <div className="md:col-span-2 bg-gray-900/50 border border-gray-800 rounded-xl p-6">
          <p className="text-sm text-cyan-400 mb-2 flex items-center gap-2">
            <Zap className="w-4 h-4" /> Tactical Identity
          </p>
          <p className="text-gray-300 leading-relaxed">{analysis.tactical_identity}</p>
        </div>
      </div>

      {/* Radar Chart */}
      <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <BarChart3 className="w-5 h-5 text-emerald-400" /> Tactical Radar
        </h3>
        <div className="h-96">
          <ResponsiveContainer width="100%" height="100%">
            <RadarChart data={radarData}>
              <PolarGrid stroke="#374151" />
              <PolarAngleAxis dataKey="stat" tick={{ fill: "#9CA3AF", fontSize: 12 }} />
              <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fill: "#6B7280", fontSize: 10 }} />
              <Radar name={analysis.team_name} dataKey="value" stroke="#10B981" fill="#10B981" fillOpacity={0.2} strokeWidth={2} />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Top & Weak Attributes */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Star className="w-5 h-5 text-emerald-400" /> Top Attributes
          </h3>
          <div className="space-y-3">
            {analysis.top_attributes.map((attr) => (
              <div key={attr.name} className="flex items-center justify-between">
                <div>
                  <span className="text-gray-300">{attr.label || labelFor(attr.name)}</span>
                  <span className="ml-2 text-xs px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400">
                    {attr.tier}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-24 h-2 bg-gray-800 rounded-full overflow-hidden">
                    <div className="h-full bg-emerald-500 rounded-full" style={{ width: `${attr.value}%` }} />
                  </div>
                  <span className="text-emerald-400 font-mono text-sm w-8">{attr.value}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
        <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-yellow-400" /> Areas to Improve
          </h3>
          <div className="space-y-3">
            {analysis.weak_attributes.map((attr) => (
              <div key={attr.name} className="flex items-center justify-between">
                <div>
                  <span className="text-gray-300">{attr.label || labelFor(attr.name)}</span>
                  <span className="ml-2 text-xs px-2 py-0.5 rounded-full bg-yellow-500/20 text-yellow-400">
                    {attr.tier}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-24 h-2 bg-gray-800 rounded-full overflow-hidden">
                    <div className="h-full bg-yellow-500 rounded-full" style={{ width: `${attr.value}%` }} />
                  </div>
                  <span className="text-yellow-400 font-mono text-sm w-8">{attr.value}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Key Insights */}
      <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Lightbulb className="w-5 h-5 text-cyan-400" /> AI Tactical Insights
        </h3>
        <div className="space-y-3">
          {analysis.key_insights.map((insight, i) => (
            <div key={i} className="flex gap-3 p-3 bg-gray-800/50 rounded-lg">
              <div className="w-6 h-6 bg-cyan-500/20 rounded-full flex items-center justify-center shrink-0 mt-0.5">
                <span className="text-cyan-400 text-xs font-bold">{i + 1}</span>
              </div>
              <p className="text-gray-300 text-sm leading-relaxed">{insight}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Strengths & Weaknesses */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Shield className="w-5 h-5 text-emerald-400" /> Strengths
          </h3>
          <ul className="space-y-2">
            {analysis.strengths.map((s, i) => (
              <li key={i} className="flex items-center gap-2 text-gray-300 text-sm">
                <div className="w-1.5 h-1.5 bg-emerald-400 rounded-full" />
                {s}
              </li>
            ))}
          </ul>
        </div>
        <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-red-400" /> Weaknesses
          </h3>
          <ul className="space-y-2">
            {analysis.weaknesses.map((w, i) => (
              <li key={i} className="flex items-center gap-2 text-gray-300 text-sm">
                <div className="w-1.5 h-1.5 bg-red-400 rounded-full" />
                {w}
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Season snapshot */}
      <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Activity className="w-5 h-5 text-emerald-400" /> Season Snapshot
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {Object.entries(analysis.season_record).map(([k, v]) => (
            <div key={k} className="p-3 bg-gray-800/50 rounded-lg">
              <p className="text-xs text-gray-500 capitalize">{k.replace(/_/g, " ")}</p>
              <p className="text-lg font-semibold text-gray-200">{v}</p>
            </div>
          ))}
        </div>
        <p className="mt-4 text-gray-500 text-xs italic">
          Performance data sourced live from {analysis.source}. Ratings are derived from this season\u2019s real results.
        </p>
      </div>

      {/* Tactical Recommendations */}
      <div className="bg-gradient-to-br from-emerald-500/5 to-cyan-500/5 border border-emerald-500/20 rounded-xl p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Lightbulb className="w-5 h-5 text-yellow-400" /> Tactical Recommendations
        </h3>
        <div className="space-y-2">
          {analysis.tactical_recommendations.map((rec, i) => (
            <div key={i} className="flex gap-3 p-3 bg-gray-900/50 rounded-lg">
              <ChevronRight className="w-4 h-4 text-yellow-400 shrink-0 mt-0.5" />
              <p className="text-gray-300 text-sm">{rec}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

/* ============ MATCHUP PAGE ============ */
function MatchupPage({
  teams,
  team1,
  team2,
  onTeam1Change,
  onTeam2Change,
  onAnalyze,
  onBack,
}: {
  teams: TeamSummary[];
  team1: string;
  team2: string;
  onTeam1Change: (id: string) => void;
  onTeam2Change: (id: string) => void;
  onAnalyze: () => void;
  onBack: () => void;
}) {
  return (
    <div className="space-y-8">
      <div className="flex items-center gap-3">
        <button onClick={onBack} className="p-2 hover:bg-gray-800 rounded-lg transition-colors">
          <ArrowLeft className="w-5 h-5" />
        </button>
        <h2 className="text-2xl font-bold">Head-to-Head Matchup</h2>
      </div>

      <div className="max-w-2xl mx-auto bg-gray-900/50 border border-gray-800 rounded-2xl p-8 space-y-6">
        <div className="text-center mb-4">
          <Swords className="w-12 h-12 text-emerald-400 mx-auto mb-2" />
          <p className="text-gray-400">Select two teams to compare their tactical profiles</p>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm text-gray-400 mb-2">Team 1</label>
            <select
              value={team1}
              onChange={(e) => onTeam1Change(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white focus:border-emerald-500 focus:outline-none transition-colors"
            >
              <option value="">Select a team...</option>
              {teams.map((t) => (
                <option key={t.id} value={t.id}>{t.name} ({t.league})</option>
              ))}
            </select>
          </div>

          <div className="flex justify-center">
            <div className="w-10 h-10 bg-emerald-500/20 rounded-full flex items-center justify-center">
              <span className="text-emerald-400 font-bold">VS</span>
            </div>
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-2">Team 2</label>
            <select
              value={team2}
              onChange={(e) => onTeam2Change(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white focus:border-emerald-500 focus:outline-none transition-colors"
            >
              <option value="">Select a team...</option>
              {teams.map((t) => (
                <option key={t.id} value={t.id}>{t.name} ({t.league})</option>
              ))}
            </select>
          </div>
        </div>

        <button
          onClick={onAnalyze}
          disabled={!team1 || !team2 || team1 === team2}
          className="w-full py-3 bg-emerald-600 hover:bg-emerald-700 disabled:bg-gray-700 disabled:text-gray-500 rounded-lg font-semibold text-lg transition-colors flex items-center justify-center gap-2"
        >
          <Swords className="w-5 h-5" /> Analyze Matchup
        </button>
      </div>
    </div>
  );
}

/* ============ MATCHUP RESULT PAGE ============ */
function MatchupResultPage({ matchup, onBack }: { matchup: MatchupAnalysis; onBack: () => void }) {
  const labelFor = (key: string): string =>
    matchup.stat_labels?.[key] ||
    key.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
  const comparisonData = Object.entries(matchup.stat_comparison).map(([key, comp]) => ({
    stat: comp.label || labelFor(key),
    [matchup.team1.name]: comp.team1_value,
    [matchup.team2.name]: comp.team2_value,
  }));

  const radarData = Object.entries(matchup.stat_comparison).map(([key, comp]) => ({
    stat: comp.label || labelFor(key),
    team1: comp.team1_value,
    team2: comp.team2_value,
    fullMark: 100,
  }));

  return (
    <div className="space-y-8">
      <div className="flex items-center gap-3">
        <button onClick={onBack} className="p-2 hover:bg-gray-800 rounded-lg transition-colors">
          <ArrowLeft className="w-5 h-5" />
        </button>
        <h2 className="text-2xl font-bold">Matchup Analysis</h2>
      </div>

      {/* Teams Header */}
      <div className="grid grid-cols-3 gap-4 items-center">
        <div className="text-center bg-gray-900/50 border border-gray-800 rounded-xl p-6">
          {matchup.team1.logo_url && (
            <img
              src={matchup.team1.logo_url}
              alt={matchup.team1.name}
              className="w-14 h-14 mx-auto mb-2 object-contain bg-white/5 p-1 rounded-lg"
            />
          )}
          <p className="text-2xl font-bold">{matchup.team1.name}</p>
          <p className="text-gray-500 text-sm">{matchup.team1.record_summary}</p>
          <p className="text-4xl font-bold text-emerald-400 mt-2">{matchup.team1.overall_rating}</p>
        </div>
        <div className="text-center">
          <div className="w-16 h-16 bg-gray-800 rounded-full flex items-center justify-center mx-auto mb-2">
            <Swords className="w-8 h-8 text-emerald-400" />
          </div>
          <p className="text-gray-500 text-sm">VS</p>
        </div>
        <div className="text-center bg-gray-900/50 border border-gray-800 rounded-xl p-6">
          {matchup.team2.logo_url && (
            <img
              src={matchup.team2.logo_url}
              alt={matchup.team2.name}
              className="w-14 h-14 mx-auto mb-2 object-contain bg-white/5 p-1 rounded-lg"
            />
          )}
          <p className="text-2xl font-bold">{matchup.team2.name}</p>
          <p className="text-gray-500 text-sm">{matchup.team2.record_summary}</p>
          <p className="text-4xl font-bold text-cyan-400 mt-2">{matchup.team2.overall_rating}</p>
        </div>
      </div>

      {/* Win Probability */}
      <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
        <h3 className="text-lg font-semibold mb-4 text-center">Win Probability</h3>
        <div className="flex items-center gap-2">
          <span className="text-emerald-400 font-bold w-16 text-right">{matchup.win_probability.team1}%</span>
          <div className="flex-1 h-8 bg-gray-800 rounded-full overflow-hidden flex">
            <div
              className="h-full bg-gradient-to-r from-emerald-600 to-emerald-500 flex items-center justify-end pr-2 transition-all duration-500"
              style={{ width: `${matchup.win_probability.team1}%` }}
            >
              {matchup.win_probability.team1 > 20 && (
                <span className="text-xs font-bold text-white">{matchup.team1.name}</span>
              )}
            </div>
            <div
              className="h-full bg-gradient-to-r from-cyan-500 to-cyan-600 flex items-center pl-2 transition-all duration-500"
              style={{ width: `${matchup.win_probability.team2}%` }}
            >
              {matchup.win_probability.team2 > 20 && (
                <span className="text-xs font-bold text-white">{matchup.team2.name}</span>
              )}
            </div>
          </div>
          <span className="text-cyan-400 font-bold w-16">{matchup.win_probability.team2}%</span>
        </div>
      </div>

      {/* Radar Comparison */}
      <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <BarChart3 className="w-5 h-5 text-emerald-400" /> Tactical Radar Comparison
        </h3>
        <div className="h-96">
          <ResponsiveContainer width="100%" height="100%">
            <RadarChart data={radarData}>
              <PolarGrid stroke="#374151" />
              <PolarAngleAxis dataKey="stat" tick={{ fill: "#9CA3AF", fontSize: 11 }} />
              <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fill: "#6B7280", fontSize: 10 }} />
              <Radar name={matchup.team1.name} dataKey="team1" stroke="#10B981" fill="#10B981" fillOpacity={0.15} strokeWidth={2} />
              <Radar name={matchup.team2.name} dataKey="team2" stroke="#06B6D4" fill="#06B6D4" fillOpacity={0.15} strokeWidth={2} />
              <Legend />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Bar Chart Comparison */}
      <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
        <h3 className="text-lg font-semibold mb-4">Stat-by-Stat Comparison</h3>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={comparisonData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis type="number" domain={[60, 100]} tick={{ fill: "#9CA3AF", fontSize: 11 }} />
              <YAxis dataKey="stat" type="category" width={120} tick={{ fill: "#9CA3AF", fontSize: 11 }} />
              <Tooltip
                contentStyle={{ backgroundColor: "#1F2937", border: "1px solid #374151", borderRadius: "8px" }}
                labelStyle={{ color: "#F3F4F6" }}
              />
              <Legend />
              <Bar dataKey={matchup.team1.name} fill="#10B981" radius={[0, 4, 4, 0]} />
              <Bar dataKey={matchup.team2.name} fill="#06B6D4" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Key Advantages */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-gray-900/50 border border-emerald-500/30 rounded-xl p-6">
          <h3 className="text-lg font-semibold mb-4 text-emerald-400">{matchup.team1.name} Advantages</h3>
          {matchup.team1_advantages.length > 0 ? (
            <div className="space-y-2">
              {matchup.team1_advantages.map((adv, i) => (
                <div key={i} className="flex items-center justify-between text-sm">
                  <span className="text-gray-300">{adv.label || labelFor(adv.stat)}</span>
                  <span className="text-emerald-400 font-bold">+{adv.margin}</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-sm">No significant statistical advantages</p>
          )}
        </div>
        <div className="bg-gray-900/50 border border-cyan-500/30 rounded-xl p-6">
          <h3 className="text-lg font-semibold mb-4 text-cyan-400">{matchup.team2.name} Advantages</h3>
          {matchup.team2_advantages.length > 0 ? (
            <div className="space-y-2">
              {matchup.team2_advantages.map((adv, i) => (
                <div key={i} className="flex items-center justify-between text-sm">
                  <span className="text-gray-300">{adv.label || labelFor(adv.stat)}</span>
                  <span className="text-cyan-400 font-bold">+{adv.margin}</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-sm">No significant statistical advantages</p>
          )}
        </div>
      </div>

      {/* Key Battles */}
      <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Swords className="w-5 h-5 text-emerald-400" /> Key Battles
        </h3>
        <div className="space-y-4">
          {matchup.key_battles.map((battle, i) => (
            <div key={i} className="p-4 bg-gray-800/50 rounded-lg">
              <h4 className="text-emerald-400 font-semibold mb-1">{battle.battle}</h4>
              <p className="text-gray-300 text-sm">{battle.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Tactical Analysis */}
      <div className="bg-gray-900/50 border border-gray-800 rounded-xl p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Lightbulb className="w-5 h-5 text-cyan-400" /> Tactical Analysis
        </h3>
        <div className="space-y-3">
          {matchup.tactical_analysis.map((ta, i) => (
            <div key={i} className="flex gap-3 p-3 bg-gray-800/30 rounded-lg">
              <div className="w-6 h-6 bg-cyan-500/20 rounded-full flex items-center justify-center shrink-0 mt-0.5">
                <span className="text-cyan-400 text-xs font-bold">{i + 1}</span>
              </div>
              <p className="text-gray-300 text-sm leading-relaxed">{ta}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Prediction */}
      <div className="bg-gradient-to-br from-emerald-500/10 to-cyan-500/10 border border-emerald-500/30 rounded-xl p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Trophy className="w-5 h-5 text-yellow-400" /> Match Prediction
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <div className="text-center p-4 bg-gray-900/50 rounded-lg">
            <p className="text-xs text-gray-500 mb-1">Favorite</p>
            <p className="text-lg font-bold text-yellow-400">{matchup.prediction.favorite}</p>
          </div>
          <div className="text-center p-4 bg-gray-900/50 rounded-lg">
            <p className="text-xs text-gray-500 mb-1">Confidence</p>
            <p className={`text-lg font-bold ${
              matchup.prediction.confidence === "High" ? "text-emerald-400" :
              matchup.prediction.confidence === "Moderate" ? "text-yellow-400" :
              "text-gray-400"
            }`}>{matchup.prediction.confidence}</p>
          </div>
          <div className="text-center p-4 bg-gray-900/50 rounded-lg">
            <p className="text-xs text-gray-500 mb-1">Score Prediction</p>
            <p className="text-lg font-bold text-white">{matchup.prediction.score_prediction}</p>
          </div>
        </div>
        <p className="text-gray-300 text-sm leading-relaxed">{matchup.prediction.narrative}</p>
      </div>
    </div>
  );
}

export default App;
