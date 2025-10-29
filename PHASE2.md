# Project Icarus - Phase 2 Features

## Overview

Phase 2 introduces advanced features including multiple scenarios, a real-time web dashboard, game replay capabilities, and enhanced monitoring. This document covers all Phase 2 features and how to use them.

---

## New Features

### 1. Multiple Scenarios ✨

Three complete scenarios are now available:

#### Scenario 1: DVWA Basic Web Application Pentest (Beginner)
**Target**: Ubuntu with DVWA, MySQL, SSH
**Vulnerabilities**: SQL injection, weak credentials, directory traversal
**Flag**: `/root/flag.txt`

```bash
# Run with default profile
docker-compose up

# Or explicitly
SCENARIO_ID=dvwa_basic_pentest docker-compose --profile scenario1 up
```

#### Scenario 2: Network Services Exploitation (Intermediate)
**Target**: Ubuntu with FTP, SSH, SMB, Telnet
**Vulnerabilities**: Anonymous FTP, SMB EternalBlue, weak passwords, unencrypted telnet
**Flag**: `/opt/secrets/flag.txt`

```bash
SCENARIO_ID=network_services_exploit docker-compose --profile scenario2 up
```

#### Scenario 3: API Security Testing (Advanced)
**Target**: Flask REST API with JWT authentication and MongoDB
**Vulnerabilities**: JWT secret exposure, NoSQL injection, IDOR, broken access control
**Flag**: `/app/data/admin_flag.json`

```bash
SCENARIO_ID=api_security_test docker-compose --profile scenario3 up
```

### 2. Web Dashboard 📊

A comprehensive real-time monitoring dashboard with:

**Features**:
- Real-time game monitoring with WebSocket updates
- Complete game history browser
- Round-by-round action replay
- Live score tracking
- Event timeline
- Statistics and leaderboards
- Game replay viewer

**Access**:
- Frontend: http://localhost:3000
- Backend API: http://localhost:5001
- API Docs: http://localhost:5001

**Components**:
- **Game List**: Browse all games with filtering (running/completed)
- **Game Detail**: View complete game breakdown with rounds and events
- **Live Monitor**: Watch games in real-time as they progress
- **Statistics**: Overall stats, win rates, average scores
- **Leaderboard**: Top-performing games by various metrics

### 3. Scenario Manager 🎯

Dynamic scenario loading and configuration:

```python
from src.scenario_manager import ScenarioManager

manager = ScenarioManager()

# List all scenarios
scenarios = manager.list_scenarios()

# Get specific scenario
scenario = manager.get_scenario('network_services_exploit')

# Get scenario info
info = manager.get_scenario_info('api_security_test')
print(info)
```

### 4. REST API Endpoints 🔌

Complete API for game data access:

```bash
# Get all games
GET /api/games

# Get game details
GET /api/games/{game_id}

# Get rounds for a game
GET /api/games/{game_id}/rounds

# Get events
GET /api/games/{game_id}/events

# Get command history
GET /api/games/{game_id}/commands

# Get game replay data
GET /api/games/{game_id}/replay

# Statistics
GET /api/stats

# Leaderboard
GET /api/leaderboard?metric=red_score&limit=10
```

### 5. WebSocket Real-Time Updates 🔴

Live game monitoring via WebSocket:

```javascript
import { io } from 'socket.io-client';

const socket = io('http://localhost:5001');

// Join a game room
socket.emit('join_game', { game_id: 'your-game-id' });

// Listen for updates
socket.on('game_update', (data) => {
  console.log('Game updated:', data);
});

socket.on('round_complete', (data) => {
  console.log('Round completed:', data);
});

socket.on('game_over', (data) => {
  console.log('Game over:', data);
});
```

---

## Installation & Setup

### Prerequisites

- Docker 24.0+ and Docker Compose 2.20+
- Node.js 18+ (for local dashboard development)
- Python 3.11+
- Anthropic API key

### Quick Start

1. **Configure environment**:
```bash
cp .env.example .env
# Edit .env:
# - Add your ANTHROPIC_API_KEY
# - Set SCENARIO_ID to desired scenario
```

