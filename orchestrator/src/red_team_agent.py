"""
Red Team AI Agent for Project Icarus
AI-controlled penetration testing agent using Claude API
"""

import logging
import json
from typing import Dict, List, Optional
from datetime import datetime
from anthropic import Anthropic

logger = logging.getLogger(__name__)


class RedTeamAgent:
    """AI-controlled penetration testing agent"""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-5-20250929"):
        """
        Initialize Red Team agent

        Args:
            api_key: Anthropic API key
            model: Claude model to use
        """
        self.api_key = api_key
        self.model = model
        self.client = Anthropic(api_key=api_key)
        self.memory = []
        self.current_phase = "reconnaissance"
        self.access_level = "external"
        self.discovered_info = {}

    def observe_environment(self) -> Dict:
        """
        Gather current state information

        Returns:
            Observation dict for AI context
        """
        return {
            "phase": self.current_phase,
            "access_level": self.access_level,
            "available_tools": [
                "nmap - network scanning",
                "curl - web requests",
                "wget - download files",
                "nc - netcat for connections",
                "nikto - web vulnerability scanner",
                "sqlmap - SQL injection tool",
                "hydra - password cracker",
                "ssh - secure shell client"
            ],
            "discovered_services": self.discovered_info.get("services", []),
            "target_ip": "172.20.0.10"
        }

    def decide_action(self, observation: Dict, history: List[Dict]) -> Dict:
        """
        Use Claude API to decide next action

        Args:
            observation: Current environment observation
            history: Recent action history

        Returns:
            Decision dict with reasoning and command
        """
        prompt = self._build_decision_prompt(observation, history)

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.7,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Extract text content
            response_text = response.content[0].text

            # Parse JSON response
            decision = json.loads(response_text)

            # Update internal state
            self._update_state(decision)

            return decision

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response: {e}")
            logger.error(f"Response was: {response_text}")
            # Return safe fallback
            return {
                "reasoning": "Failed to parse AI response, falling back to safe command",
                "command": "echo 'Error in AI decision making'",
                "expected_outcome": "Error recovery",
                "phase": self.current_phase
            }
        except Exception as e:
            logger.error(f"AI decision error: {e}")
            return {
                "reasoning": f"Error: {str(e)}",
                "command": "echo 'AI error'",
                "expected_outcome": "Error state",
                "phase": self.current_phase
            }

    def _build_decision_prompt(self, observation: Dict, history: List[Dict]) -> str:
        """
        Construct detailed prompt for Claude API

        Args:
            observation: Current state
            history: Recent history

        Returns:
            Formatted prompt string
        """
        history_text = self._format_history(history[-5:]) if history else "No previous attempts yet."

        return f"""You are an AI penetration tester with access to a Kali Linux system.
Your goal is to gain root access to the target system and exfiltrate sensitive data.

CURRENT PHASE: {observation['phase']}
ACCESS LEVEL: {observation['access_level']}
TARGET IP: {observation['target_ip']}

AVAILABLE TOOLS:
{chr(10).join(f"- {tool}" for tool in observation['available_tools'])}

DISCOVERED INFORMATION:
{json.dumps(observation.get('discovered_services', []), indent=2)}

RECENT HISTORY (last 5 attempts):
{history_text}

MISSION OBJECTIVES (in order):
1. Reconnaissance: Identify services and vulnerabilities (scan ports, identify versions)
2. Initial Access: Gain a foothold on the system (exploit vulnerabilities, brute force, etc.)
3. Privilege Escalation: Obtain root/admin access
4. Persistence: Establish backdoor access
5. Exfiltration: Extract /root/flag.txt

RULES:
- You can only execute ONE command per turn
- Commands will be executed in the red-kali container
- Be methodical - learn from previous attempts
- Consider what the blue team might detect
- Balance speed with effectiveness
- Commands should be bash commands that work in Kali Linux

CURRENT PHASE GUIDANCE:
- reconnaissance: Use nmap, curl, nikto to discover services and vulnerabilities
- initial_access: Use exploits, password attacks, SQL injection
- privilege_escalation: Use privilege escalation techniques once you have initial access
- persistence: Create backdoors, add SSH keys
- exfiltration: Extract the flag file from /root/flag.txt

Think step-by-step:
1. What have we learned so far from the history?
2. What is the logical next step in the {observation['phase']} phase?
3. What specific command should we execute?
4. What do we expect to learn or achieve?

Respond ONLY with valid JSON in this exact format:
{{
    "reasoning": "Detailed explanation of strategy and why this command",
    "command": "exact bash command to execute",
    "expected_outcome": "what we hope to discover or achieve",
    "phase": "{observation['phase']}"
}}

DO NOT include any text outside the JSON structure.
Ensure the command is a valid bash command.
"""

    def _format_history(self, history: List[Dict]) -> str:
        """Format history for prompt"""
        if not history:
            return "No history available."

        formatted = []
        for i, entry in enumerate(history, 1):
            action = entry.get('red_action', 'unknown')
            success = entry.get('red_success', False)
            result_preview = str(entry.get('red_result', ''))[:200]
            formatted.append(
                f"{i}. Action: {action}\n"
                f"   Success: {success}\n"
                f"   Result: {result_preview}..."
            )
        return "\n\n".join(formatted)

    def _update_state(self, decision: Dict):
        """Update internal state based on decision"""
        # Update phase if changed
        if 'phase' in decision:
            self.current_phase = decision['phase']

        # Store in memory
        self.memory.append({
            "decision": decision,
            "timestamp": datetime.now().isoformat()
        })

    def update_from_result(self, command: str, result: Dict, success: bool):
        """
        Update agent state based on command result

        Args:
            command: Command that was executed
            result: Execution result
            success: Whether command succeeded
        """
        # Extract useful information from results
        stdout = result.get('stdout', '')

        # Update discovered services if we see port scan results
        if 'nmap' in command and success:
            self.discovered_info['services'] = self._parse_nmap_output(stdout)

        # Update access level if we gain access
        if success and any(keyword in stdout.lower() for keyword in ['shell', 'root@', 'admin@']):
            if 'root@' in stdout:
                self.access_level = 'root'
                self.current_phase = 'exfiltration'
            elif any(keyword in stdout for keyword in ['shell', '@']):
                self.access_level = 'user'
                self.current_phase = 'privilege_escalation'

    def _parse_nmap_output(self, output: str) -> List[str]:
        """Parse nmap output to extract services"""
        services = []
        lines = output.split('\n')
        for line in lines:
            if '/tcp' in line or '/udp' in line:
                services.append(line.strip())
        return services if services else ["(nmap scan completed)"]
