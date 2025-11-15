# Quick Start Guide

This guide will help you get Project Icarus up and running quickly once the implementation is complete.

## Prerequisites Checklist

Before you begin, ensure you have:

- [ ] Docker 24.0+ installed and running
- [ ] Docker Compose 2.20+ installed
- [ ] Python 3.11 or higher
- [ ] PostgreSQL client (optional, for database inspection)
- [ ] Anthropic API key ([Get one here](https://console.anthropic.com/))
- [ ] At least 8GB RAM available
- [ ] 50GB free disk space

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/Icarus.git
cd Icarus
```

### 2. Set Up Environment Variables

```bash
# Copy the example environment file
cp .env.example .env
```

Edit `.env` and configure the following:

```bash
# Required: Anthropic API key
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Optional: OpenAI API key (if using GPT models)
OPENAI_API_KEY=sk-your-openai-key

# Database configuration
DATABASE_URL=postgresql://gamemaster:password@database:5432/cyberrange
POSTGRES_PASSWORD=your-secure-password-here

# AI Model configuration
RED_TEAM_MODEL=claude-sonnet-4.5
BLUE_TEAM_MODEL=claude-sonnet-4.5

# Game settings
MAX_ROUNDS=30
COMMAND_TIMEOUT=30
LOG_LEVEL=INFO
```

### 3. Build Docker Containers

```bash
# Build all containers
docker-compose build

# This will build:
# - PostgreSQL database container
# - Orchestrator (Python application)
# - Red Team (Kali Linux)
# - Blue Team (Ubuntu target)
# - Dashboard (optional)
```

### 4. Initialize the Database

```bash
# Start the database container
docker-compose up -d database

# Wait for database to be ready (about 10 seconds)
sleep 10

# Initialize schema (first time only)
docker-compose exec orchestrator python scripts/init_db.py

# Verify database setup
docker-compose exec database psql -U gamemaster -d cyberrange -c "\dt"
```

### 5. Start All Services

```bash
# Start all containers
docker-compose up -d

# Check that all containers are running
docker-compose ps

# View logs
docker-compose logs -f
```

## Running Your First Game

### Starting a Game

```bash
# Start a basic web application penetration test scenario
docker-compose exec orchestrator python main.py --scenario dvwa

# Or use the CLI with more options
docker-compose exec orchestrator python main.py \
    --scenario dvwa \
    --max-rounds 20 \
    --red-model claude-sonnet-4.5 \
    --blue-model claude-sonnet-4.5
```

### Available Scenarios

1. **dvwa** - Web Application Pentest (Beginner)
   - SQL injection vulnerabilities
   - Weak authentication
   - Basic exploitation

2. **network** - Network Services Exploitation (Intermediate)
   - Multiple vulnerable services
   - Port scanning
   - Service exploitation

3. **api** - API Security Testing (Advanced)
   - JWT manipulation
   - NoSQL injection
   - API endpoint enumeration

### Watching the Game Live

```bash
# Follow orchestrator logs
docker-compose logs -f orchestrator

# Watch red team container activity
docker-compose exec red-kali bash -c "tail -f /var/log/red-team.log"

# Monitor blue team defenses
docker-compose exec blue-target bash -c "tail -f /var/log/auth.log"
```

### Accessing the Dashboard

If you've enabled the optional web dashboard:

```bash
# Open your browser to:
http://localhost:3000

# Login with default credentials (change in production):
Username: admin
Password: changeme
```

## Understanding the Game Flow

### Game Phases

A typical game progresses through these phases:

1. **Reconnaissance (Rounds 1-5)**
   - Red team scans and enumerates
   - Blue team establishes baselines

2. **Initial Access (Rounds 6-15)**
   - Red team attempts exploitation
   - Blue team detects and blocks

3. **Privilege Escalation (Rounds 16-25)**
   - Red team seeks elevated access
   - Blue team contains breaches

4. **Mission Completion (Rounds 26-30)**
   - Red team exfiltrates data
   - Blue team recovers and hardens

### Scoring

Watch the scores update in real-time:

```bash
# Check current game status
docker-compose exec orchestrator python cli.py status

# View detailed scoring
docker-compose exec orchestrator python cli.py scores --game-id <game-id>
```

## Viewing Results

### Database Queries

Connect to the database to inspect results:

```bash
# Connect to PostgreSQL
docker-compose exec database psql -U gamemaster -d cyberrange

# View recent games
SELECT game_id, start_time, red_score, blue_score, winner
FROM games
ORDER BY start_time DESC
LIMIT 5;

# View rounds for a specific game
SELECT round_number, red_action, blue_action, red_points_earned, blue_points_earned
FROM rounds
WHERE game_id = 'your-game-id-here'
ORDER BY round_number;

# Exit psql
\q
```

### Export Game Replay

```bash
# Export game replay to JSON
docker-compose exec orchestrator python cli.py export \
    --game-id <game-id> \
    --output replay.json

# View replay in web dashboard
# Upload replay.json at http://localhost:3000/replay
```

## Common Commands

### Container Management

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart a specific service
docker-compose restart orchestrator

# View logs
docker-compose logs -f [service-name]

# Access container shell
docker-compose exec red-kali bash
docker-compose exec blue-target bash
docker-compose exec orchestrator bash
```

### Game Management

```bash
# List all games
docker-compose exec orchestrator python cli.py list-games

# Stop current game
docker-compose exec orchestrator python cli.py stop

# Replay a previous game
docker-compose exec orchestrator python cli.py replay --game-id <id>

# Delete old games
docker-compose exec orchestrator python cli.py cleanup --days 30
```

### Database Management

```bash
# Backup database
docker-compose exec database pg_dump -U gamemaster cyberrange > backup.sql

# Restore database
docker-compose exec -T database psql -U gamemaster cyberrange < backup.sql

# Reset database (WARNING: deletes all data)
docker-compose exec orchestrator python scripts/reset_db.py
```

## Troubleshooting

### Containers Won't Start

```bash
# Check Docker daemon is running
docker info

# Check available resources
docker system df

# Remove old containers and volumes
docker-compose down -v
docker system prune -a
```

### API Rate Limits

If you hit Anthropic API rate limits:

```bash
# Edit .env and add delays between requests
RATE_LIMIT_DELAY=2  # seconds between API calls

# Or reduce max rounds
MAX_ROUNDS=10
```

### Database Connection Errors

```bash
# Check database is running
docker-compose ps database

# Check database logs
docker-compose logs database

# Test connection
docker-compose exec database pg_isready -U gamemaster
```

### Permission Errors

```bash
# Fix log directory permissions
sudo chown -R $USER:$USER logs/

# Fix Docker socket permissions (Linux)
sudo chmod 666 /var/run/docker.sock
```

## Next Steps

Now that you have Icarus running:

1. **Experiment with different scenarios**
   - Try each of the three built-in scenarios
   - Compare results across multiple runs

2. **Try different AI models**
   - Compare Claude Sonnet vs Opus
   - Test OpenAI GPT-4 if you have API access

3. **Create custom scenarios**
   - Read [Creating Scenarios](CREATING_SCENARIOS.md)
   - Design your own vulnerable environments

4. **Analyze game data**
   - Explore the PostgreSQL database
   - Build custom queries for insights
   - Export data for analysis

5. **Contribute**
   - Report bugs or suggest features
   - Read [CONTRIBUTING.md](../CONTRIBUTING.md)
   - Join the community

## Getting Help

If you run into issues:

1. Check the [Troubleshooting Guide](TROUBLESHOOTING.md)
2. Search [existing issues](https://github.com/yourusername/Icarus/issues)
3. Ask in [GitHub Discussions](https://github.com/yourusername/Icarus/discussions)
4. Read the [full specification](SPECIFICATION.md)

## Additional Resources

- [Full Documentation](README.md)
- [API Reference](API.md)
- [Architecture Overview](ARCHITECTURE.md)
- [Scoring System Details](SPECIFICATION.md#scoring-system)
- [Security Considerations](SPECIFICATION.md#security-considerations)

---

**Ready to run your first AI vs AI cybersecurity battle!**