2. **Build all services**:
```bash
docker-compose build
```

3. **Start with dashboard**:
```bash
# Start game + dashboard
docker-compose up

# Or specific scenario
SCENARIO_ID=network_services_exploit docker-compose --profile scenario2 up
```

4. **Access dashboard**:
- Open http://localhost:3000 in your browser
- Watch the game in real-time!

---

## Usage Examples

### Running Different Scenarios

```bash
# Scenario 1: DVWA (default)
docker-compose up

# Scenario 2: Network Services
SCENARIO_ID=network_services_exploit docker-compose --profile scenario2 up

# Scenario 3: API Security
SCENARIO_ID=api_security_test docker-compose --profile scenario3 up
```

### Viewing Game Data

```bash
# List all games
curl http://localhost:5001/api/games

# Get specific game
curl http://localhost:5001/api/games/{game_id}

# Get statistics
curl http://localhost:5001/api/stats

# Get leaderboard
curl http://localhost:5001/api/leaderboard
```

### Monitoring Live Games

1. Open dashboard: http://localhost:3000
2. Click "Live Monitor" tab
3. Select running game from dropdown
4. Watch real-time updates!

### Replaying Past Games

1. Go to "Games" tab
2. Click on any completed game
3. View round-by-round breakdown
4. See all events and commands
5. Analyze team strategies

---

## Architecture

### System Components

```
┌──────────────────────────────────────────────────────────────┐
│                     Admin Network                             │
│                                                               │
│  ┌─────────────┐   ┌──────────────┐   ┌──────────────────┐  │
│  │ Dashboard   │   │  Dashboard   │   │   Orchestrator   │  │
│  │  Frontend   │──▶│   Backend    │◀─▶│                  │  │
│  │  (React)    │   │   (Flask)    │   │  (Game Logic)    │  │
│  └─────────────┘   └──────┬───────┘   └────────┬─────────┘  │
│      :3000              :5001 │                 │            │
│                              │                  │            │
│                    ┌─────────▼──────────────────▼─────────┐  │
│                    │      PostgreSQL Database              │  │
│                    │   (Games, Rounds, Events, Stats)      │  │
│                    └───────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
                                     │
                    ┌────────────────▼──────────────────┐
                    │         CTF Network (Isolated)     │
                    │                                    │
                    │   ┌──────────┐      ┌──────────┐  │
                    │   │ Red Team │─────▶│ Blue Team│  │
                    │   │  (Kali)  │      │ (Target) │  │
                    │   └──────────┘      └──────────┘  │
                    └────────────────────────────────────┘
```

### Dashboard Technology Stack

**Backend**:
- Flask - REST API framework
- Flask-SocketIO - WebSocket support
- PostgreSQL - Data persistence
- psycopg2 - Database adapter

**Frontend**:
- React 18 - UI framework
- Socket.io-client - Real-time updates
- Axios - HTTP client
- Recharts - Data visualization

---

## Configuration

### Environment Variables

