# Project Icarus Documentation

Welcome to the Project Icarus documentation! This directory contains comprehensive guides and references for using and developing the AI-powered cybersecurity training platform.

## Documentation Index

### Getting Started

- **[Quick Start Guide](QUICKSTART.md)** - Get up and running in 15 minutes
- **[Installation Guide](INSTALLATION.md)** *(Coming Soon)* - Detailed installation instructions
- **[First Game Tutorial](FIRST_GAME.md)** *(Coming Soon)* - Step-by-step walkthrough of your first game

### Core Documentation

- **[Complete Specification](SPECIFICATION.md)** - Full technical specification (1,664 lines)
  - System architecture
  - Database schema
  - Scoring system
  - Game phases
  - Implementation roadmap

- **[Architecture Overview](ARCHITECTURE.md)** *(Coming Soon)* - High-level system design
  - Component interactions
  - Data flow
  - Security model

- **[API Reference](API.md)** *(Coming Soon)* - REST API and CLI documentation

### User Guides

- **[Scenario Guide](SCENARIOS.md)** *(Coming Soon)* - Available scenarios and how to use them
- **[Scoring System](SCORING.md)** *(Coming Soon)* - Detailed explanation of points and achievements
- **[Dashboard Guide](DASHBOARD.md)** *(Coming Soon)* - Using the web dashboard
- **[Database Queries](DATABASE_QUERIES.md)** *(Coming Soon)* - Useful SQL queries for analysis

### Developer Documentation

- **[Development Setup](DEVELOPMENT.md)** *(Coming Soon)* - Setting up your development environment
- **[Contributing Guide](../CONTRIBUTING.md)** - How to contribute to the project
- **[Creating Scenarios](CREATING_SCENARIOS.md)** *(Coming Soon)* - Build your own scenarios
- **[AI Agent Development](AI_AGENTS.md)** *(Coming Soon)* - Developing and tuning AI agents
- **[Testing Guide](TESTING.md)** *(Coming Soon)* - Testing framework and best practices

### Operations

- **[Deployment Guide](DEPLOYMENT.md)** *(Coming Soon)* - Production deployment
- **[Monitoring & Logging](MONITORING.md)** *(Coming Soon)* - Observability setup
- **[Troubleshooting](TROUBLESHOOTING.md)** *(Coming Soon)* - Common issues and solutions
- **[Security Hardening](SECURITY.md)** *(Coming Soon)* - Security best practices

## Quick Links by Role

### I'm a User

1. Start with [Quick Start Guide](QUICKSTART.md)
2. Choose a scenario from [Scenario Guide](SCENARIOS.md) *(Coming Soon)*
3. Learn about scoring in [Scoring System](SCORING.md) *(Coming Soon)*
4. View results in [Dashboard Guide](DASHBOARD.md) *(Coming Soon)*

### I'm a Developer

1. Read [Development Setup](DEVELOPMENT.md) *(Coming Soon)*
2. Review [Contributing Guide](../CONTRIBUTING.md)
3. Study the [Complete Specification](SPECIFICATION.md)
4. Check out [AI Agent Development](AI_AGENTS.md) *(Coming Soon)*

### I'm an Operator/Admin

1. Follow [Deployment Guide](DEPLOYMENT.md) *(Coming Soon)*
2. Set up [Monitoring & Logging](MONITORING.md) *(Coming Soon)*
3. Review [Security Hardening](SECURITY.md) *(Coming Soon)*
4. Keep [Troubleshooting](TROUBLESHOOTING.md) handy *(Coming Soon)*

### I'm a Researcher

1. Read the [Complete Specification](SPECIFICATION.md)
2. Understand [AI Agent Development](AI_AGENTS.md) *(Coming Soon)*
3. Explore [Database Queries](DATABASE_QUERIES.md) for analysis *(Coming Soon)*
4. Create custom scenarios with [Creating Scenarios](CREATING_SCENARIOS.md) *(Coming Soon)*

## Documentation Status

| Document | Status | Last Updated |
|----------|--------|--------------|
| Quick Start Guide | ✅ Complete | Nov 2025 |
| Specification | ✅ Complete | Nov 2025 |
| Contributing Guide | ✅ Complete | Nov 2025 |
| Installation Guide | 📝 Planned | - |
| Architecture Overview | 📝 Planned | - |
| API Reference | 📝 Planned | - |
| Scenario Guide | 📝 Planned | - |
| Development Setup | 📝 Planned | - |
| Troubleshooting | 📝 Planned | - |
| Deployment Guide | 📝 Planned | - |

