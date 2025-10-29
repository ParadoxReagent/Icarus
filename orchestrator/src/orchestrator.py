"""
Game Orchestrator for Project Icarus
Manages game loop, AI coordination, and command execution
"""

import logging
import time
import docker
from typing import Dict, Optional
import json

from .database import GameDatabase
from .red_team_agent import RedTeamAgent
from .blue_team_agent import BlueTeamAgent
from .scoring import ScoringSystem

logger = logging.getLogger(__name__)


class GameOrchestrator:
    """Main game loop coordinator"""

    def __init__(
        self,
        database: GameDatabase,
        red_agent: RedTeamAgent,
        blue_agent: BlueTeamAgent,
        command_timeout: int = 30
    ):
        """
        Initialize orchestrator

        Args:
            database: Database interface
            red_agent: Red team AI agent
            blue_agent: Blue team AI agent
            command_timeout: Command execution timeout in seconds
        """
        self.db = database
        self.red_agent = red_agent
        self.blue_agent = blue_agent
        self.docker_client = docker.from_env()
        self.command_timeout = command_timeout
        self.scoring = ScoringSystem()

        self.current_game_id = None
        self.round_number = 0

    def start_game(self, scenario: str, max_rounds: int = 30) -> str:
        """
        Initialize and start a new game session

        Args:
            scenario: Scenario name
            max_rounds: Maximum number of rounds

        Returns:
            game_id: UUID of the game
        """
        logger.info(f"Starting new game with scenario: {scenario}")

        # Create game in database
        config = {
            'max_rounds': max_rounds,
            'command_timeout': self.command_timeout,
            'scenario': scenario
        }

        self.current_game_id = self.db.create_game(
            red_team_model=self.red_agent.model,
            blue_team_model=self.blue_agent.model,
            scenario=scenario,
            config=config
        )

        logger.info(f"Game created with ID: {self.current_game_id}")

        # Verify containers are running
        self._verify_containers()

        # Run game loop
        self.run_game_loop(max_rounds)

        return self.current_game_id

    def _verify_containers(self):
        """Verify required containers are running"""
        required = ['red-kali', 'blue-target']
        for container_name in required:
            try:
                container = self.docker_client.containers.get(container_name)
                if container.status != 'running':
                    logger.warning(f"Container {container_name} is not running: {container.status}")
                else:
                    logger.info(f"Container {container_name} is ready")
            except docker.errors.NotFound:
                logger.error(f"Container {container_name} not found!")
                raise

    def run_game_loop(self, max_rounds: int):
        """
        Main game execution loop

        Args:
            max_rounds: Maximum number of rounds
        """
        logger.info("Starting game loop")
        self.round_number = 0

        while self.round_number < max_rounds:
            self.round_number += 1
            current_phase = self.scoring.get_current_phase(self.round_number)

            print(f"\n{'=' * 80}")
            print(f"ROUND {self.round_number} / {max_rounds} - Phase: {current_phase.upper()}")
            print(f"{'=' * 80}\n")

            # Update agent phases
            self.red_agent.current_phase = current_phase

            # Execute red team turn
            print("[RED TEAM TURN]")
            red_result = self.execute_red_team_turn()

            # Small delay between turns
            time.sleep(1)

            # Execute blue team turn
            print("\n[BLUE TEAM TURN]")
            blue_result = self.execute_blue_team_turn()

            # Log round to database
            round_id = self.db.log_round(
                game_id=self.current_game_id,
                round_num=self.round_number,
                phase=current_phase,
                red_data=red_result,
                blue_data=blue_result
            )

            # Evaluate events and update scores
            events = self.scoring.evaluate_round(round_id, red_result, blue_result)
            self._process_events(round_id, events)

            # Display scores
            scores = self.db.get_game_scores(self.current_game_id)
            print(f"\n[SCORES] Red: {scores['red']} | Blue: {scores['blue']}")

            # Check win conditions
            red_event_types = [e[1] for e in events if e[0] == 'red']
            blue_event_types = [e[1] for e in events if e[0] == 'blue']
            game_over, winner = self.scoring.check_win_conditions(
                red_event_types, blue_event_types, self.round_number, max_rounds
            )

            if game_over:
                if winner:
                    print(f"\n{'=' * 80}")
                    print(f"GAME OVER! {winner.upper()} TEAM WINS!")
                    print(f"{'=' * 80}\n")
                else:
                    # Determine winner by score
                    winner = 'red' if scores['red'] > scores['blue'] else 'blue' if scores['blue'] > scores['red'] else None
                    if winner:
                        print(f"\n{'=' * 80}")
                        print(f"GAME OVER! {winner.upper()} TEAM WINS BY SCORE!")
                        print(f"{'=' * 80}\n")
                    else:
                        print(f"\n{'=' * 80}")
                        print(f"GAME OVER! IT'S A DRAW!")
                        print(f"{'=' * 80}\n")

                self.db.end_game(self.current_game_id, winner)
                break

            # Pause between rounds
            time.sleep(2)

        # End game if max rounds reached
        if self.round_number >= max_rounds:
            scores = self.db.get_game_scores(self.current_game_id)
            winner = 'red' if scores['red'] > scores['blue'] else 'blue' if scores['blue'] > scores['red'] else None
            self.db.end_game(self.current_game_id, winner)

            print(f"\n{'=' * 80}")
            print(f"GAME COMPLETE - Final Scores: Red: {scores['red']} | Blue: {scores['blue']}")
            if winner:
                print(f"Winner: {winner.upper()} TEAM")
            else:
                print("Result: DRAW")
            print(f"{'=' * 80}\n")

    def execute_red_team_turn(self) -> Dict:
        """
        Execute red team observation -> decision -> action

        Returns:
            Red team turn result
        """
        # Get current state
        observation = self.red_agent.observe_environment()

        # Get recent history from database
        history = self.db.get_recent_context(
            game_id=self.current_game_id,
            team='red',
            limit=10
        )

        # AI decides action
        decision = self.red_agent.decide_action(observation, history)

        print(f"Reasoning: {decision.get('reasoning', 'N/A')[:200]}...")
        print(f"Command: {decision.get('command', 'N/A')}")

        # Execute command in red-kali container
        start_time = time.time()
        result = self.execute_in_container(
            container='red-kali',
            command=decision.get('command', 'echo "No command"')
        )
        execution_time = int((time.time() - start_time) * 1000)

        success = result['exit_code'] == 0
        result_preview = result['stdout'][:300] if result['stdout'] else result['stderr'][:300]
        print(f"Result: {result_preview}...")
        print(f"Success: {success}")

        # Update red agent with result
        self.red_agent.update_from_result(decision.get('command', ''), result, success)

        # Log to database
        self.db.log_command(
            game_id=self.current_game_id,
            round_id=str(self.round_number),
            team='red',
            container='red-kali',
            command=decision.get('command', ''),
            result=result,
            execution_time_ms=execution_time
        )

        return {
            'observation': json.dumps(observation),
            'reasoning': decision.get('reasoning', ''),
            'action': decision.get('command', ''),
            'result': result['stdout'] + result['stderr'],
            'success': success,
            'execution_time_ms': execution_time,
            'phase': decision.get('phase', 'unknown')
        }

    def execute_blue_team_turn(self) -> Dict:
        """
        Execute blue team monitoring -> analysis -> defense

        Returns:
            Blue team turn result
        """
        # Collect telemetry
        telemetry = self.blue_agent.monitor_system(self.execute_in_container)

        # Get recent history
        history = self.db.get_recent_context(
            game_id=self.current_game_id,
            team='blue',
            limit=10
        )

        # AI analyzes and decides
        defense = self.blue_agent.decide_defense(telemetry, history)

        print(f"Threat Level: {defense.get('threat_assessment', 'unknown')}")
        print(f"Reasoning: {defense.get('reasoning', 'N/A')[:200]}...")
        print(f"Action: {defense.get('defensive_action', 'none')}")

        # Execute defensive action if needed
        result = {'stdout': '', 'stderr': '', 'exit_code': 0}
        execution_time = 0

        if defense.get('defensive_action') != 'none':
            start_time = time.time()
            result = self.execute_in_container(
                container='blue-target',
                command=defense.get('defensive_action', 'echo "No action"')
            )
            execution_time = int((time.time() - start_time) * 1000)

            success = result['exit_code'] == 0
            print(f"Defense executed: {success}")

            # Update blue agent with result
            self.blue_agent.update_from_result(defense.get('defensive_action', ''), result, success)

            # Log to database
            self.db.log_command(
                game_id=self.current_game_id,
                round_id=str(self.round_number),
                team='blue',
                container='blue-target',
                command=defense.get('defensive_action', ''),
                result=result,
                execution_time_ms=execution_time
            )

        return {
            'observation': json.dumps(telemetry),
            'reasoning': defense.get('reasoning', ''),
            'action': defense.get('defensive_action', 'none'),
            'result': result['stdout'] + result['stderr'],
            'success': result['exit_code'] == 0,
            'execution_time_ms': execution_time
        }

    def execute_in_container(self, container: str, command: str) -> Dict:
        """
        Execute command in specified Docker container

        Args:
            container: Container name
            command: Command to execute

        Returns:
            Dict with exit_code, stdout, stderr
        """
        try:
            container_obj = self.docker_client.containers.get(container)

            # Execute with timeout
            exit_code, output = container_obj.exec_run(
                cmd=['bash', '-c', command],
                demux=True,
                timeout=self.command_timeout
            )

            stdout = output[0].decode('utf-8', errors='replace') if output[0] else ""
            stderr = output[1].decode('utf-8', errors='replace') if output[1] else ""

            return {
                'exit_code': exit_code,
                'stdout': stdout,
                'stderr': stderr
            }

        except docker.errors.NotFound:
            logger.error(f"Container {container} not found")
            return {
                'exit_code': -1,
                'stdout': '',
                'stderr': f"Container {container} not found"
            }
        except Exception as e:
            logger.error(f"Command execution error: {e}")
            return {
                'exit_code': -1,
                'stdout': '',
                'stderr': str(e)
            }

    def _process_events(self, round_id: str, events: list):
        """
        Process and record events

        Args:
            round_id: Round UUID
            events: List of event tuples
        """
        for team, event_type, points, description in events:
            # Update score
            self.db.update_score(self.current_game_id, team, points)

            # Record event
            self.db.record_event(
                game_id=self.current_game_id,
                round_id=round_id,
                event_type=event_type,
                team=team,
                description=description,
                points=points
            )

            # Log to console
            if points != 0:
                sign = '+' if points > 0 else ''
                print(f"  [EVENT] {team.upper()}: {event_type} ({sign}{points} points)")
