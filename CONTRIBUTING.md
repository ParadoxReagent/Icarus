# Contributing to Project Icarus

Thank you for your interest in contributing to Project Icarus! This document provides guidelines and instructions for contributing to this AI-powered cybersecurity training platform.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Creating Scenarios](#creating-scenarios)
- [Documentation](#documentation)
- [Community](#community)

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inspiring community for all. Please be respectful and constructive in all interactions.

### Expected Behavior

- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

### Unacceptable Behavior

- Harassment, discrimination, or derogatory comments
- Publishing others' private information without permission
- Trolling, insulting/derogatory comments, and personal attacks
- Other conduct which could reasonably be considered inappropriate

## Getting Started

Project Icarus is currently in the **planning/pre-implementation phase**. This is an excellent time to get involved as we're building the foundation!

### Current Priorities

1. **MVP Development** - Implementing the basic orchestrator and AI agents
2. **Database Schema** - Finalizing and implementing the PostgreSQL schema
3. **Docker Configuration** - Creating Dockerfiles and docker-compose setup
4. **Testing Framework** - Establishing unit and integration tests
5. **Documentation** - Expanding guides and tutorials

### Areas Where We Need Help

- Python development (orchestrator, AI agents)
- Docker and containerization
- PostgreSQL database design
- Security tool expertise (Kali, pentesting)
- Documentation and tutorials
- UI/UX design (for future dashboard)
- Testing and QA

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:

- **Clear title** describing the problem
- **Detailed description** of the issue
- **Steps to reproduce** the behavior
- **Expected behavior** vs actual behavior
- **Environment details** (OS, Docker version, Python version)
- **Screenshots** if applicable

### Suggesting Enhancements

We welcome feature suggestions! Please create an issue with:

- **Clear title** describing the enhancement
- **Detailed description** of the proposed feature
- **Use case** - why is this useful?
- **Possible implementation** approach (if you have ideas)
- **Alternatives considered**

### Your First Contribution

New to open source? Here are some good first issues:

- Documentation improvements
- Adding comments to code
- Writing tests for existing code
- Fixing typos or formatting
- Adding examples to the README

Look for issues labeled `good-first-issue` or `help-wanted`.

## Development Setup

### Prerequisites

```bash
# Required
- Docker 24.0+
- Docker Compose 2.20+
- Python 3.11+
- Git
- Anthropic API key

# Recommended
- Visual Studio Code or PyCharm
- PostgreSQL client (psql, pgAdmin, or DBeaver)
```

### Initial Setup

```bash
# 1. Fork the repository on GitHub
# 2. Clone your fork
git clone https://github.com/YOUR-USERNAME/Icarus.git
cd Icarus

# 3. Add upstream remote
git remote add upstream https://github.com/ORIGINAL-OWNER/Icarus.git

# 4. Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 5. Install dependencies (when available)
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 6. Set up environment variables
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# 7. Create a feature branch
git checkout -b feature/your-feature-name
```

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://peps.python.org/pep-0008/) with some modifications:

- **Line length**: 100 characters (not 79)
- **Docstrings**: Google style docstrings
- **Type hints**: Use type hints for function signatures
- **Formatting**: Use `black` for code formatting
- **Linting**: Use `ruff` for linting

### Code Formatting

```bash
# Format code with black
black orchestrator/ tests/

# Check with ruff
ruff check orchestrator/ tests/

# Type checking with mypy
mypy orchestrator/
```

### Example Code Style

```python
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class RedTeamAgent:
    """
    AI-controlled penetration testing agent.

    This class manages the red team's offensive operations, including
    reconnaissance, exploitation, and data exfiltration.

    Attributes:
        api_key: Anthropic API key for Claude
        model: The AI model to use (e.g., "claude-sonnet-4.5")
        memory: List of previous actions and results
    """

    def __init__(self, api_key: str, model: str = "claude-sonnet-4.5") -> None:
        """
        Initialize the Red Team Agent.

        Args:
            api_key: Anthropic API key
            model: AI model identifier

        Raises:
            ValueError: If api_key is empty
        """
        if not api_key:
            raise ValueError("API key cannot be empty")

        self.api_key = api_key
        self.model = model
        self.memory: List[Dict[str, Any]] = []

        logger.info(f"Initialized RedTeamAgent with model {model}")

    def decide_action(
        self,
        observation: Dict[str, Any],
        history: List[Dict[str, Any]]
    ) -> Dict[str, str]:
        """
        Decide the next action based on current observation.

        Args:
            observation: Current environment state
            history: Previous actions and results

        Returns:
            Dictionary containing reasoning, command, and expected outcome

        Example:
            >>> agent = RedTeamAgent(api_key="sk-...")
            >>> obs = {"phase": "reconnaissance", "access_level": "external"}
            >>> action = agent.decide_action(obs, [])
            >>> print(action["command"])
            'nmap -sV target.local'
        """
        # Implementation here
        pass
```

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(orchestrator): add game state persistence
fix(red-agent): correct command timeout handling
docs(readme): update installation instructions
test(blue-agent): add monitoring tests
```

## Testing Guidelines

### Writing Tests

```python
import pytest
from orchestrator.agents import RedTeamAgent

class TestRedTeamAgent:
    """Test suite for RedTeamAgent class."""

    @pytest.fixture
    def agent(self):
        """Create a RedTeamAgent instance for testing."""
        return RedTeamAgent(api_key="test-key-123")

    def test_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent.api_key == "test-key-123"
        assert agent.model == "claude-sonnet-4.5"
        assert len(agent.memory) == 0

    def test_decide_action_returns_valid_structure(self, agent):
        """Test decide_action returns expected dictionary structure."""
        observation = {"phase": "reconnaissance"}
        result = agent.decide_action(observation, [])

        assert "reasoning" in result
        assert "command" in result
        assert "expected_outcome" in result
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=orchestrator --cov-report=html

# Run specific test file
pytest tests/test_agents.py

# Run specific test
pytest tests/test_agents.py::TestRedTeamAgent::test_initialization
```

### Test Coverage

- Aim for 80%+ code coverage
- All new features must include tests
- Bug fixes should include regression tests

## Pull Request Process

### Before Submitting

1. **Update your fork**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run tests and linters**
   ```bash
   black orchestrator/ tests/
   ruff check orchestrator/ tests/
   pytest
   ```

3. **Update documentation** if needed

4. **Commit your changes** with clear messages

### Submitting a Pull Request

1. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create pull request** on GitHub

3. **Fill out the PR template** with:
   - Clear description of changes
   - Related issue numbers
   - Testing performed
   - Screenshots (if UI changes)

4. **Address review feedback** promptly

### PR Requirements

- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] Commit messages follow conventions
- [ ] No merge conflicts with main branch

## Creating Scenarios

Scenarios are the heart of Project Icarus. Here's how to create a new scenario:

### Scenario Structure

```python
# scenarios/my_scenario.py

class MyScenario:
    """
    Description of what this scenario tests.

    Difficulty: Easy/Medium/Hard
    Focus: Web/Network/API/System
    """

    name = "my_scenario"
    difficulty = "medium"

    def setup(self):
        """Set up the target environment."""
        # Configure vulnerable services
        # Create flag files
        # Set up initial state
        pass

    def get_objectives(self):
        """Return red team objectives."""
        return [
            "Identify running services",
            "Find vulnerability",
            "Gain shell access",
            "Escalate privileges",
            "Exfiltrate /root/flag.txt"
        ]

    def get_scoring_events(self):
        """Define custom scoring events."""
        return {
            "service_discovered": 15,
            "exploit_successful": 100,
            "flag_captured": 300
        }
```

### Scenario Guidelines

- Start simple, test thoroughly
- Document all vulnerabilities
- Include both easy and hard objectives
- Provide hints for educational scenarios
- Test with different AI models

## Documentation

### Documentation Standards

- Use clear, concise language
- Include code examples
- Add diagrams where helpful
- Keep documentation up-to-date with code changes

### Building Documentation

```bash
# Install documentation dependencies
pip install -r docs/requirements.txt

# Build documentation locally
cd docs
mkdocs serve

# View at http://localhost:8000
```

## Community

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and ideas
- **Discord** (coming soon): Real-time chat
- **Email**: security@project-icarus.dev (for security issues)

### Getting Help

- Check existing documentation
- Search closed issues
- Ask in GitHub Discussions
- Be patient and respectful

## Recognition

Contributors will be recognized in:
- `CONTRIBUTORS.md` file
- Release notes
- Project documentation

## Legal

By contributing, you agree that your contributions will be licensed under the GNU GPL v3 license.

### Security Disclosure

If you discover a security vulnerability:
1. **Do not** open a public issue
2. Email security@project-icarus.dev
3. Include detailed description
4. Wait for response before disclosure

## Questions?

Feel free to reach out:
- Open a GitHub Discussion
- Comment on relevant issues
- Tag maintainers with @mention

---

Thank you for contributing to Project Icarus! Together we're building something amazing.
