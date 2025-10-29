# Project Icarus

**AI Red Team vs Blue Team Cyber Range**

An automated cyber security training environment where AI models (using Claude or other LLMs) control both offensive (red team) and defensive (blue team) operations in containerized environments.

---

## Overview

Project Icarus is a novel approach to cybersecurity training and AI research. Two AI agents compete against each other:

- **Red Team AI**: Controls a Kali Linux container and attempts to compromise target systems
- **Blue Team AI**: Defends target systems, monitors for attacks, and implements countermeasures
- **Orchestrator**: Manages game flow, executes commands, tracks state, and provides context to AIs
- **Database**: Centralized logging and game state management

The AIs learn through **in-context learning** (reading history of what worked/failed) rather than model training.

---

## Features

### Phase 1 (MVP) ✅
- ✅ Automated AI vs AI cybersecurity competitions
- ✅ Real penetration testing tools (nmap, metasploit, sqlmap, etc.)
- ✅ Realistic vulnerable applications (DVWA)
- ✅ Comprehensive scoring system
- ✅ Detailed logging and telemetry
- ✅ Docker-based isolation and portability
- ✅ Phase-based gameplay (reconnaissance → initial access → privilege escalation → exfiltration)

### Phase 2 (Advanced) ✅ NEW!
- ✅ **3 Complete Scenarios** (DVWA, Network Services, API Security)
- ✅ **Real-time Web Dashboard** with live monitoring
- ✅ **WebSocket Live Updates** for instant game feedback
- ✅ **Game Replay System** with full round-by-round analysis
- ✅ **REST API** for game data access
- ✅ **Statistics & Leaderboards**
- ✅ **Dynamic Scenario Loading** from configuration files

**📊 [View Phase 2 Documentation](PHASE2.md)** for complete feature guide!

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Orchestrator                           │
│  • Game loop management                                     │
│  • AI decision coordination                                 │
│  • Command execution via Docker API                         │
│  • Scoring and event detection                              │
└──────┬────────────────────────────────┬─────────────────────┘
       │                                │
       │  ┌─────────────────────────────▼──────┐
       │  │     PostgreSQL Database             │
       │  │  • Game state & history             │
       │  │  • Command logs                     │
       │  │  • Telemetry & events               │
       │  └─────────────────────────────────────┘
       │
  ┌────┴─────────────────────────────────┐
  │                                      │
  │  CTF Network (isolated)              │
  │                                      │
  ├────▼─────┐              ┌──────▼─────┤
  │   Red    │              │    Blue    │
  │   Team   │──── Attack ─▶│   Team     │
  │  (Kali)  │   Traffic    │  (Target)  │
  └──────────┘              └────────────┘
```

---

## Prerequisites

- **Docker** 24.0+ and **Docker Compose** 2.20+
- **Python** 3.11+ (for local development)
- **Anthropic API Key** (for Claude AI)
- **8GB RAM minimum** (16GB recommended)
- **4 CPU cores minimum** (8 cores recommended)
- **50GB disk space**

---

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/icarus.git
cd icarus
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
nano .env
```

Required environment variables:
```bash
ANTHROPIC_API_KEY=sk-ant-your-key-here
POSTGRES_PASSWORD=secure_password_here
```

### 3. Build and Start

```bash
# Build all containers
docker-compose build

# Start the game
docker-compose up
```

The orchestrator will automatically start a game session when all containers are ready.

### 4. Watch the Game

**Option A: Web Dashboard (Recommended)**
- Open http://localhost:3000 in your browser
- Real-time game monitoring with live updates
- View round-by-round breakdown
- Statistics and leaderboards

**Option B: Console Output**
Watch the console to see:
- Each round's actions and decisions
- AI reasoning for both teams
- Command executions and results
- Points scored and events triggered
- Final scores and winner

### 5. View Logs

```bash
# Orchestrator logs
docker-compose logs -f orchestrator

# Database query example
docker exec -it game-db psql -U gamemaster -d cyberrange -c "SELECT * FROM games ORDER BY start_time DESC LIMIT 1;"
```

---

## Game Flow

### Phases

1. **Reconnaissance (Rounds 1-5)**
   - Red team scans for services and vulnerabilities
   - Blue team establishes baseline and monitoring

2. **Initial Access (Rounds 6-15)**
   - Red team attempts exploitation
   - Blue team detects and blocks attacks

3. **Privilege Escalation (Rounds 16-25)**
   - Red team seeks root access
   - Blue team contains breaches

4. **Exfiltration (Rounds 26-30)**
   - Red team tries to extract flag file
   - Blue team prevents data loss

### Scoring

**Red Team Points:**
- Port scan complete: 10 points
- Service identified: 15 points
- Vulnerability found: 25 points
- Credentials obtained: 50 points
- Shell access gained: 100 points
- Privilege escalation: 150 points
- Data exfiltration: 300 points (wins game)

**Blue Team Points:**
- Attack detected: 25 points
- Attack blocked: 50 points
- Attacker IP banned: 75 points
- Service maintained: 10 points per round

**Penalties:**
- Service down: -50 points (blue)
- Detected by blue team: -25 points (red)
- False positive alert: -10 points (blue)

---

## Project Structure

