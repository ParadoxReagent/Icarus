#!/usr/bin/env python3
"""
Project Icarus - Interactive Launcher
Presents scenarios, builds containers, and launches the game with dashboard
"""

import os
import sys
import json
import subprocess
import webbrowser
import time
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header():
    """Print fancy header"""
    print(f"\n{Colors.CYAN}{'=' * 70}")
    print(f"{Colors.BOLD}⚔️  PROJECT ICARUS - AI Cyber Range Launcher{Colors.END}")
    print(f"{Colors.CYAN}    AI Red Team vs Blue Team Competition")
    print(f"{'=' * 70}{Colors.END}\n")


def load_scenarios():
    """Load scenarios from scenarios.json"""
    scenarios_file = Path(__file__).parent / "scenarios" / "scenarios.json"

    try:
        with open(scenarios_file, 'r') as f:
            data = json.load(f)
            return data.get('scenarios', [])
    except FileNotFoundError:
        print(f"{Colors.RED}Error: scenarios.json not found at {scenarios_file}{Colors.END}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"{Colors.RED}Error parsing scenarios.json: {e}{Colors.END}")
        sys.exit(1)


def print_scenarios(scenarios):
    """Display available scenarios"""
    print(f"{Colors.BOLD}Available Scenarios:{Colors.END}\n")

    for i, scenario in enumerate(scenarios, 1):
        difficulty_color = {
            'beginner': Colors.GREEN,
            'intermediate': Colors.YELLOW,
            'advanced': Colors.RED
        }.get(scenario['difficulty'], Colors.CYAN)

        print(f"{Colors.BOLD}{i}.{Colors.END} {Colors.CYAN}{scenario['name']}{Colors.END}")
        print(f"   Difficulty: {difficulty_color}{scenario['difficulty'].upper()}{Colors.END}")
        print(f"   Target: {scenario['target_container']}")
        print()


def print_scenario_details(scenario):
    """Print detailed information about a scenario"""
    print(f"\n{Colors.CYAN}{'─' * 70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.HEADER}Scenario Details:{Colors.END}\n")

    print(f"{Colors.BOLD}Name:{Colors.END} {scenario['name']}")
    print(f"{Colors.BOLD}ID:{Colors.END} {scenario['id']}")

    difficulty_color = {
        'beginner': Colors.GREEN,
        'intermediate': Colors.YELLOW,
        'advanced': Colors.RED
    }.get(scenario['difficulty'], Colors.CYAN)
    print(f"{Colors.BOLD}Difficulty:{Colors.END} {difficulty_color}{scenario['difficulty'].upper()}{Colors.END}")

    print(f"\n{Colors.BOLD}Description:{Colors.END}")
    print(f"  {scenario['description']}")

    print(f"\n{Colors.BOLD}Vulnerabilities:{Colors.END}")
    for vuln in scenario.get('vulnerabilities', []):
        print(f"  • {vuln}")

    print(f"\n{Colors.BOLD}Red Team Objectives:{Colors.END}")
    for obj in scenario.get('objectives', {}).get('red_team', []):
        print(f"  🔴 {obj}")

    print(f"\n{Colors.BOLD}Blue Team Objectives:{Colors.END}")
    for obj in scenario.get('objectives', {}).get('blue_team', []):
        print(f"  🔵 {obj}")

    print(f"\n{Colors.BOLD}Flag Location:{Colors.END} {scenario.get('flag_location', 'N/A')}")
    print(f"{Colors.BOLD}Estimated Rounds:{Colors.END} {scenario.get('estimated_rounds', 30)}")
    print(f"{Colors.CYAN}{'─' * 70}{Colors.END}\n")


def check_env_file():
    """Check if .env file exists and has API key"""
    env_file = Path(__file__).parent / ".env"

    if not env_file.exists():
        print(f"{Colors.YELLOW}⚠️  Warning: .env file not found!{Colors.END}")
        print(f"\n{Colors.BOLD}Creating .env from .env.example...{Colors.END}")

        example_file = Path(__file__).parent / ".env.example"
        if example_file.exists():
            subprocess.run(["cp", str(example_file), str(env_file)], check=True)
            print(f"{Colors.GREEN}✓ Created .env file{Colors.END}")
        else:
            print(f"{Colors.RED}Error: .env.example not found!{Colors.END}")
            return False

    # Check for API key
    with open(env_file, 'r') as f:
        content = f.read()
        if 'sk-ant-your-key-here' in content or 'ANTHROPIC_API_KEY=' not in content:
            print(f"\n{Colors.RED}⚠️  ANTHROPIC_API_KEY not configured!{Colors.END}")
            print(f"{Colors.YELLOW}Please edit .env and add your Anthropic API key:{Colors.END}")
            print(f"  {Colors.CYAN}ANTHROPIC_API_KEY=sk-ant-your-actual-key{Colors.END}\n")

            choice = input(f"Continue anyway? (y/n): ").strip().lower()
            if choice != 'y':
                return False

    return True


def get_profile_for_scenario(scenario_id):
    """Get docker-compose profile for scenario"""
    profile_map = {
        'dvwa_basic_pentest': 'default',
        'network_services_exploit': 'scenario2',
        'api_security_test': 'scenario3'
    }
    return profile_map.get(scenario_id, 'default')


def build_containers(scenario_id, profile):
    """Build Docker containers for the scenario"""
    print(f"\n{Colors.CYAN}{'─' * 70}{Colors.END}")
    print(f"{Colors.BOLD}🔨 Building Docker containers...{Colors.END}\n")

    cmd = ["docker-compose", "build"]
    if profile != 'default':
        cmd.extend(["--profile", profile])

    try:
        subprocess.run(cmd, check=True, cwd=Path(__file__).parent)
        print(f"\n{Colors.GREEN}✓ Containers built successfully!{Colors.END}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n{Colors.RED}✗ Build failed: {e}{Colors.END}")
        return False


def start_game(scenario_id, profile):
    """Start the game with docker-compose"""
    print(f"\n{Colors.CYAN}{'─' * 70}{Colors.END}")
    print(f"{Colors.BOLD}🚀 Starting Project Icarus...{Colors.END}\n")

    # Set environment variable for scenario
    env = os.environ.copy()
    env['SCENARIO_ID'] = scenario_id

    cmd = ["docker-compose"]
    if profile != 'default':
        cmd.extend(["--profile", profile])
    cmd.append("up")

    print(f"{Colors.CYAN}Running: {' '.join(cmd)}{Colors.END}")
    print(f"{Colors.CYAN}Scenario: {scenario_id}{Colors.END}\n")

    print(f"{Colors.YELLOW}⏳ Starting containers (this may take a minute)...{Colors.END}\n")

    try:
        # Start in background
        process = subprocess.Popen(
            cmd,
            env=env,
            cwd=Path(__file__).parent,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )

        # Wait a bit and show initial logs
        time.sleep(3)

        print(f"{Colors.GREEN}✓ Containers starting...{Colors.END}\n")
        print(f"{Colors.BOLD}Dashboard will be available at:{Colors.END}")
        print(f"  {Colors.CYAN}http://localhost:3000{Colors.END}\n")

        # Ask if they want to open browser
        print(f"{Colors.BOLD}Opening dashboard in browser...{Colors.END}")
        time.sleep(5)  # Wait for services to start

        try:
            webbrowser.open('http://localhost:3000')
            print(f"{Colors.GREEN}✓ Dashboard opened in browser{Colors.END}\n")
        except Exception as e:
            print(f"{Colors.YELLOW}Could not open browser automatically: {e}{Colors.END}")
            print(f"Please open {Colors.CYAN}http://localhost:3000{Colors.END} manually\n")

        print(f"{Colors.BOLD}Game is now running!{Colors.END}")
        print(f"\n{Colors.YELLOW}Monitoring logs (Press Ctrl+C to stop):{Colors.END}\n")
        print(f"{Colors.CYAN}{'─' * 70}{Colors.END}\n")

        # Follow logs
        for line in process.stdout:
            print(line, end='')

        process.wait()

    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️  Interrupted by user{Colors.END}")
        print(f"{Colors.BOLD}Stopping containers...{Colors.END}")
        subprocess.run(["docker-compose", "down"], cwd=Path(__file__).parent)
        print(f"{Colors.GREEN}✓ Stopped{Colors.END}\n")
    except Exception as e:
        print(f"\n{Colors.RED}Error starting game: {e}{Colors.END}")
        return False

    return True


def main():
    """Main launcher function"""
    print_header()

    # Check environment
    if not check_env_file():
        print(f"\n{Colors.RED}Setup incomplete. Please configure .env and try again.{Colors.END}\n")
        sys.exit(1)

    # Load scenarios
    scenarios = load_scenarios()
    if not scenarios:
        print(f"{Colors.RED}No scenarios found!{Colors.END}")
        sys.exit(1)

    # Display scenarios
    print_scenarios(scenarios)

    # Get user selection
    while True:
        try:
            choice = input(f"{Colors.BOLD}Select a scenario (1-{len(scenarios)}) or 'q' to quit: {Colors.END}").strip()

            if choice.lower() == 'q':
                print(f"\n{Colors.CYAN}Goodbye!{Colors.END}\n")
                sys.exit(0)

            choice_num = int(choice)
            if 1 <= choice_num <= len(scenarios):
                break
            else:
                print(f"{Colors.RED}Invalid choice. Please enter 1-{len(scenarios)}{Colors.END}\n")
        except ValueError:
            print(f"{Colors.RED}Invalid input. Please enter a number or 'q'{Colors.END}\n")

    selected_scenario = scenarios[choice_num - 1]

    # Show scenario details
    print_scenario_details(selected_scenario)

    # Confirm selection
    confirm = input(f"{Colors.BOLD}Start this scenario? (y/n): {Colors.END}").strip().lower()
    if confirm != 'y':
        print(f"\n{Colors.YELLOW}Cancelled. Run the script again to choose a different scenario.{Colors.END}\n")
        sys.exit(0)

    # Get profile
    scenario_id = selected_scenario['id']
    profile = get_profile_for_scenario(scenario_id)

    # Ask about building
    print(f"\n{Colors.BOLD}Build containers?{Colors.END}")
    print(f"  {Colors.GREEN}y{Colors.END} - Build containers (recommended for first run or after changes)")
    print(f"  {Colors.YELLOW}n{Colors.END} - Skip build (faster if already built)")

    build = input(f"\n{Colors.BOLD}Build? (y/n): {Colors.END}").strip().lower()

    if build == 'y':
        if not build_containers(scenario_id, profile):
            print(f"\n{Colors.RED}Build failed. Cannot continue.{Colors.END}\n")
            sys.exit(1)

    # Start the game
    start_game(scenario_id, profile)

    print(f"\n{Colors.GREEN}Thank you for using Project Icarus!{Colors.END}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Interrupted{Colors.END}\n")
        sys.exit(0)