## Frequently Asked Questions

### General Questions

**Q: What is Project Icarus?**
A: An AI-powered cybersecurity training platform where autonomous AI agents compete in red team vs blue team scenarios. See [Complete Specification](SPECIFICATION.md#project-overview).

**Q: What phase is the project in?**
A: Currently in the planning/pre-implementation phase. The specification is complete and we're seeking contributors for the MVP.

**Q: What AI models are supported?**
A: Primary support for Anthropic Claude (Sonnet 4.5). Optional support for OpenAI GPT models. See [Specification](SPECIFICATION.md#ai-integration).

**Q: Is this for training AI models?**
A: No! AIs learn through in-context learning by reading game history. No model training/fine-tuning occurs.

### Technical Questions

**Q: What are the system requirements?**
A: Minimum 8GB RAM, 4 CPU cores, 50GB disk. Recommended 16GB RAM, 8 cores. See [Quick Start Guide](QUICKSTART.md#prerequisites-checklist).

**Q: What operating systems are supported?**
A: Any OS that can run Docker: Linux, macOS, Windows (with WSL2).

**Q: Can I run this without Docker?**
A: Not recommended. Docker provides essential isolation and security. Manual setup would be complex and potentially insecure.

**Q: How much does it cost to run?**
A: Free except for API costs. Anthropic Claude API pricing varies. A typical 30-round game uses approximately 60-100 API calls (~$0.50-$2.00 at current rates).

### Usage Questions

**Q: How long does a game take?**
A: Typically 10-30 minutes depending on rounds (30 rounds = ~15-20 minutes with API delays).

**Q: Can I pause a game?**
A: Not in MVP. Planned for Phase 2. See [Specification](SPECIFICATION.md#implementation-phases).

**Q: Can I replay games?**
A: Yes! All game data is stored in PostgreSQL. Replay functionality planned for Phase 2.

**Q: Can multiple games run simultaneously?**
A: Not in MVP. Planned for Phase 3 with tournament mode.

## Contributing to Documentation

Found an error? Want to improve the docs? Please:

1. Open an issue describing the problem
2. Submit a pull request with fixes
3. Follow the [Contributing Guide](../CONTRIBUTING.md)

Documentation contributions are highly valued!

### Documentation Style Guide

- Use clear, concise language
- Include code examples for technical content
- Add diagrams for complex concepts (Mermaid preferred)
- Link to related documentation
- Keep line length under 100 characters
- Use proper Markdown formatting

## Getting Help

Can't find what you need?

- Check if a planned document will answer your question
- Search [GitHub Issues](https://github.com/yourusername/Icarus/issues)
- Ask in [GitHub Discussions](https://github.com/yourusername/Icarus/discussions)
- Tag documentation issues with `documentation` label

## Roadmap

### Phase 1 (MVP) Documentation Priorities

- [x] Quick Start Guide
- [x] Complete Specification
- [x] Contributing Guide
- [ ] Installation Guide
- [ ] Troubleshooting Guide
- [ ] Basic API Reference

### Phase 2 Documentation

- [ ] Architecture Deep Dive
- [ ] Scenario Creation Guide
- [ ] Dashboard User Guide
- [ ] Database Query Examples
- [ ] Deployment Guide

### Phase 3 Documentation

- [ ] Advanced AI Agent Tuning
- [ ] Tournament Mode Guide
- [ ] Multi-Game Analytics
- [ ] Educational Curriculum

## Additional Resources

### External Links

- [Anthropic Claude API Docs](https://docs.anthropic.com/)
- [Docker Documentation](https://docs.docker.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Kali Linux Tools](https://www.kali.org/tools/)
- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [MITRE ATT&CK Framework](https://attack.mitre.org/)

### Community

- [Project GitHub](https://github.com/yourusername/Icarus)
- [Discussions](https://github.com/yourusername/Icarus/discussions)
- Discord *(Coming Soon)*

---

**Document Version**: 1.0.0
**Last Updated**: November 2025
**Maintainers**: Project Icarus Team
