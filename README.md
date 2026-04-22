Backend

backend/app/sports_api.py (new) — async client for ESPN's team, team-detail, and schedule endpoints with per-endpoint TTL caching (default 1 hour, configurable via SPORTS_API_CACHE_TTL). Covers:
Soccer: Premier League, La Liga, Bundesliga, Serie A, Ligue 1
Basketball: all 30 NBA teams
American Football: all 32 NFL teams
backend/app/data.py — now async and thin. Calls sports_api, normalizes records into the shape the analyzer expects, and derives six sport-appropriate ratings (attack, defense, efficiency, differential, consistency, form) on a 0–100 scale.
backend/app/analyzer.py — rewritten so every narrative line is grounded in real numbers. Tactical identity, key insights, recommendations, matchups, key battles, and score predictions are all derived from ESPN record data. Score predictions use expected points based on each team's scoring average and opponent defensive average.
backend/app/main.py — endpoints are now await-ed; API shape unchanged.
httpx added as a dependency.
Frontend

Team cards render real ESPN team badges (logo URLs) instead of first-letter avatars.
Analysis page shows record, standing summary, and a season-snapshot grid sourced from the API.
Matchup header replaces "formation" text with real season records.
Stat labels come from the server (stat_labels map) so the radar/bar charts and top/weak attribute lists show proper names ("Point Differential" instead of "differential").
TypeScript types in src/lib/api.ts updated to match the new response shapes; removed formation, style, key_players, tactical_notes, etc. that no longer exist.
What this does NOT do
No API key or signup required — ESPN's public endpoints are used as-is. Respect their (undocumented) rate limits by leaving the TTL cache in place.
No Postgres persistence yet — data is fetched on-demand and cached in-process.
No authenticated/premium data sources; if you ever want richer data (e.g. player-level stats), swapping in a paid API later is now a one-file change.
Review & Testing Checklist for Human
 Start the backend (poetry install && poetry run uvicorn app.main:app --reload inside backend/) and frontend (npm install && npm run dev inside frontend/). Verify the Home → Sports → Teams flow loads real logos for soccer / NBA / NFL.
 Click into a team (try Manchester City, Boston Celtics, Kansas City Chiefs) and check that the identity narrative, insights, and season snapshot reflect the real numbers shown in the ESPN record summary.
 Run a matchup between two NBA teams and between two Premier League teams. Confirm the score prediction, radar chart labels, and "advantages" list all read cleanly.
 Decide whether the ESPN-only data source is acceptable, or whether you'd rather add a TheSportsDB fallback for richer team descriptions / wider league coverage (Champions League, MLS, etc.).
Notes
ESPN's API is undocumented and could change without warning; the client logs warnings and returns empty lists on HTTP errors so partial outages degrade gracefully rather than hard-failing.
The six-stat universal schema intentionally collapses sport-specific FIFA-style attributes into outcome-based ones that can be computed consistently across soccer/NBA/NFL. If you want sport-specific advanced stats back (e.g. 3PT%, pass yards), we'd layer them on top of the ESPN stats payload — that's a small follow-up, not a rewrite.
