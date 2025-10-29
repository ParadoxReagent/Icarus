"""
Blue Team AI Agent for Project Icarus
AI-controlled defensive security operations agent supporting multiple AI providers
Phase 3: Includes AI memory and learning capabilities
"""

import logging
import json
import os
from typing import Dict, List, Optional
from datetime import datetime
from .ai_provider import AIClient

logger = logging.getLogger(__name__)


class BlueTeamAgent:
    """
    AI-controlled defensive security operations agent with learning capabilities

    Phase 3 Features:
    - Learns from past games via memory system
    - Adapts defense strategies based on patterns
    - Improves detection based on historical attacks
    """

    def __init__(self, provider: str = None, model: str = None, memory_manager=None, scenario: str = None):
        """
        Initialize Blue Team agent with multi-provider support and memory

        Args:
            provider: AI provider (anthropic, litellm, openrouter). Auto-detected if None.
            model: Model identifier. Uses BLUE_TEAM_MODEL env var if None.
            memory_manager: MemoryManager instance for cross-game learning (Phase 3)
            scenario: Current scenario ID for relevant memory retrieval
        """
        # Use environment variables if not provided
        if model is None:
            model = os.getenv('BLUE_TEAM_MODEL', 'claude-sonnet-4-5-20250929')

        if provider is None:
            provider = os.getenv('BLUE_TEAM_PROVIDER', '').strip()
            provider = provider if provider else None  # Auto-detect if empty

        self.model = model
        self.provider = provider or 'auto-detected'

        # Initialize AI client with provider abstraction
        try:
            self.client = AIClient(provider_type=provider, model=model)
            logger.info(f"Blue Team initialized: provider={self.client.provider_type}, model={model}")
        except Exception as e:
            logger.error(f"Failed to initialize Blue Team AI client: {e}")
            raise

        # Session memory (current game)
        self.memory = []
        self.alerts = []
        self.blocked_ips = []
        self.baseline_metrics = {}

        # Phase 3: Cross-game learning
        self.memory_manager = memory_manager
        self.scenario = scenario
        self.learning_enabled = memory_manager is not None

        if self.learning_enabled:
            logger.info("Blue Team: Learning mode ENABLED - will use past game knowledge")
            self._load_relevant_memories()
        else:
            logger.info("Blue Team: Learning mode disabled (no memory manager provided)")

    def monitor_system(self, execute_command_func) -> Dict:
        """
        Collect telemetry from target system

        Args:
            execute_command_func: Function to execute commands on blue-target

        Returns:
            Telemetry data dictionary
        """
        telemetry = {}

        # Get active network connections
        result = execute_command_func("blue-target", "netstat -tn | grep ESTABLISHED | wc -l")
        telemetry['active_connections'] = result.get('stdout', '0').strip()

        # Check failed auth attempts
        result = execute_command_func("blue-target", "grep 'Failed password' /var/log/auth.log 2>/dev/null | tail -5")
        telemetry['failed_auth_attempts'] = result.get('stdout', 'No recent failures').strip()

        # Check running processes
        result = execute_command_func("blue-target", "ps aux | wc -l")
        telemetry['process_count'] = result.get('stdout', '0').strip()

        # Check Apache access log
        result = execute_command_func("blue-target", "tail -10 /var/log/apache2/access.log 2>/dev/null")
        telemetry['recent_web_requests'] = result.get('stdout', 'No web logs').strip()

        # Check for suspicious files
        result = execute_command_func("blue-target", "find /tmp -type f -mmin -10 2>/dev/null | wc -l")
        telemetry['recent_tmp_files'] = result.get('stdout', '0').strip()

        # Check firewall rules
        result = execute_command_func("blue-target", "iptables -L INPUT -n | grep DROP | wc -l")
        telemetry['blocked_ips_count'] = result.get('stdout', '0').strip()

        return telemetry

    def decide_defense(self, telemetry: Dict, history: List[Dict]) -> Dict:
        """
        Use Claude API to analyze threats and decide defensive action

        Args:
            telemetry: Current system telemetry
            history: Recent defensive action history

        Returns:
            Defense decision dict
        """
        prompt = self._build_defense_prompt(telemetry, history)

        try:
            # Use unified AI client interface
            response_text = self.client.create_message(
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )

            # Strip markdown code blocks if present (some models wrap JSON in ```json ... ```)
            cleaned_response = response_text.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:]  # Remove ```json
            if cleaned_response.startswith('```'):
                cleaned_response = cleaned_response[3:]  # Remove ```
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3]  # Remove trailing ```
            cleaned_response = cleaned_response.strip()

            # Parse JSON response
            decision = json.loads(cleaned_response)

            # Update internal state
            self._update_state(decision)

            return decision

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response: {e}")
            logger.error(f"Response was: {response_text}")
            # Return safe fallback
            return {
                "threat_assessment": "unknown",
                "reasoning": "Failed to parse AI response",
                "defensive_action": "none",
                "indicators": [],
                "risk_to_availability": "low"
            }
        except Exception as e:
            logger.error(f"AI decision error: {e}")
            return {
                "threat_assessment": "error",
                "reasoning": f"Error: {str(e)}",
                "defensive_action": "none",
                "indicators": [],
                "risk_to_availability": "low"
            }

    def _build_defense_prompt(self, telemetry: Dict, history: List[Dict]) -> str:
        """
        Construct detailed prompt for Claude API

        Args:
            telemetry: Current telemetry
            history: Recent history

        Returns:
            Formatted prompt string
        """
        history_text = self._format_history(history[-5:]) if history else "No previous defensive actions."

        # Phase 3: Include memory context from past games
        memory_context = self._get_memory_context()

        return f"""You are an AI SOC analyst defending a Linux system from cyber attacks.

CURRENT TELEMETRY:
{json.dumps(telemetry, indent=2)}

RECENT ALERTS:
{self._format_alerts(self.alerts[-5:])}

BLOCKED IPs:
{json.dumps(self.blocked_ips, indent=2) if self.blocked_ips else "None blocked yet"}

RECENT DEFENSIVE ACTIONS:
{history_text}

{memory_context}

YOUR RESPONSIBILITIES:
1. Monitor system for suspicious activity
2. Detect and classify threats
3. Block malicious actors
4. Maintain service availability
5. Perform forensic analysis

AVAILABLE DEFENSES:
- iptables -A INPUT -s <IP> -j DROP: Block specific IP address
- iptables -L INPUT -n: List firewall rules
- grep 'pattern' /var/log/auth.log: Search authentication logs
- grep 'pattern' /var/log/apache2/access.log: Search web logs
- tail -f /var/log/apache2/access.log: Monitor web traffic
- ps aux | grep <process>: Check for suspicious processes
- netstat -tnp: View active connections
- service apache2 status: Check service status

THREAT INDICATORS TO WATCH FOR:
- Multiple failed SSH login attempts (brute force)
- Port scanning activity (many connections)
- SQL injection patterns in web logs
- Unusual processes or files in /tmp
- Suspicious network connections
- Web vulnerability scanners (nikto, sqlmap)

SCORING NOTES:
- You get points for detecting and blocking REAL attacks
- You LOSE points for false positives that block legitimate traffic
- You LOSE points if services go down unnecessarily
- Balance security with availability
- Only take action when you have clear evidence of malicious activity

Analyze the current situation:
1. Is there active malicious activity based on the telemetry?
2. What specific indicators of compromise do you see?
3. What is the threat level?
4. What defensive action (if any) should be taken?
5. Will this action maintain service availability?

IMPORTANT:
- If you see clear evidence of attack (multiple failed logins, scanning, SQL injection), take defensive action
- If telemetry looks normal, use "none" for defensive_action
- Only block IPs when you have strong evidence of malicious activity
- Be specific about what indicators you're seeing

Respond ONLY with valid JSON in this exact format:
{{
    "threat_assessment": "none|low|medium|high|critical",
    "reasoning": "Detailed analysis of the situation and evidence",
    "defensive_action": "exact bash command to execute, or 'none' if no action needed",
    "indicators": ["list", "of", "specific", "IOCs", "observed"],
    "risk_to_availability": "low|medium|high"
}}

DO NOT include any text outside the JSON structure.
"""

    def _format_history(self, history: List[Dict]) -> str:
        """Format history for prompt"""
        if not history:
            return "No history available."

        formatted = []
        for i, entry in enumerate(history, 1):
            action = entry.get('blue_action', 'none')
            success = entry.get('blue_success', False)
            reasoning = entry.get('blue_reasoning') or 'unknown'
            # Handle None values safely
            reasoning_text = reasoning[:150] if reasoning and len(reasoning) > 150 else reasoning
            formatted.append(
                f"{i}. Action: {action}\n"
                f"   Success: {success}\n"
                f"   Reasoning: {reasoning_text}..."
            )
        return "\n\n".join(formatted)

    def _format_alerts(self, alerts: List[Dict]) -> str:
        """Format recent alerts"""
        if not alerts:
            return "No recent alerts."

        formatted = []
        for alert in alerts:
            formatted.append(f"- {alert.get('type', 'unknown')}: {alert.get('description', 'no details')}")
        return "\n".join(formatted)

    def _update_state(self, decision: Dict):
        """Update internal state based on decision"""
        # Track blocked IPs
        action = decision.get('defensive_action', '')
        if 'iptables' in action and '-j DROP' in action:
            # Extract IP from iptables command
            parts = action.split()
            if '-s' in parts:
                idx = parts.index('-s')
                if idx + 1 < len(parts):
                    ip = parts[idx + 1]
                    if ip not in self.blocked_ips:
                        self.blocked_ips.append(ip)

        # Add to alerts if threat detected
        threat = decision.get('threat_assessment', 'none')
        if threat not in ['none', 'low']:
            self.alerts.append({
                'type': threat,
                'description': decision.get('reasoning', ''),
                'timestamp': datetime.now().isoformat()
            })

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
        # Track successful blocks
        if 'iptables' in command and success and '-j DROP' in command:
            logger.info("Successfully blocked an IP address")

    # ============================================================================
    # Phase 3: Memory and Learning Methods
    # ============================================================================

    def _load_relevant_memories(self):
        """Load relevant memories from past games (Phase 3)"""
        if not self.learning_enabled:
            return

        try:
            # Get learning summary
            summary = self.memory_manager.get_learning_summary(
                team='blue',
                scenario=self.scenario
            )

            logger.info(f"Blue Team loaded {summary['total_memories']} memories from past games")
            logger.info(f"  Successful: {summary['successful_count']}, Failed: {summary['failed_count']}")

            # Log high-value learnings
            if summary['high_value_learnings']:
                logger.info("Blue Team high-value learnings:")
                for learning in summary['high_value_learnings'][:3]:
                    logger.info(f"  [{learning['type']}] {learning['content'][:80]}...")

        except Exception as e:
            logger.error(f"Failed to load memories: {e}")

    def _get_memory_context(self) -> str:
        """
        Get relevant memory context for current situation (Phase 3)

        Returns:
            Formatted string with relevant learnings
        """
        if not self.learning_enabled:
            return ""

        try:
            return self.memory_manager.format_memories_for_prompt(
                team='blue',
                phase='defense',  # Blue team doesn't have phases like red team
                scenario=self.scenario or 'unknown',
                limit=5
            )
        except Exception as e:
            logger.error(f"Error retrieving memory context: {e}")
            return ""

    def store_learning(self, game_id: str, command: str, result: Dict, success: bool):
        """
        Store learning from this execution for future games (Phase 3)

        Args:
            game_id: Current game ID
            command: Command that was executed
            result: Execution result
            success: Whether command succeeded
        """
        if not self.learning_enabled:
            return

        try:
            # Analyze if this is worth remembering
            pattern = self.memory_manager.analyze_pattern(
                team='blue',
                command=command,
                result=result,
                success=success,
                phase='defense'
            )

            if pattern:
                # Store the memory
                memory_id = self.memory_manager.store_memory(
                    game_id=game_id,
                    team='blue',
                    memory_type=pattern['type'],
                    content=pattern['content'],
                    successful=success,
                    context={
                        'command': command,
                        'phase': 'defense',
                        'scenario': self.scenario,
                        'blocked_ips': len(self.blocked_ips),
                        'alerts': len(self.alerts)
                    },
                    relevance_score=pattern['relevance']
                )

                logger.debug(f"Stored {pattern['type']} memory: {memory_id}")

        except Exception as e:
            logger.error(f"Failed to store learning: {e}")
