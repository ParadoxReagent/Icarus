"""
Scenario Manager for Project Icarus
Handles dynamic loading and configuration of game scenarios
"""

import json
import logging
from typing import Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class ScenarioManager:
    """Manages game scenarios and their configurations"""

    def __init__(self, scenarios_file: str = "/app/../scenarios/scenarios.json"):
        """
        Initialize scenario manager

        Args:
            scenarios_file: Path to scenarios configuration file
        """
        self.scenarios_file = scenarios_file
        self.scenarios = {}
        self.load_scenarios()

    def load_scenarios(self):
        """Load scenarios from JSON configuration file"""
        try:
            # Try multiple possible paths
            possible_paths = [
                self.scenarios_file,
                "/app/scenarios/scenarios.json",
                "scenarios/scenarios.json",
                "../scenarios/scenarios.json"
            ]

            scenarios_data = None
            for path in possible_paths:
                try:
                    with open(path, 'r') as f:
                        scenarios_data = json.load(f)
                        logger.info(f"Loaded scenarios from {path}")
                        break
                except FileNotFoundError:
                    continue

            if not scenarios_data:
                logger.warning("No scenarios file found, using default")
                self._load_default_scenarios()
                return

            for scenario in scenarios_data.get("scenarios", []):
                self.scenarios[scenario["id"]] = scenario

            logger.info(f"Loaded {len(self.scenarios)} scenarios")

        except Exception as e:
            logger.error(f"Failed to load scenarios: {e}")
            self._load_default_scenarios()

    def _load_default_scenarios(self):
        """Load default DVWA scenario if file not found"""
        self.scenarios = {
            "dvwa_basic_pentest": {
                "id": "dvwa_basic_pentest",
                "name": "DVWA Basic Web Application Pentest",
                "description": "Target a vulnerable web application",
                "difficulty": "beginner",
                "target_container": "blue-target",
                "flag_location": "/root/flag.txt",
                "estimated_rounds": 30,
                "vulnerabilities": [
                    "SQL injection",
                    "Weak SSH credentials",
                    "Directory traversal"
                ]
            }
        }

    def get_scenario(self, scenario_id: str) -> Optional[Dict]:
        """
        Get scenario configuration by ID

        Args:
            scenario_id: Scenario identifier

        Returns:
            Scenario configuration dict or None
        """
        return self.scenarios.get(scenario_id)

    def list_scenarios(self) -> List[Dict]:
        """
        List all available scenarios

        Returns:
            List of scenario configurations
        """
        return list(self.scenarios.values())

    def get_scenario_info(self, scenario_id: str) -> str:
        """
        Get formatted scenario information

        Args:
            scenario_id: Scenario identifier

        Returns:
            Formatted scenario description
        """
        scenario = self.get_scenario(scenario_id)
        if not scenario:
            return f"Scenario '{scenario_id}' not found"

        info = f"""
Scenario: {scenario['name']}
ID: {scenario['id']}
Difficulty: {scenario['difficulty']}
Target Container: {scenario['target_container']}
Estimated Rounds: {scenario['estimated_rounds']}

Description:
{scenario['description']}

Vulnerabilities:
{chr(10).join(f"  - {v}" for v in scenario.get('vulnerabilities', []))}

Flag Location: {scenario.get('flag_location', 'Not specified')}
"""
        return info

    def get_target_container(self, scenario_id: str) -> str:
        """
        Get target container name for scenario

        Args:
            scenario_id: Scenario identifier

        Returns:
            Container name
        """
        scenario = self.get_scenario(scenario_id)
        if scenario:
            return scenario.get('target_container', 'blue-target')
        return 'blue-target'

    def get_flag_location(self, scenario_id: str) -> str:
        """
        Get flag file location for scenario

        Args:
            scenario_id: Scenario identifier

        Returns:
            Flag file path
        """
        scenario = self.get_scenario(scenario_id)
        if scenario:
            return scenario.get('flag_location', '/root/flag.txt')
        return '/root/flag.txt'

    def get_estimated_rounds(self, scenario_id: str) -> int:
        """
        Get estimated rounds for scenario

        Args:
            scenario_id: Scenario identifier

        Returns:
            Number of estimated rounds
        """
        scenario = self.get_scenario(scenario_id)
        if scenario:
            return scenario.get('estimated_rounds', 30)
        return 30

    def validate_scenario(self, scenario_id: str) -> tuple[bool, str]:
        """
        Validate that a scenario exists and is properly configured

        Args:
            scenario_id: Scenario identifier

        Returns:
            Tuple of (is_valid, error_message)
        """
        scenario = self.get_scenario(scenario_id)

        if not scenario:
            return False, f"Scenario '{scenario_id}' not found"

        required_fields = ['id', 'name', 'target_container']
        for field in required_fields:
            if field not in scenario:
                return False, f"Scenario missing required field: {field}"

        return True, "Scenario is valid"
