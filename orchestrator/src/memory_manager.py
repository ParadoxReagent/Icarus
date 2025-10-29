"""
AI Memory Manager for Project Icarus
Enables AI agents to learn from past games and improve strategies
"""

import logging
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import re

logger = logging.getLogger(__name__)


class MemoryManager:
    """
    Manages AI memory storage and retrieval for learning across games.

    Memory Types:
    - successful_attack: Commands/strategies that succeeded in compromising systems
    - failed_attack: Attempted attacks that were blocked or failed
    - defensive_pattern: Successful defensive actions
    - vulnerability: Discovered vulnerabilities and how to exploit them
    - evasion_technique: Methods that avoided detection
    - detection_signature: Patterns that indicate malicious activity
    """

    MEMORY_TYPES = [
        'successful_attack',
        'failed_attack',
        'defensive_pattern',
        'vulnerability',
        'evasion_technique',
        'detection_signature',
        'learned_strategy'
    ]

    def __init__(self, database):
        """
        Initialize memory manager

        Args:
            database: GameDatabase instance
        """
        self.db = database
        self.cache = {}  # In-memory cache for current session

    def store_memory(
        self,
        game_id: str,
        team: str,
        memory_type: str,
        content: str,
        successful: bool,
        context: Dict = None,
        relevance_score: float = 0.5
    ) -> str:
        """
        Store a new memory entry

        Args:
            game_id: Game session ID
            team: 'red' or 'blue'
            memory_type: Type of memory (see MEMORY_TYPES)
            content: Text description of the memory
            successful: Whether this action was successful
            context: Additional context data (command, phase, etc.)
            relevance_score: How relevant/important this memory is (0.0-1.0)

        Returns:
            memory_id: UUID of stored memory
        """
        if memory_type not in self.MEMORY_TYPES:
            logger.warning(f"Unknown memory type: {memory_type}")

        context = context or {}

        with self.db.get_cursor() as cur:
            cur.execute("""
                INSERT INTO ai_memory (
                    game_id, team, memory_type, content,
                    successful, context, relevance_score
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING memory_id
            """, (game_id, team, memory_type, content, successful, json.dumps(context), relevance_score))

            memory_id = cur.fetchone()[0]
            self.db.conn.commit()

            logger.info(f"Stored {memory_type} memory for {team} team: {content[:50]}...")
            return memory_id

    def retrieve_memories(
        self,
        team: str,
        memory_type: Optional[str] = None,
        successful_only: bool = False,
        limit: int = 10,
        min_relevance: float = 0.3,
        scenario: Optional[str] = None,
        phase: Optional[str] = None
    ) -> List[Dict]:
        """
        Retrieve relevant memories for decision making

        Args:
            team: 'red' or 'blue'
            memory_type: Filter by memory type, or None for all
            successful_only: Only return successful memories
            limit: Maximum number of memories to return
            min_relevance: Minimum relevance score
            scenario: Filter by scenario
            phase: Filter by phase (reconnaissance, initial_access, etc.)

        Returns:
            List of memory dicts with content, context, relevance_score
        """
        cache_key = f"{team}_{memory_type}_{successful_only}_{scenario}_{phase}"

        # Check cache first
        if cache_key in self.cache:
            return self.cache[cache_key][:limit]

        with self.db.get_cursor() as cur:
            query = """
                SELECT
                    m.memory_id,
                    m.memory_type,
                    m.content,
                    m.successful,
                    m.context,
                    m.relevance_score,
                    m.created_at,
                    g.scenario
                FROM ai_memory m
                LEFT JOIN games g ON m.game_id = g.game_id
                WHERE m.team = %s
                AND m.relevance_score >= %s
            """

            params = [team, min_relevance]

            if memory_type:
                query += " AND m.memory_type = %s"
                params.append(memory_type)

            if successful_only:
                query += " AND m.successful = TRUE"

            if scenario:
                query += " AND g.scenario = %s"
                params.append(scenario)

            if phase:
                query += " AND m.context->>'phase' = %s"
                params.append(phase)

            query += """
                ORDER BY m.relevance_score DESC, m.created_at DESC
                LIMIT %s
            """
            params.append(limit)

            cur.execute(query, params)

            memories = []
            for row in cur.fetchall():
                memories.append({
                    'memory_id': row[0],
                    'memory_type': row[1],
                    'content': row[2],
                    'successful': row[3],
                    'context': row[4],
                    'relevance_score': row[5],
                    'created_at': row[6],
                    'scenario': row[7]
                })

            # Cache results
            self.cache[cache_key] = memories

            return memories

    def analyze_pattern(
        self,
        team: str,
        command: str,
        result: Dict,
        success: bool,
        phase: str
    ) -> Optional[Dict]:
        """
        Analyze a command execution to identify patterns worth remembering

        Args:
            team: 'red' or 'blue'
            command: Command that was executed
            result: Execution result
            success: Whether command succeeded
            phase: Current game phase

        Returns:
            Pattern dict if significant pattern found, None otherwise
        """
        patterns = []

        # Red team pattern analysis
        if team == 'red':
            # Successful port scan
            if 'nmap' in command and success:
                if 'open' in result.get('stdout', '').lower():
                    patterns.append({
                        'type': 'successful_attack',
                        'content': f"Port scan successful: {command}",
                        'relevance': 0.6
                    })

            # Successful exploitation
            if any(tool in command for tool in ['sqlmap', 'metasploit', 'hydra', 'ssh']) and success:
                if any(indicator in result.get('stdout', '').lower()
                       for indicator in ['shell', 'success', 'admin', 'root']):
                    patterns.append({
                        'type': 'successful_attack',
                        'content': f"Exploitation succeeded in {phase}: {command}",
                        'relevance': 0.9
                    })

            # Failed attempts (important to remember what doesn't work)
            if not success and phase in ['initial_access', 'privilege_escalation']:
                patterns.append({
                    'type': 'failed_attack',
                    'content': f"Failed in {phase}: {command}",
                    'relevance': 0.4
                })

            # Discovered vulnerability
            if 'vulnerable' in result.get('stdout', '').lower():
                patterns.append({
                    'type': 'vulnerability',
                    'content': f"Vulnerability identified: {command}",
                    'relevance': 0.8
                })

        # Blue team pattern analysis
        elif team == 'blue':
            # Successful attack detection
            if 'grep' in command and success:
                stdout = result.get('stdout', '')
                if any(indicator in stdout.lower() for indicator in ['failed', 'denied', 'attack', 'scan']):
                    patterns.append({
                        'type': 'detection_signature',
                        'content': f"Detection pattern: {command}",
                        'relevance': 0.7
                    })

            # Successful blocking
            if 'iptables' in command and '-j DROP' in command and success:
                patterns.append({
                    'type': 'defensive_pattern',
                    'content': f"Successfully blocked IP: {command}",
                    'relevance': 0.8
                })

            # Service monitoring
            if success and any(svc in command for svc in ['systemctl', 'service', 'ps aux']):
                patterns.append({
                    'type': 'defensive_pattern',
                    'content': f"Effective monitoring: {command}",
                    'relevance': 0.5
                })

        return patterns[0] if patterns else None

    def get_learning_summary(self, team: str, scenario: Optional[str] = None) -> Dict:
        """
        Generate summary of what the AI has learned

        Args:
            team: 'red' or 'blue'
            scenario: Optional scenario filter

        Returns:
            Summary dict with statistics and key learnings
        """
        memories = self.retrieve_memories(
            team=team,
            scenario=scenario,
            limit=100,
            min_relevance=0.4
        )

        summary = {
            'total_memories': len(memories),
            'successful_count': sum(1 for m in memories if m['successful']),
            'failed_count': sum(1 for m in memories if not m['successful']),
            'by_type': defaultdict(int),
            'high_value_learnings': [],
            'recent_learnings': []
        }

        for memory in memories:
            summary['by_type'][memory['memory_type']] += 1

            # High value learnings (relevance > 0.7)
            if memory['relevance_score'] > 0.7:
                summary['high_value_learnings'].append({
                    'type': memory['memory_type'],
                    'content': memory['content'][:100],
                    'score': memory['relevance_score']
                })

        # Recent learnings (last 10)
        summary['recent_learnings'] = [
            {
                'type': m['memory_type'],
                'content': m['content'][:100],
                'successful': m['successful']
            }
            for m in memories[:10]
        ]

        return summary

    def format_memories_for_prompt(
        self,
        team: str,
        phase: str,
        scenario: str,
        limit: int = 5
    ) -> str:
        """
        Format relevant memories as text for inclusion in AI prompt

        Args:
            team: 'red' or 'blue'
            phase: Current game phase
            scenario: Current scenario
            limit: Max memories to include

        Returns:
            Formatted string for prompt injection
        """
        memories = self.retrieve_memories(
            team=team,
            scenario=scenario,
            phase=phase,
            limit=limit,
            min_relevance=0.5
        )

        if not memories:
            return "No previous learnings available for this scenario."

        formatted = ["LEARNED FROM PAST GAMES:", ""]

        successful = [m for m in memories if m['successful']]
        failed = [m for m in memories if not m['successful']]

        if successful:
            formatted.append("✓ SUCCESSFUL STRATEGIES:")
            for i, mem in enumerate(successful[:3], 1):
                formatted.append(f"  {i}. [{mem['memory_type']}] {mem['content']}")
                if 'command' in mem['context']:
                    formatted.append(f"     Command: {mem['context']['command']}")
            formatted.append("")

        if failed:
            formatted.append("✗ FAILED ATTEMPTS (avoid these):")
            for i, mem in enumerate(failed[:2], 1):
                formatted.append(f"  {i}. {mem['content']}")
            formatted.append("")

        return "\n".join(formatted)

    def clear_cache(self):
        """Clear in-memory cache"""
        self.cache = {}
        logger.info("Memory cache cleared")

    def prune_old_memories(self, days: int = 30, min_relevance: float = 0.3):
        """
        Remove old, low-relevance memories to keep database lean

        Args:
            days: Remove memories older than this
            min_relevance: Keep memories above this threshold regardless of age
        """
        cutoff = datetime.now() - timedelta(days=days)

        with self.db.get_cursor() as cur:
            cur.execute("""
                DELETE FROM ai_memory
                WHERE created_at < %s
                AND relevance_score < %s
            """, (cutoff, min_relevance))

            deleted = cur.rowcount
            self.db.conn.commit()

            logger.info(f"Pruned {deleted} old memories (>{days} days, <{min_relevance} relevance)")
            return deleted

    def boost_relevance(self, memory_id: str, boost: float = 0.1):
        """
        Increase relevance score of a memory (when it proves useful)

        Args:
            memory_id: Memory to boost
            boost: Amount to increase (0.1 = 10% increase)
        """
        with self.db.get_cursor() as cur:
            cur.execute("""
                UPDATE ai_memory
                SET relevance_score = LEAST(1.0, relevance_score + %s)
                WHERE memory_id = %s
            """, (boost, memory_id))

            self.db.conn.commit()
            logger.debug(f"Boosted relevance of memory {memory_id} by {boost}")


