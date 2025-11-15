# Project Icarus

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Status](https://img.shields.io/badge/Status-Planning-yellow.svg)]()
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Required-blue.svg)](https://www.docker.com/)

## AI-Powered Cybersecurity Training Platform

An automated red team vs blue team cyber range where AI models (using Claude or other LLMs) control both offensive and defensive operations in realistic containerized security scenarios.

### What is Project Icarus?

Project Icarus creates an autonomous cybersecurity training environment where:

- **Red Team AI** controls a Kali Linux container to perform penetration testing
- **Blue Team AI** defends target systems, monitors for attacks, and implements countermeasures
- **Game Orchestrator** manages the competition, executes commands, and tracks scoring
- **PostgreSQL Database** logs all actions, maintains game state, and provides AI memory
- **AIs Learn** through in-context learning by analyzing history of successful and failed attempts

This platform enables:
- Automated security research and testing
- AI model comparison for cybersecurity tasks
- Educational cybersecurity training scenarios
- Development of autonomous security agents

## Current Status

**Project Stage**: Planning / Pre-implementation

The project currently consists of comprehensive specification documents. Implementation has not yet begun.

## Quick Start

### Prerequisites

- Docker 24.0+
- Docker Compose 2.20+
- Python 3.11+
- PostgreSQL 15+ (via Docker)
- Anthropic API key (for Claude)

### Installation (When Implemented)

```bash
# Clone the repository
git clone https://github.com/yourusername/Icarus.git
cd Icarus

# Set up environment variables
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# Build and start containers
docker-compose up --build

# Initialize database (first run only)
docker-compose exec orchestrator python init_db.py

# Start a game
docker-compose exec orchestrator python main.py --scenario dvwa
```

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      Orchestrator                           │
│  • Game loop management                                     │
│  • AI decision coordination                                 │
│  • Command execution via Docker API                         │
└──────┬────────────────────────────────┬─────────────────────┘
       │                                │
       │  ┌─────────────────────────────▼──────┐
       │  │     PostgreSQL Database            │
       │  │  • Game state & history            │
       │  │  • Command logs                    │
       │  │  • AI memory/context               │
       │  └────────────────────────────────────┘
       │
  ┌────┴─────────────────────────────────┐
  │          CTF Network (Isolated)      │
  │                                      │
  │  ┌──────────┐              ┌───────────┐
  │  │   Red    │              │   Blue    │
  │  │   Team   │──── Attack ─▶│   Team    │
  │  │  (Kali)  │    Traffic   │ (Target)  │
  │  └──────────┘              └───────────┘
  └──────────────────────────────────────────┘
```

## Key Features (Planned)

### Core Capabilities
- ✅ Autonomous AI agents for offense and defense
- ✅ Realistic penetration testing scenarios
- ✅ Containerized, isolated environments
- ✅ Comprehensive logging and replay
- ✅ Scoring system for competitive evaluation
- ✅ In-context learning (no model training required)

### Scenarios
1. **Web Application Pentest** - DVWA exploitation
2. **Network Services** - Multi-service environment with common vulnerabilities
3. **API Security** - REST API with authentication flaws

### AI Integration
- Primary: Anthropic Claude (Sonnet 4.5)
- Optional: OpenAI GPT models
- Extensible to other LLMs

## Documentation

- **[Quick Start Guide](docs/QUICKSTART.md)** - Get up and running in 15 minutes
- **[Complete Specification](docs/SPECIFICATION.md)** - Full technical specification (1,664 lines)
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute to the project
- **[Documentation Index](docs/README.md)** - Complete documentation directory
- **[Architecture Details](docs/ARCHITECTURE.md)** - System design deep-dive (coming soon)

## Technology Stack

**Infrastructure**
- Docker & Docker Compose
- PostgreSQL 15
- Python 3.11+

**AI**
- Anthropic Claude API
- OpenAI API (optional)
- LangChain (optional)

**Security Tools**
- Red Team: nmap, metasploit, sqlmap, hydra, nikto, burp suite
- Blue Team: fail2ban, iptables, auditd, SIEM tools

## Implementation Roadmap

### Phase 1: MVP (2-3 weeks)
- Basic orchestrator with game loop
- Simple red/blue AI agents
- PostgreSQL integration
- One scenario (DVWA)
- Command-line interface

### Phase 2: Core Features (3-4 weeks)
- Multiple scenarios
- Advanced tooling
- Web dashboard
- Event detection
- Game replay

### Phase 3: Intelligence (4-6 weeks)
- AI memory and learning
- Tournament mode
- Model comparison
- Strategy analytics

### Phase 4: Advanced (6-8 weeks)
- Multi-container networks
- SIEM integration
- Autonomous exploit development
- Real-world CVE scenarios

### Phase 5: Production (Ongoing)
- Cloud deployment
- Multi-tenant architecture
- API for integrations
- Educational content

## Scoring System

### Red Team Points
- Port scan: 10
- Service identified: 15
- Vulnerability found: 25
- Valid credentials: 50
- Shell access: 100
- Privilege escalation: 150
- Persistence: 200
- Data exfiltration: 300

### Blue Team Points
- Attack detected: 25
- Attack blocked: 50
- Attacker IP banned: 75
- Vulnerability patched: 100
- Service maintained: 10/round
- Forensics complete: 150
- Recovery complete: 200

## Contributing

Contributions are welcome! This project is in the planning phase, so now is a great time to get involved.

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## Security and Ethics

**Important**: This project is for:
- Educational purposes
- Authorized security testing
- Research and development
- Defensive security training

**Never** use these tools or techniques for:
- Unauthorized access to systems
- Malicious attacks
- Illegal activities

All scenarios run in isolated Docker containers with no external network access.

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Contact & Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/Icarus/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/Icarus/discussions)
- **Documentation**: [Project Wiki](https://github.com/yourusername/Icarus/wiki)

## Acknowledgments

- Inspired by traditional cyber ranges and CTF competitions
- Built with Anthropic's Claude AI
- Utilizes open-source security tools from the Kali Linux project
- Vulnerable applications from OWASP and the security community

## References

- [MITRE ATT&CK Framework](https://attack.mitre.org/)
- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [Anthropic Claude API](https://docs.anthropic.com/)
- [Docker Documentation](https://docs.docker.com/)
- [Kali Linux Tools](https://www.kali.org/tools/)

---

**Status**: Pre-implementation planning phase. Looking for contributors!

**Last Updated**: November 2025
