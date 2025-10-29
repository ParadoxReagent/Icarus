# Interactive Launcher Guide

## Overview

The Project Icarus launcher (`./icarus` or `python3 start.py`) provides an easy, interactive way to start games with scenario selection.

## Quick Start

```bash
./icarus
```

## What Happens

### Step 1: Environment Check

The launcher automatically:
- Creates `.env` from `.env.example` if needed
- Checks for `ANTHROPIC_API_KEY`
- Warns if API key is not configured

### Step 2: Scenario Selection

You'll see a menu like this:

```
======================================================================
⚔️  PROJECT ICARUS - AI Cyber Range Launcher
    AI Red Team vs Blue Team Competition
======================================================================

Available Scenarios:

1. DVWA Basic Web Application Pentest
   Difficulty: BEGINNER
   Target: blue-target

2. Network Services Exploitation
   Difficulty: INTERMEDIATE
   Target: network-services

3. API Security Testing
   Difficulty: ADVANCED
   Target: api-target

Select a scenario (1-3) or 'q' to quit:
```

### Step 3: Scenario Details

After selecting, you'll see full details:

```
──────────────────────────────────────────────────────────────────────
Scenario Details:

Name: Network Services Exploitation
ID: network_services_exploit
Difficulty: INTERMEDIATE

Description:
  Target multiple network services including FTP, SSH, SMB, and Telnet
  with various vulnerabilities

Vulnerabilities:
  • Anonymous FTP access
  • SMB EternalBlue (CVE-2017-0144)
  • Weak SSH passwords
  • Unencrypted Telnet
  • Misconfigured NFS shares

Red Team Objectives:
  🔴 Enumerate all network services
  🔴 Exploit anonymous FTP or SMB vulnerability
  🔴 Establish persistence via cron job
  🔴 Lateral movement between services
  🔴 Exfiltrate sensitive data

Blue Team Objectives:
  🔵 Detect port scanning activity
  🔵 Block exploitation attempts
  🔵 Remove backdoors and persistence
  🔵 Harden service configurations
  🔵 Monitor for lateral movement

Flag Location: /opt/secrets/flag.txt
Estimated Rounds: 35
──────────────────────────────────────────────────────────────────────

Start this scenario? (y/n):
```

### Step 4: Build Containers

If you choose to build:

```
Build containers? (y/n):
  y - Build containers (recommended for first run or after changes)
  n - Skip build (faster if already built)

Build? (y/n): y

──────────────────────────────────────────────────────────────────────
🔨 Building Docker containers...

[docker build output...]

✓ Containers built successfully!
```

### Step 5: Start Game

The launcher:
1. Starts all containers with `docker-compose up`
2. Waits for services to be ready
3. Automatically opens `http://localhost:3000` in your browser
4. Shows live logs in the terminal

```
──────────────────────────────────────────────────────────────────────
🚀 Starting Project Icarus...

Running: docker-compose --profile scenario2 up
Scenario: network_services_exploit

⏳ Starting containers (this may take a minute)...

✓ Containers starting...

Dashboard will be available at:
  http://localhost:3000

Opening dashboard in browser...
✓ Dashboard opened in browser

Game is now running!

Monitoring logs (Press Ctrl+C to stop):

──────────────────────────────────────────────────────────────────────

[Live game logs appear here...]
```

## Usage Examples

### Basic Usage

```bash
./icarus
```

### Quit Before Starting

```bash
./icarus
# At the selection prompt, type 'q' to quit
Select a scenario (1-3) or 'q' to quit: q
```

### Stop Running Game

Press `Ctrl+C` in the terminal:

```
^C
⚠️  Interrupted by user
Stopping containers...
✓ Stopped
```

## Features

### Color-Coded Output

- 🟢 **Green**: Success messages
- 🟡 **Yellow**: Warnings and info
- 🔴 **Red**: Errors
- 🔵 **Cyan**: Headers and commands

### Automatic Browser Opening

After starting, the launcher automatically opens your default browser to `http://localhost:3000` where you can:
- Watch the game in real-time
- View round-by-round breakdowns
- See statistics and scores
- Monitor live updates

### Smart Container Building

The launcher asks if you want to build:
- **First run**: Always build
- **After changes**: Build again
- **Repeat runs**: Skip build for faster startup

### Environment Validation

Checks for:
- `.env` file existence
- `ANTHROPIC_API_KEY` configuration
- Proper scenario files

## Troubleshooting

### "ANTHROPIC_API_KEY not configured"

```bash
# Edit .env file
nano .env

# Add your key:
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
```

### "scenarios.json not found"

Make sure you're running from the project root:
```bash
cd /path/to/icarus
./icarus
```

### "Build failed"

Try cleaning and rebuilding:
```bash
docker-compose down -v
./icarus
# Choose 'y' to build
```

### Port Already in Use

If ports 3000 or 5001 are in use:
```bash
# Find what's using the port
lsof -i :3000
lsof -i :5001

# Kill the process or change ports in docker-compose.yml
```

### Browser Doesn't Open

The dashboard URL is always shown. Manually open:
```
http://localhost:3000
```

## Advanced Options

### Run Specific Scenario Directly

While the interactive launcher is recommended, you can still use docker-compose directly:

```bash
# Set scenario in .env
echo "SCENARIO_ID=network_services_exploit" >> .env

# Build and run with profile
docker-compose --profile scenario2 up
```

### View Only Container Logs

```bash
# In another terminal while game is running
docker-compose logs -f orchestrator
docker-compose logs -f red-kali
docker-compose logs -f blue-target
```

### Access Dashboard Without Launcher

```bash
# Start containers manually
docker-compose up -d

# Dashboard is at:
# http://localhost:3000
```

## Tips

1. **First Run**: Always choose to build containers
2. **Testing Different Scenarios**: Skip build after first run for faster iterations
3. **Watch the Dashboard**: Open http://localhost:3000 for the best experience
4. **Learn from Logs**: Terminal logs show AI reasoning - very educational!
5. **Clean Between Runs**: Use `docker-compose down` to stop everything cleanly

## Example Session

Complete example of using the launcher:

```bash
# Start launcher
./icarus

# Output:
# ⚔️  PROJECT ICARUS - AI Cyber Range Launcher
# Available Scenarios:
# 1. DVWA Basic Web Application Pentest
# 2. Network Services Exploitation
# 3. API Security Testing

# Select scenario
Select a scenario (1-3) or 'q' to quit: 2

# Review details
# [Detailed scenario information shown]
Start this scenario? (y/n): y

# Build containers
Build? (y/n): y
# [Build process...]
# ✓ Containers built successfully!

# Game starts
# 🚀 Starting Project Icarus...
# ✓ Dashboard opened in browser
# [Logs streaming...]

# Watch in browser at http://localhost:3000
# Press Ctrl+C when done

^C
# ⚠️  Interrupted by user
# Stopping containers...
# ✓ Stopped
```

## Need Help?

- Check [README.md](README.md) for full documentation
- See [PHASE2.md](PHASE2.md) for advanced features
- View [overview.md](overview.md) for complete specifications

---

**Happy Hacking!** 🚀