```
icarus/
├── docker-compose.yml          # Container orchestration
├── .env.example                # Environment template
├── README.md                   # This file
├── overview.md                 # Detailed specification
├── LICENSE                     # MIT License
│
├── database/
│   ├── schema.sql              # Database schema
│   └── seed.sql                # Seed data
│
├── orchestrator/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py                 # Entry point
│   └── src/
│       ├── database.py         # Database interface
│       ├── red_team_agent.py   # Red team AI
│       ├── blue_team_agent.py  # Blue team AI
│       ├── orchestrator.py     # Game loop
│       └── scoring.py          # Event detection
│
├── containers/
│   ├── red-kali/
│   │   └── Dockerfile          # Kali Linux with tools
│   └── blue-target/
│       └── Dockerfile          # Ubuntu with DVWA
│
└── logs/                       # Log output directory
```

---

## Configuration

### Environment Variables

See `.env.example` for all available options:

- `ANTHROPIC_API_KEY`: Your Claude API key (required)
- `RED_TEAM_MODEL`: AI model for red team (default: claude-sonnet-4-5-20250929)
- `BLUE_TEAM_MODEL`: AI model for blue team (default: claude-sonnet-4-5-20250929)
- `MAX_ROUNDS`: Maximum game rounds (default: 30)
- `COMMAND_TIMEOUT`: Command timeout in seconds (default: 30)
- `LOG_LEVEL`: Logging level (default: INFO)

### Database

PostgreSQL connection string format:
```
postgresql://gamemaster:password@database:5432/cyberrange
```

---

## Development

### Running Tests

```bash
# Install dev dependencies
pip install -r orchestrator/requirements.txt

# Run tests
cd orchestrator
pytest
```

### Accessing Containers

```bash
# Red team Kali Linux
docker exec -it red-kali bash

# Blue team target
docker exec -it blue-target bash

# Database
docker exec -it game-db psql -U gamemaster -d cyberrange
```

### Manual Commands

```bash
# Start individual services
docker-compose up database
docker-compose up red-kali blue-target
docker-compose up orchestrator

# Rebuild specific container
docker-compose build orchestrator

# View database schema
docker exec -it game-db psql -U gamemaster -d cyberrange -c "\dt"

# Stop all containers
docker-compose down

# Remove volumes (reset database)
docker-compose down -v
```

---

## Scenarios

### Current Scenario: DVWA Basic Pentest

**Target Setup:**
- Ubuntu 22.04 with Apache2
- DVWA (Damn Vulnerable Web Application)
- MySQL database
- SSH enabled with weak password (admin/password123)
- Flag file at `/root/flag.txt`

**Vulnerabilities:**
- SQL injection in login forms
- Weak SSH credentials
- Unpatched services
- Directory traversal

---

## Security Considerations

### Isolation

- CTF network is isolated (no internet access)
- Containers have resource limits
- Commands have strict timeouts
- Dangerous commands are blocked

### Safety

This project is for **educational and research purposes only**. The vulnerable systems are intentionally insecure and should never be exposed to public networks.

---

## Troubleshooting

### Containers Won't Start

```bash
# Check Docker status
docker ps -a

# View container logs
docker-compose logs red-kali
docker-compose logs blue-target

# Restart containers
docker-compose restart
```

### Database Connection Issues

```bash
# Check database is ready
docker exec game-db pg_isready -U gamemaster

# View database logs
docker-compose logs database

# Reset database
docker-compose down -v
docker-compose up database
```

### API Rate Limits

If you hit Claude API rate limits:
- Increase delay between rounds in orchestrator.py
- Reduce MAX_ROUNDS in .env
- Use different models for red/blue teams

### Out of Memory

If containers crash due to memory:
- Increase Docker memory allocation
- Reduce number of concurrent processes
- Add resource limits in docker-compose.yml

---

## Roadmap

### Phase 1: MVP ✅ (Current)
- Basic orchestrator with game loop
- Red team AI with simple commands
- Blue team AI with monitoring
- PostgreSQL database integration
- One scenario (DVWA)
- Simple scoring system

### Phase 2: Core Features (Next)
- Multiple scenarios
- Advanced tools (metasploit, sqlmap)
- Enhanced blue team capabilities
- Web dashboard for visualization
- Game replay functionality

### Phase 3: Intelligence & Learning
- AI memory system (learn from past games)
- Strategy pattern recognition
- Multi-game tournaments
- Model comparison tools

### Phase 4: Advanced Capabilities
- Multi-container targets
- SIEM integration
- Real-world CVE scenarios
- Multi-agent coordination

---

## Contributing

Contributions are welcome! Areas of interest:

- New scenarios and vulnerable applications
- Enhanced AI prompting strategies
- Additional security tools
- Web dashboard development
- Documentation improvements
- Bug fixes and optimizations

Please open an issue before starting major work.

---

## License

MIT License - See LICENSE file for details

---

## Credits

- Built with [Anthropic Claude](https://www.anthropic.com/)
- Vulnerable app: [DVWA](https://github.com/digininja/DVWA)
- Penetration testing tools: [Kali Linux](https://www.kali.org/)
- Container orchestration: [Docker](https://www.docker.com/)

---

## Citation

If you use Project Icarus in research or education, please cite:

```
Project Icarus: AI Red Team vs Blue Team Cyber Range
https://github.com/yourusername/icarus
```

---

## Contact & Support

- **Issues**: https://github.com/yourusername/icarus/issues
- **Documentation**: See overview.md for detailed specifications
- **Community**: [Coming soon]

---

## Disclaimer

This project is for **educational and authorized security testing only**. Misuse of these tools for unauthorized access to systems is illegal. Users are responsible for compliance with all applicable laws and regulations.

---

**Built with Claude Code** 🚀
