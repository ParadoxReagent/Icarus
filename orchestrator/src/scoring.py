"""
Scoring and Event Detection System for Project Icarus
Detects achievements and awards points based on game actions
"""

import logging
import re
import json
from typing import Dict, List, Tuple, Optional

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
        reasoning = result.get('reasoning', '')

        if not success:
            return events

        # Port scan completed - extract specific ports found
        if 'nmap' in action and ('open' in stdout or 'closed' in stdout):
            # Extract open ports from nmap output
            open_ports = re.findall(r'(\d+)/tcp\s+open\s+(\w+)', stdout)
            if open_ports:
                port_details = ', '.join([f"{port}/{service}" for port, service in open_ports[:5]])
                description = f"Red team completed port scan - Found open ports: {port_details}"
                if len(open_ports) > 5:
                    description += f" and {len(open_ports) - 5} more"
            else:
                # Extract target IP if available
                target_match = re.search(r'(?:nmap|scan)\s+[\w\-]*\s*([\d\.]+)', action)
                target = target_match.group(1) if target_match else "target"
                description = f"Red team scanned {target} - Scan completed but ports info not in standard format"

            events.append(('red', 'port_scan_complete', self.RED_TEAM_SCORES['port_scan_complete'],
                          description))

        # Service identification - be specific about what was found
        service_keywords = {
            'ssh': 'SSH', 'http': 'HTTP', 'https': 'HTTPS',
            'mysql': 'MySQL', 'apache': 'Apache', 'nginx': 'Nginx',
            'ftp': 'FTP', 'smtp': 'SMTP', 'telnet': 'Telnet'
        }
        found_services = [name for keyword, name in service_keywords.items() if keyword in stdout]

        if found_services and ('nmap' in action or 'curl' in action or 'wget' in action):
            # Extract version info if available
            version_match = re.search(r'version\s+([\d\.]+)', stdout) or re.search(r'([\d\.]+)', stdout)
            version_info = f" version {version_match.group(1)}" if version_match else ""

            services_str = ', '.join(found_services[:3])
            description = f"Red team identified services: {services_str}{version_info}"

            events.append(('red', 'service_identified', self.RED_TEAM_SCORES['service_identified'],
                          description))

        # Vulnerability found - extract specific vulnerability info
        if any(keyword in stdout for keyword in ['vulnerable', 'exploit', 'cve', 'weakness']):
            # Try to extract CVE or vulnerability name
            cve_match = re.search(r'(CVE-\d{4}-\d+)', stdout, re.IGNORECASE)
            vuln_match = re.search(r'(?:vulnerable to|exploit|weakness):\s*([^\n]+)', stdout, re.IGNORECASE)

            if cve_match:
                description = f"Red team found vulnerability: {cve_match.group(1)}"
            elif vuln_match:
                vuln_desc = vuln_match.group(1)[:100]
                description = f"Red team found vulnerability: {vuln_desc}"
            else:
                description = f"Red team discovered potential vulnerability using {action.split()[0]}"

            events.append(('red', 'vulnerability_found', self.RED_TEAM_SCORES['vulnerability_found'],
                          description))

        # Credentials obtained - extract username if possible
        if any(keyword in stdout for keyword in ['password', 'credential', 'username', 'login success']):
            user_match = re.search(r'(?:user|username|login)[:\s]+([^\s\n]+)', stdout, re.IGNORECASE)
            password_match = re.search(r'(?:password|pass)[:\s]+([^\s\n]+)', stdout, re.IGNORECASE)

            if user_match and password_match:
                description = f"Red team obtained credentials - User: {user_match.group(1)}, Password: {'*' * len(password_match.group(1))}"
            elif user_match:
                description = f"Red team obtained credentials for user: {user_match.group(1)}"
            else:
                # Check if it's from brute force
                if 'hydra' in action:
                    description = f"Red team brute-forced credentials using Hydra"
                elif 'sqlmap' in action:
                    description = f"Red team extracted credentials via SQL injection"
                else:
                    description = f"Red team obtained valid credentials"

            events.append(('red', 'credentials_obtained', self.RED_TEAM_SCORES['credentials_obtained'],
                          description))

        # Shell access gained - specify the method
        if any(keyword in stdout for keyword in ['shell', '$', '#', 'bash', 'sh-', 'connected to']):
            if 'ssh' in action:
                user_match = re.search(r'ssh\s+(?:[\w\-]+@)?([\w\-]+)@', action)
                target_match = re.search(r'ssh\s+[^\s]*\s*([\d\.]+)', action)
                user = user_match.group(1) if user_match else "user"
                target = target_match.group(1) if target_match else "target"
                description = f"Red team gained SSH shell access as '{user}' on {target}"
            elif 'nc' in action:
                port_match = re.search(r'nc\s+[\d\.]+\s+(\d+)', action)
                port = port_match.group(1) if port_match else "unknown port"
                description = f"Red team established netcat reverse shell on port {port}"
            elif 'exploit' in action:
                description = f"Red team gained shell access via exploit execution"
            else:
                description = f"Red team obtained shell access on target system"

            events.append(('red', 'shell_access_gained', self.RED_TEAM_SCORES['shell_access_gained'],
                          description))

        # Privilege escalation - specify method if possible
        if any(keyword in stdout for keyword in ['root@', 'uid=0', 'euid=0']):
            method = "unknown method"
            if 'sudo' in action:
                method = "sudo exploit"
            elif 'su' in action:
                method = "su command"
            elif 'exploit' in action:
                method = "kernel/privilege exploit"
            elif 'suid' in action or 'chmod' in action:
                method = "SUID binary abuse"

            description = f"Red team escalated privileges to root via {method}"
            events.append(('red', 'privilege_escalation', self.RED_TEAM_SCORES['privilege_escalation'],
                          description))

        # Data exfiltration (flag file) - show what was exfiltrated
        if 'flag' in stdout or 'icarus{' in stdout.lower():
            flag_match = re.search(r'(icarus\{[^}]+\})', stdout, re.IGNORECASE)
            if flag_match:
                description = f"Red team exfiltrated flag: {flag_match.group(1)}"
            else:
                file_match = re.search(r'cat\s+([^\s]+flag[^\s]*)', action)
                filename = file_match.group(1) if file_match else "/root/flag.txt"
                description = f"Red team successfully exfiltrated sensitive data from {filename}"

            events.append(('red', 'data_exfiltration', self.RED_TEAM_SCORES['data_exfiltration'],
                          description))

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
        observation = result.get('observation', '')

        # Attack detected (based on reasoning) - extract specific indicators
        if any(keyword in reasoning for keyword in ['attack', 'suspicious', 'malicious', 'threat']):
            if 'detected' in reasoning or 'found' in reasoning:
                # Identify what type of attack was detected
                attack_type = "unknown attack"
                indicators = []

                if 'nmap' in reasoning or 'port scan' in reasoning or 'scanning' in reasoning:
                    attack_type = "port scanning activity"
                    # Try to extract connection count
                    conn_match = re.search(r'(\d+)\s+connection', reasoning)
                    if conn_match:
                        indicators.append(f"{conn_match.group(1)} connections")
                elif 'brute' in reasoning or 'failed password' in reasoning or 'failed login' in reasoning:
                    attack_type = "brute force authentication attempts"
                    # Extract failed attempt count
                    fail_match = re.search(r'(\d+)\s+failed', reasoning)
                    if fail_match:
                        indicators.append(f"{fail_match.group(1)} failed attempts")
                elif 'sql injection' in reasoning or 'sqlmap' in reasoning:
                    attack_type = "SQL injection attack"
                elif 'nikto' in reasoning or 'web scanner' in reasoning:
                    attack_type = "web vulnerability scanning"
                elif 'exploit' in reasoning:
                    attack_type = "exploitation attempt"

                # Extract IP if mentioned
                ip_match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', reasoning)
                if ip_match:
                    indicators.append(f"from IP {ip_match.group(1)}")

                # Build detailed description
                if indicators:
                    description = f"Blue team detected {attack_type}: {', '.join(indicators)}"
                else:
                    description = f"Blue team detected {attack_type}"

                events.append(('blue', 'attack_detected', self.BLUE_TEAM_SCORES['attack_detected'],
                              description))

        # Attack blocked - extract details about what was blocked
        if 'iptables' in action and '-j drop' in action and success:
            # Extract the IP being blocked
            ip_match = re.search(r'-s\s+([\d\.]+)', action)
            blocked_ip = ip_match.group(1) if ip_match else "attacker IP"

            # Determine reason from reasoning
            reason = "malicious activity"
            if 'scan' in reasoning:
                reason = "port scanning"
            elif 'brute' in reasoning:
                reason = "brute force attempts"
            elif 'sql' in reasoning:
                reason = "SQL injection"
            elif 'exploit' in reasoning:
                reason = "exploitation attempts"

            description = f"Blue team blocked {blocked_ip} due to {reason}"
            events.append(('blue', 'attack_blocked', self.BLUE_TEAM_SCORES['attack_blocked'],
                          description))

        # Attacker IP banned - provide details
        if 'iptables' in action and success and ('-a input' in action or '-i input' in action):
            ip_match = re.search(r'-s\s+([\d\.]+)', action)
            banned_ip = ip_match.group(1) if ip_match else "attacker IP"

            # Extract threat level from reasoning
            threat_level = "medium"
            if 'critical' in reasoning or 'high' in reasoning:
                threat_level = "high"
            elif 'low' in reasoning:
                threat_level = "low"

            description = f"Blue team banned {banned_ip} (threat level: {threat_level})"
            events.append(('blue', 'attacker_ip_banned', self.BLUE_TEAM_SCORES['attacker_ip_banned'],
                          description))

        # Service maintained - be specific about what's being maintained
        if action == 'none' or 'status' in action or 'ps' in action:
            # Extract info from observation/telemetry
            services_status = []

            # Parse observation if available
            if observation:
                try:
                    obs_dict = json.loads(observation) if isinstance(observation, str) else observation
                    # Check for active services
                    if 'active_connections' in obs_dict:
                        services_status.append(f"{obs_dict['active_connections']} active connections")
                    if 'process_count' in obs_dict:
                        services_status.append(f"{obs_dict['process_count']} processes running")
                except:
                    pass

            # Check if monitoring logs
            if 'grep' in action or 'tail' in action or 'log' in action:
                log_type = "system logs"
                if 'auth' in action:
                    log_type = "authentication logs"
                elif 'apache' in action or 'access' in action:
                    log_type = "web access logs"
                description = f"Blue team monitoring {log_type}"
            elif services_status:
                description = f"Blue team maintaining services: {', '.join(services_status)}"
            elif 'apache' in reasoning or 'web' in reasoning:
                description = f"Blue team maintained web services (Apache running)"
            elif 'ssh' in reasoning:
                description = f"Blue team maintained SSH service"
            else:
                description = f"Blue team performed routine system monitoring"

            events.append(('blue', 'service_maintained', self.BLUE_TEAM_SCORES['service_maintained'],
                          description))

        # Check for false positives
        if 'iptables' in action and success:
            # If blue team blocks but no actual attack indicators, it's a false positive
            # This is simplified; in production, you'd cross-reference with red team actions
            if 'no evidence' in reasoning or 'precaution' in reasoning:
                ip_match = re.search(r'-s\s+([\d\.]+)', action)
                blocked_ip = ip_match.group(1) if ip_match else "IP"
                description = f"Blue team false positive: blocked {blocked_ip} without sufficient evidence"
                events.append(('blue', 'false_positive_alert', self.PENALTIES['false_positive_alert'],
                              description))

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
        detected_activity = None
        if 'nmap' in blue_reasoning or 'port scan' in blue_reasoning or 'scanning' in blue_reasoning:
            detected_activity = "port scanning"
        elif 'brute force' in blue_reasoning or 'password attack' in blue_reasoning:
            detected_activity = "brute force attack"
        elif 'sql injection' in blue_reasoning or 'sqlmap' in blue_reasoning:
            detected_activity = "SQL injection"
        elif 'nikto' in blue_reasoning or 'web scan' in blue_reasoning:
            detected_activity = "web vulnerability scanning"
        elif 'exploit' in blue_reasoning:
            detected_activity = "exploitation attempt"
        elif any(keyword in blue_reasoning for keyword in ['probe', 'suspicious connection']):
            detected_activity = "suspicious network activity"

        if detected_activity:
            # Extract what red team was actually doing
            red_tool = "unknown tool"
            if 'nmap' in red_action:
                red_tool = "nmap"
            elif 'hydra' in red_action:
                red_tool = "Hydra"
            elif 'sqlmap' in red_action:
                red_tool = "sqlmap"
            elif 'nikto' in red_action:
                red_tool = "Nikto"
            elif 'curl' in red_action:
                red_tool = "curl"

            # Blue team detected red team activity
            events.append(('blue', 'attack_detected', self.BLUE_TEAM_SCORES['attack_detected'],
                          f"Blue team detected {detected_activity} (Red team using {red_tool})"))

            # Red team gets penalty for being detected
            events.append(('red', 'detected_by_blue', self.PENALTIES['detected_by_blue'],
                          f"Red team's {detected_activity} was detected by blue team"))

        # Check if services went down
        blue_stdout = blue_result.get('result', '').lower()
        blue_action = blue_result.get('action', '').lower()

        if any(keyword in blue_stdout for keyword in ['stopped', 'dead', 'failed', 'inactive']):
            # Identify which service went down
            service_name = "unknown service"
            if 'apache' in blue_stdout or 'httpd' in blue_stdout:
                service_name = "Apache web server"
            elif 'ssh' in blue_stdout or 'sshd' in blue_stdout:
                service_name = "SSH service"
            elif 'mysql' in blue_stdout or 'mariadb' in blue_stdout:
                service_name = "MySQL database"
            elif 'ftp' in blue_stdout:
                service_name = "FTP service"

            # Check if it was intentional (blue team stopped it) or accidental
            if 'stop' in blue_action or 'kill' in blue_action:
                description = f"Blue team intentionally stopped {service_name} (security measure)"
            else:
                description = f"{service_name} went down unexpectedly"

            events.append(('blue', 'service_down', self.PENALTIES['service_down'],
                          description))

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
