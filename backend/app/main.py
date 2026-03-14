from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from app.data import SPORTS, get_all_teams, get_teams_by_sport, get_team
from app.analyzer import analyze_team, analyze_matchup

app = FastAPI(title="AI Tactical Analyzer", version="1.0.0")

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


class TeamAnalysisRequest(BaseModel):
    team_id: str


class MatchupRequest(BaseModel):
    team1_id: str
    team2_id: str


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


@app.get("/api/sports")
async def list_sports():
    return {"sports": SPORTS}


@app.get("/api/teams")
async def list_teams(sport: Optional[str] = None):
    if sport:
        teams = get_teams_by_sport(sport)
    else:
        teams = get_all_teams()
    return {"teams": teams, "count": len(teams)}


@app.get("/api/teams/{team_id}")
async def get_team_details(team_id: str):
    team = get_team(team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return {"team": team}


@app.post("/api/analyze/team")
async def analyze_team_endpoint(request: TeamAnalysisRequest):
    team = get_team(request.team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    analysis = analyze_team(team)
    return {"analysis": analysis}


@app.post("/api/analyze/matchup")
async def analyze_matchup_endpoint(request: MatchupRequest):
    team1 = get_team(request.team1_id)
    team2 = get_team(request.team2_id)
    if not team1:
        raise HTTPException(status_code=404, detail=f"Team '{request.team1_id}' not found")
    if not team2:
        raise HTTPException(status_code=404, detail=f"Team '{request.team2_id}' not found")
    if team1["sport"] != team2["sport"]:
        raise HTTPException(status_code=400, detail="Cannot compare teams from different sports")
    result = analyze_matchup(team1, team2)
    return {"matchup": result}
