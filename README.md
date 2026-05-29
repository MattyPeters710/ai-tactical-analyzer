## Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- PostgreSQL (optional, uses in-memory data by default)

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Install dependencies with Poetry:
```bash
poetry install
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Start the FastAPI server:
```bash
poetry run uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API URL
```

4. Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:5173`

## API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for interactive OpenAPI documentation.

### Endpoints

#### Sports & Teams
- `GET /api/sports` - List all supported sports
- `GET /api/teams` - List all teams (optional sport filter)
- `GET /api/teams/{team_id}` - Get detailed team information

#### Analysis
- `POST /api/analyze/team` - Analyze a single team
- `POST /api/analyze/matchup` - Compare two teams

#### Health
- `GET /healthz` - Health check endpoint

### Request Examples

#### Analyze Team
```bash
curl -X POST "http://localhost:8000/api/analyze/team" \
  -H "Content-Type: application/json" \
  -d '{"team_id": "soccer_mancity"}'
```

#### Analyze Matchup
```bash
curl -X POST "http://localhost:8000/api/analyze/matchup" \
  -H "Content-Type: application/json" \
  -d '{"team1_id": "soccer_mancity", "team2_id": "soccer_realmadrid"}'
```

## Project Structure

```
ai-tactical-analyzer/
|-- backend/
|   |-- app/
|   |   |-- __init__.py
|   |   |-- main.py          # FastAPI application
|   |   |-- analyzer.py      # Analysis engine
|   |   |-- data.py          # Team database
|   |   |-- sports_api.py    # ESPN API client
|   |-- pyproject.toml       # Python dependencies
|   |-- poetry.lock
|   |-- README.md
|-- frontend/
|   |-- src/
|   |   |-- App.tsx          # Main application
|   |   |-- lib/
|   |   |   |-- api.ts       # API client
|   |   |   |-- utils.ts     # Utility functions
|   |   |-- components/      # React components
|   |-- package.json
|   |-- vite.config.ts
|   |-- tailwind.config.js
|-- README.md                # This file
```

## Configuration

### Environment Variables

#### Backend (.env)
```env
# Database (optional)
DATABASE_URL=postgresql://user:password@localhost/dbname

# API Settings
DEBUG=false
HOST=0.0.0.0
PORT=8000

# CORS Settings
ALLOWED_ORIGINS=["http://localhost:5173", "http://localhost:3000"]
```

#### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000
```

## Data Model

The system includes comprehensive data for:
- **Soccer**: 17+ major teams (Premier League, La Liga, Bundesliga, Serie A, Ligue 1)
- **Basketball**: 6 NBA teams
- **American Football**: 5 NFL teams
- **Cricket**: 10 IPL teams (Indian Premier League)

Each team includes:
- 5 core tactical attributes (attack, defense, efficiency, differential, consistency)
- Recent form tracking (W/D/L history)
- Season record and statistics
- Team metadata (league, location, branding)
- Sport-specific metrics (runs for cricket, goals for soccer, points for others)

## Analysis Features

### Team Analysis
- Overall rating calculation
- Tactical identity classification
- Key insights generation (sport-specific)
- Strength/weakness analysis
- Tactical recommendations

### Matchup Analysis
- Statistical comparison across all attributes
- Win probability calculation
- Key tactical battles identification (sport-specific)
- Predictive scoring
- Narrative analysis

## Sport-Specific Features

### Cricket Analysis
- **Batting vs Bowling** - Attack/Defense matchup analysis
- **Run Differential** - Scoring dominance tracking
- **Match Prediction** - Score predictions in runs format
- **Form Tracking** - Win/loss streaks over recent matches
- **Cricket Terminology** - "Complete Outfit", "Batting Powerhouse", "Bowling Fortress" tactical identities

### Soccer Analysis
- Goal-based metrics and predictions
- Possession and efficiency tracking
- Formation-aware tactical identity

### Basketball/American Football Analysis
- Points-based analysis and predictions
- Win percentage and efficiency metrics

## Development

### Code Style
- Python: Black formatter, PEP 8
- TypeScript: ESLint + Prettier
- Commits: Conventional commits

### Testing
```bash
# Backend tests
cd backend && poetry run pytest

# Frontend tests
cd frontend && npm test
```

### Building for Production

#### Backend
```bash
cd backend
poetry build
```

#### Frontend
```bash
cd frontend
npm run build
```
