"""
Database interface for Project Icarus
Handles all PostgreSQL interactions for game state, logging, and telemetry
"""

import logging
import psycopg2
import psycopg2.extras
from datetime import datetime
from typing import Dict, List, Optional, Any
import json

logger = logging.getLogger(__name__)


class GameDatabase:
    """Database interface for game state and logging"""

    def __init__(self, connection_string: str):
        """
        Initialize database connection

        Args:
            connection_string: PostgreSQL connection string
        """
        self.connection_string = connection_string
        self.conn = None
        self.connect()

    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(self.connection_string)
            self.conn.autocommit = False
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise

    def ensure_connection(self):
        """Ensure database connection is alive"""
        try:
            if self.conn.closed:
                self.connect()
        except Exception as e:
            logger.warning(f"Connection check failed, reconnecting: {e}")
            self.connect()

    def create_game(
        self,
        red_team_model: str,
        blue_team_model: str,
        scenario: str,
        config: Optional[Dict] = None
    ) -> str:
        """
        Create a new game session

        Args:
            red_team_model: AI model for red team
            blue_team_model: AI model for blue team
            scenario: Scenario name
            config: Optional game configuration

        Returns:
            game_id: UUID of created game
        """
        self.ensure_connection()
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO games (red_team_model, blue_team_model, scenario, config)
                    VALUES (%s, %s, %s, %s)
                    RETURNING game_id
                    """,
                    (red_team_model, blue_team_model, scenario, json.dumps(config) if config else None)
                )
                game_id = cur.fetchone()[0]
                self.conn.commit()
                logger.info(f"Created game {game_id} with scenario {scenario}")
                return str(game_id)
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Failed to create game: {e}")
            raise

    def end_game(self, game_id: str, winner: Optional[str] = None):
        """
        Mark game as completed

        Args:
            game_id: Game UUID
            winner: 'red', 'blue', or None for draw
        """
        self.ensure_connection()
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE games
                    SET end_time = NOW(), status = 'completed', winner = %s
                    WHERE game_id = %s
                    """,
                    (winner, game_id)
                )
                self.conn.commit()
                logger.info(f"Game {game_id} ended. Winner: {winner or 'draw'}")
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Failed to end game: {e}")
            raise

    def log_round(
        self,
        game_id: str,
        round_num: int,
        phase: str,
        red_data: Dict,
        blue_data: Dict
    ) -> str:
        """
        Log a complete round

        Args:
            game_id: Game UUID
            round_num: Round number
            phase: Game phase
            red_data: Red team action data
            blue_data: Blue team action data

        Returns:
            round_id: UUID of created round
        """
        self.ensure_connection()
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO rounds (
                        game_id, round_number, phase,
                        red_observation, red_reasoning, red_action, red_result, red_success, red_execution_time_ms,
                        blue_observation, blue_reasoning, blue_action, blue_result, blue_success, blue_execution_time_ms
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING round_id
                    """,
                    (
                        game_id, round_num, phase,
                        red_data.get('observation'), red_data.get('reasoning'),
                        red_data.get('action'), red_data.get('result'),
                        red_data.get('success'), red_data.get('execution_time_ms'),
                        blue_data.get('observation'), blue_data.get('reasoning'),
                        blue_data.get('action'), blue_data.get('result'),
                        blue_data.get('success'), blue_data.get('execution_time_ms')
                    )
                )
                round_id = cur.fetchone()[0]
                self.conn.commit()
                logger.debug(f"Logged round {round_num} for game {game_id}")
                return str(round_id)
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Failed to log round: {e}")
            raise

    def log_command(
        self,
        game_id: str,
        round_id: str,
        team: str,
        container: str,
        command: str,
        result: Dict,
        execution_time_ms: int
    ):
        """
        Log a command execution

        Args:
            game_id: Game UUID
            round_id: Round UUID
            team: 'red' or 'blue'
            container: Container name
            command: Command executed
            result: Execution result dict
            execution_time_ms: Execution time in milliseconds
        """
        self.ensure_connection()
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO command_log (
                        game_id, round_id, team, container, command,
                        exit_code, stdout, stderr, execution_time_ms
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        game_id, round_id, team, container, command,
                        result.get('exit_code'), result.get('stdout'),
                        result.get('stderr'), execution_time_ms
                    )
                )
                self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Failed to log command: {e}")
            raise

    def update_score(self, game_id: str, team: str, points: int):
        """
        Update team score

        Args:
            game_id: Game UUID
            team: 'red' or 'blue'
            points: Points to add (can be negative)
        """
        self.ensure_connection()
        try:
            column = f"{team}_score"
            with self.conn.cursor() as cur:
                cur.execute(
                    f"""
                    UPDATE games
                    SET {column} = {column} + %s
                    WHERE game_id = %s
                    """,
                    (points, game_id)
                )
                self.conn.commit()
                logger.debug(f"Updated {team} score by {points} points")
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Failed to update score: {e}")
            raise

    def record_event(
        self,
        game_id: str,
        round_id: str,
        event_type: str,
        team: str,
        description: str,
        points: int = 0,
        metadata: Optional[Dict] = None
    ):
        """
        Record a game event

        Args:
            game_id: Game UUID
            round_id: Round UUID
            event_type: Type of event
            team: 'red' or 'blue'
            description: Event description
            points: Points awarded
            metadata: Optional metadata
        """
        self.ensure_connection()
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO events (
                        game_id, round_id, event_type, team, description, points_awarded, metadata
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (game_id, round_id, event_type, team, description, points, json.dumps(metadata) if metadata else None)
                )
                self.conn.commit()
                logger.info(f"Event: {team} - {event_type} ({points} points)")
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Failed to record event: {e}")
            raise

    def get_recent_context(self, game_id: str, team: str, limit: int = 10) -> List[Dict]:
        """
        Get recent round history for a team

        Args:
            game_id: Game UUID
            team: 'red' or 'blue'
            limit: Number of recent rounds to fetch

        Returns:
            List of round data dictionaries
        """
        self.ensure_connection()
        try:
            with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                columns = f"{team}_action, {team}_result, {team}_success, {team}_reasoning"
                cur.execute(
                    f"""
                    SELECT round_number, {columns}
                    FROM rounds
                    WHERE game_id = %s
                    ORDER BY round_number DESC
                    LIMIT %s
                    """,
                    (game_id, limit)
                )
                rows = cur.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Failed to get recent context: {e}")
            return []

    def get_game_scores(self, game_id: str) -> Dict[str, int]:
        """
        Get current game scores

        Args:
            game_id: Game UUID

        Returns:
            Dictionary with 'red' and 'blue' scores
        """
        self.ensure_connection()
        try:
            with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(
                    "SELECT red_score, blue_score FROM games WHERE game_id = %s",
                    (game_id,)
                )
                result = cur.fetchone()
                return {'red': result['red_score'], 'blue': result['blue_score']}
        except Exception as e:
            logger.error(f"Failed to get scores: {e}")
            return {'red': 0, 'blue': 0}

    def close(self):
        """Close database connection"""
        if self.conn and not self.conn.closed:
            self.conn.close()
            logger.info("Database connection closed")
