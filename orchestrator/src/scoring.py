"""
Scoring and Event Detection System for Project Icarus
Detects achievements and awards points based on game actions
"""

import logging
import re
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


class ScoringSystem:
    """Detects events and awards points"""

    # Red Team Point Values
    RED_TEAM_SCORES = {
        'port_scan_complete': 10,
        'service_identified': 15,
        'vulnerability_found': 25,
        'credentials_obtained': 50,
        'shell_access_gained': 100,
        'privilege_escalation': 150,
        'persistence_established': 200,
        'data_exfiltration': 300,
    }

    # Blue Team Point Values
    BLUE_TEAM_SCORES = {
        'attack_detected': 25,
        'attack_blocked': 50,
        'attacker_ip_banned': 75,
        'vulnerability_patched': 100,
        'service_maintained': 10,
        'forensics_complete': 150,
        'recovery_complete': 200,
    }

    # Penalties
    PENALTIES = {
        'service_down': -50,
        'detected_by_blue': -25,
        'false_positive_alert': -10,
        'command_timeout': -5,
        'invalid_command': -10,
    }

    def __init__(self):
        """Initialize scoring system"""
        self.detected_events = []

    def evaluate_round(
        self,
        round_id: str,
        red_result: Dict,
        blue_result: Dict
    ) -> List[Tuple[str, str, int, str]]:
        """
        Evaluate round outcomes and identify point-worthy events

        Args:
            round_id: Round UUID
            red_result: Red team action result
            blue_result: Blue team action result

        Returns:
            List of tuples: (team, event_type, points, description)
        """
        events = []

        # Evaluate red team achievements
        events.extend(self._evaluate_red_team(red_result))

        # Evaluate blue team achievements
        events.extend(self._evaluate_blue_team(blue_result))

        # Check for interactions (e.g., blue detecting red)
        events.extend(self._evaluate_interactions(red_result, blue_result))

        return events

    def _evaluate_red_team(self, result: Dict) -> List[Tuple[str, str, int, str]]:
        """
        Evaluate red team actions for achievements

        Args:
            result: Red team action result

        Returns:
            List of events
        """
        events = []
        action = result.get('action', '').lower()
        stdout = result.get('result', '').lower()
        success = result.get('success', False)

        if not success:
            return events

        # Port scan completed
        if 'nmap' in action and ('open' in stdout or 'closed' in stdout):
            events.append(('red', 'port_scan_complete', self.RED_TEAM_SCORES['port_scan_complete'],
                          'Red team completed port scan'))

        # Service identification
        if any(keyword in stdout for keyword in ['ssh', 'http', 'mysql', 'version', 'apache']):
            if 'nmap' in action or 'curl' in action:
                events.append(('red', 'service_identified', self.RED_TEAM_SCORES['service_identified'],
                              'Red team identified service'))

        # Vulnerability found
        if any(keyword in stdout for keyword in ['vulnerable', 'exploit', 'cve', 'weakness']):
            events.append(('red', 'vulnerability_found', self.RED_TEAM_SCORES['vulnerability_found'],
                          'Red team found vulnerability'))

        # Credentials obtained
        if any(keyword in stdout for keyword in ['password', 'credential', 'username', 'login success']):
            events.append(('red', 'credentials_obtained', self.RED_TEAM_SCORES['credentials_obtained'],
                          'Red team obtained credentials'))

        # Shell access gained
        if any(keyword in stdout for keyword in ['shell', '$', '#', 'bash', 'sh-', 'connected to']):
            if 'ssh' in action or 'nc' in action or 'exploit' in action:
                events.append(('red', 'shell_access_gained', self.RED_TEAM_SCORES['shell_access_gained'],
                              'Red team gained shell access'))

        # Privilege escalation
        if any(keyword in stdout for keyword in ['root@', 'uid=0', 'euid=0']):
            events.append(('red', 'privilege_escalation', self.RED_TEAM_SCORES['privilege_escalation'],
                          'Red team escalated to root'))

        # Data exfiltration (flag file)
        if 'flag' in stdout or 'icarus{' in stdout.lower():
            events.append(('red', 'data_exfiltration', self.RED_TEAM_SCORES['data_exfiltration'],
                          'Red team exfiltrated flag data'))

        return events

    def _evaluate_blue_team(self, result: Dict) -> List[Tuple[str, str, int, str]]:
        """
        Evaluate blue team actions for achievements

        Args:
            result: Blue team action result

        Returns:
            List of events
        """
        events = []
        action = result.get('action', '').lower()
        stdout = result.get('result', '').lower()
        success = result.get('success', False)
        reasoning = result.get('reasoning', '').lower()

        # Attack detected (based on reasoning)
        if any(keyword in reasoning for keyword in ['attack', 'suspicious', 'malicious', 'threat']):
            if 'detected' in reasoning or 'found' in reasoning:
                events.append(('blue', 'attack_detected', self.BLUE_TEAM_SCORES['attack_detected'],
                              'Blue team detected attack'))

        # Attack blocked
        if 'iptables' in action and '-j drop' in action and success:
            events.append(('blue', 'attack_blocked', self.BLUE_TEAM_SCORES['attack_blocked'],
                          'Blue team blocked attack'))

        # Attacker IP banned
        if 'iptables' in action and success and ('-a input' in action or '-i input' in action):
            events.append(('blue', 'attacker_ip_banned', self.BLUE_TEAM_SCORES['attacker_ip_banned'],
                          'Blue team banned attacker IP'))

        # Service maintained (if action is monitoring and services are up)
        if action == 'none' or 'status' in action or 'ps' in action:
            events.append(('blue', 'service_maintained', self.BLUE_TEAM_SCORES['service_maintained'],
                          'Blue team maintained services'))

        # Check for false positives
        if 'iptables' in action and success:
            # If blue team blocks but no actual attack indicators, it's a false positive
            # This is simplified; in production, you'd cross-reference with red team actions
            if 'no evidence' in reasoning or 'precaution' in reasoning:
                events.append(('blue', 'false_positive_alert', self.PENALTIES['false_positive_alert'],
                              'Blue team false positive'))

        return events

    def _evaluate_interactions(self, red_result: Dict, blue_result: Dict) -> List[Tuple[str, str, int, str]]:
        """
        Evaluate interactions between teams

        Args:
            red_result: Red team result
            blue_result: Blue team result

        Returns:
            List of events
        """
        events = []

        # Check if blue team detected red team
        blue_reasoning = blue_result.get('reasoning', '').lower()
        red_action = red_result.get('action', '').lower()

        # If blue team mentions specific red team activity
        if any(keyword in blue_reasoning for keyword in ['nmap', 'scan', 'probe', 'brute force', 'injection']):
            # Blue team detected red team activity
            events.append(('blue', 'attack_detected', self.BLUE_TEAM_SCORES['attack_detected'],
                          'Blue team detected red team activity'))

            # Red team gets penalty for being detected
            events.append(('red', 'detected_by_blue', self.PENALTIES['detected_by_blue'],
                          'Red team was detected'))

        # Check if services went down
        blue_stdout = blue_result.get('result', '').lower()
        if any(keyword in blue_stdout for keyword in ['stopped', 'dead', 'failed', 'inactive']):
            if 'service' in blue_result.get('action', ''):
                events.append(('blue', 'service_down', self.PENALTIES['service_down'],
                              'Service went down'))

        return events

    def get_current_phase(self, round_number: int) -> str:
        """
        Determine game phase based on round number

        Args:
            round_number: Current round

        Returns:
            Phase name
        """
        if round_number <= 5:
            return 'reconnaissance'
        elif round_number <= 15:
            return 'initial_access'
        elif round_number <= 25:
            return 'privilege_escalation'
        else:
            return 'exfiltration'

    def check_win_conditions(self, red_events: List[str], blue_events: List[str], round_number: int, max_rounds: int) -> Tuple[bool, Optional[str]]:
        """
        Check if game should end

        Args:
            red_events: List of red team event types
            blue_events: List of blue team event types
            round_number: Current round number
            max_rounds: Maximum rounds

        Returns:
            Tuple of (game_over, winner)
        """
        # Red team wins if they exfiltrate data
        if 'data_exfiltration' in red_events:
            return (True, 'red')

        # Game ends at max rounds
        if round_number >= max_rounds:
            return (True, None)  # Will determine winner by score

        return (False, None)