class PatternRecognizer:
    """
    Identifies patterns and strategies from game history
    """

    def __init__(self, database):
        self.db = database

    def identify_winning_strategies(self, team: str, scenario: str, min_games: int = 3) -> List[Dict]:
        """
        Identify strategies that consistently lead to wins

        Args:
            team: 'red' or 'blue'
            scenario: Scenario to analyze
            min_games: Minimum games needed for pattern

        Returns:
            List of identified strategy patterns
        """
        with self.db.get_cursor() as cur:
            # Get games where this team won
            cur.execute("""
                SELECT g.game_id, g.winner, r.round_number, r.phase,
                       CASE
                           WHEN %s = 'red' THEN r.red_action
                           ELSE r.blue_action
                       END as action,
                       CASE
                           WHEN %s = 'red' THEN r.red_reasoning
                           ELSE r.blue_reasoning
                       END as reasoning
                FROM games g
                JOIN rounds r ON g.game_id = r.game_id
                WHERE g.scenario = %s
                AND g.winner = %s
                AND g.status = 'completed'
                ORDER BY g.start_time DESC, r.round_number
                LIMIT 100
            """, (team, team, scenario, team))

            winning_games = cur.fetchall()

        if len(set(row[0] for row in winning_games)) < min_games:
            return []

        # Analyze patterns
        patterns = self._extract_patterns(winning_games)

        return patterns

    def _extract_patterns(self, game_data: List[Tuple]) -> List[Dict]:
        """Extract common patterns from game data"""
        patterns = []

        # Pattern: Command sequences
        command_sequences = defaultdict(int)
        phase_strategies = defaultdict(list)

        current_game = None
        game_sequence = []

        for game_id, winner, round_num, phase, action, reasoning in game_data:
            if game_id != current_game:
                if game_sequence:
                    seq_key = " -> ".join(game_sequence[:5])  # First 5 commands
                    command_sequences[seq_key] += 1
                current_game = game_id
                game_sequence = []

            if action:
                game_sequence.append(action.split()[0] if action.split() else action)
                phase_strategies[phase].append(action)

        # Identify common sequences
        for sequence, count in sorted(command_sequences.items(), key=lambda x: x[1], reverse=True)[:5]:
            if count >= 2:
                patterns.append({
                    'type': 'command_sequence',
                    'pattern': sequence,
                    'frequency': count,
                    'description': f"Common winning sequence: {sequence}"
                })

        # Identify phase-specific strategies
        for phase, actions in phase_strategies.items():
            if len(actions) >= 3:
                # Find most common action in this phase
                action_counts = defaultdict(int)
                for action in actions:
                    if action:
                        cmd = action.split()[0] if action.split() else action
                        action_counts[cmd] += 1

                if action_counts:
                    top_action = max(action_counts.items(), key=lambda x: x[1])
                    patterns.append({
                        'type': 'phase_strategy',
                        'phase': phase,
                        'action': top_action[0],
                        'frequency': top_action[1],
                        'description': f"Effective {phase} strategy: {top_action[0]}"
                    })

        return patterns

    def detect_evasion_techniques(self, team: str = 'red') -> List[Dict]:
        """
        Identify commands that successfully evaded detection

        Args:
            team: Usually 'red' team

        Returns:
            List of evasion techniques
        """
        with self.db.get_cursor() as cur:
            cur.execute("""
                SELECT DISTINCT r.red_action, COUNT(*) as success_count
                FROM rounds r
                WHERE r.red_success = TRUE
                AND NOT EXISTS (
                    SELECT 1 FROM events e
                    WHERE e.round_id = r.round_id
                    AND e.event_type = 'attack_detected'
                )
                GROUP BY r.red_action
                HAVING COUNT(*) >= 2
                ORDER BY success_count DESC
                LIMIT 10
            """)

            techniques = []
            for action, count in cur.fetchall():
                if action:
                    techniques.append({
                        'technique': action,
                        'success_count': count,
                        'type': 'evasion',
                        'description': f"Undetected {count} times: {action[:50]}"
                    })

            return techniques


if __name__ == "__main__":
    # Test memory manager
    print("Memory Manager module loaded successfully")
    print(f"Supported memory types: {MemoryManager.MEMORY_TYPES}")