```bash
# Scenario Selection
SCENARIO_ID=dvwa_basic_pentest
# Options: dvwa_basic_pentest, network_services_exploit, api_security_test

# AI Models
RED_TEAM_MODEL=claude-sonnet-4-5-20250929
BLUE_TEAM_MODEL=claude-sonnet-4-5-20250929

# Game Settings
MAX_ROUNDS=30
COMMAND_TIMEOUT=30

# Database
DATABASE_URL=postgresql://gamemaster:password@database:5432/cyberrange

# API Keys
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### Scenario Configuration

Scenarios are defined in `scenarios/scenarios.json`:

```json
{
  "scenarios": [
    {
      "id": "scenario_id",
      "name": "Scenario Name",
      "description": "Description",
      "difficulty": "beginner|intermediate|advanced",
      "target_container": "container-name",
      "vulnerabilities": [...],
      "objectives": {
        "red_team": [...],
        "blue_team": [...]
      },
      "flag_location": "/path/to/flag.txt",
      "estimated_rounds": 30
    }
  ]
}
```

---

## API Reference

### REST Endpoints

#### Games

```
GET    /api/games                    # List all games
POST   /api/games                    # Create new game (future)
GET    /api/games/{id}               # Get game details
GET    /api/games/{id}/rounds        # Get all rounds
GET    /api/games/{id}/events        # Get all events
GET    /api/games/{id}/commands      # Get command history
GET    /api/games/{id}/replay        # Get replay data
```

#### Statistics

```
GET    /api/stats                    # Overall statistics
GET    /api/leaderboard              # Top games leaderboard
```

#### Health

```
GET    /api/health                   # API health check
GET    /                             # API information
```

### WebSocket Events

#### Client → Server

```javascript
socket.emit('join_game', { game_id: 'uuid' });
socket.emit('leave_game', { game_id: 'uuid' });
```

#### Server → Client

```javascript
socket.on('connected', callback);
socket.on('joined_game', callback);
socket.on('game_update', callback);
socket.on('round_complete', callback);
socket.on('game_over', callback);
```

---

## Development

### Running Dashboard Locally

**Backend**:
```bash
cd dashboard/backend
pip install -r requirements.txt
python app.py
```

**Frontend**:
```bash
cd dashboard/frontend
npm install
npm start
```

### Adding New Scenarios

1. Create target container in `containers/your-scenario/`
2. Add scenario definition to `scenarios/scenarios.json`
3. Update docker-compose.yml with new profile
4. Test scenario with orchestrator

### Extending the Dashboard

The React frontend is modular. Add new components in `dashboard/frontend/src/components/`:

```javascript
// Example: New visualization component
import React from 'react';

function MyNewComponent({ data }) {
  return (
    <div className="card">
      <h2>My Visualization</h2>
      {/* Your content */}
    </div>
  );
}

export default MyNewComponent;
```

---

## Troubleshooting

### Dashboard Not Loading

```bash
# Check backend logs
docker-compose logs dashboard-backend

# Check frontend logs
docker-compose logs dashboard-frontend

# Verify ports are not in use
lsof -i :3000
lsof -i :5001
```

### WebSocket Connection Issues

- Ensure dashboard-backend is running
- Check firewall settings
- Verify CORS configuration
- Check browser console for errors

### Scenario Not Found

```bash
# List available scenarios
curl http://localhost:5001/api/scenarios

# Verify SCENARIO_ID in .env
cat .env | grep SCENARIO_ID

# Check scenarios.json
cat scenarios/scenarios.json
```

### Container Build Failures

```bash
# Clean rebuild
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

---

## Performance Optimization

### Database Indexes

The schema includes optimized indexes for common queries:
- Game lookups by ID and status
- Round lookups by game and round number
- Event and command log queries

### Dashboard Caching

- Frontend refreshes every 3-5 seconds for live data
- Use WebSocket for instant updates instead of polling
- Replay data is fetched once and cached

### Resource Limits

Add to docker-compose.yml for production:

```yaml
services:
  service-name:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
```

---

## Security Considerations

### Dashboard Security

- Dashboard runs on admin network (isolated from CTF network)
- No authentication in MVP (add for production)
- CORS enabled for development (restrict for production)
- API rate limiting recommended for production

### Production Deployment

For production use:

1. Add authentication (JWT, OAuth)
2. Enable HTTPS
3. Restrict CORS origins
4. Add rate limiting
5. Use environment secrets management
6. Enable audit logging

---

## Future Enhancements

Phase 3 will include:

- **Multi-model support** (GPT-4, Claude Opus, custom models)
- **Tournament mode** (bracket-style competitions)
- **Advanced metasploit integration**
- **Enhanced blue team** (fail2ban, IDS)
- **AI memory system** (learn from past games)
- **Strategy analytics** (pattern recognition)
- **User authentication** (accounts, saved games)
- **Collaborative mode** (multiple AIs per team)

---

## Contributing

Contributions welcome! Areas of interest:

- New scenarios
- Dashboard improvements
- Additional AI models
- Enhanced visualizations
- Performance optimizations
- Documentation

---

## License

MIT License - See LICENSE file

---

**Phase 2 Status**: ✅ Complete
**Last Updated**: 2025-10-29
**Version**: 2.0.0
