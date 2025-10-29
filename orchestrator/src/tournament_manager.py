ç"""
Tournament Manager for Project Icarus
Phase 3: Run multi-game tournaments with AI learning
"""

import logging
import json
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from collections import defaultdict
import uuid

logger = logging.getLogger(__name__)


class TournamentManager:
    """
    Manages multi-game tournaments with AI learning

    Tournament Types:
    - learning_progression: Same agents play multiple times, learning from each game
    - model_comparison: Different models compete against each other
    - scenario_mastery: Same config across all scenarios
    - custom: User-defined matchups
    """

    def __init__(self, database, orchestrator_factory):
        """
        Initialize tournament manager

        Args:
            database: GameDatabase instance
            orchestrator_factory: Function that creates orchestrator instances
        """
        self.db = database
        self.orchestrator_factory = orchestrator_factory
        self.current_tournament_id = None
        self.tournament_results = []

    def create_tournament(
        self,
        name: str,
        tournament_type: str,
        config: Dict,
        description: str = ""
    ) -> str:
        """
        Create a new tournament

        Args:
            name: Tournament name
            tournament_type: Type of tournament
            config: Tournament configuration
            description: Optional description

        Returns:
            tournament_id
        """
        tournament_id = str(uuid.uuid4())

        with self.db.get_cursor() as cur:
            # Create tournaments table if it doesn't exist
            cur.execute("""
                CREATE TABLE IF NOT EXISTS tournaments (
                    tournament_id UUID PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    tournament_type VARCHAR(50) NOT NULL,
                    description TEXT,
                    config JSONB NOT NULL,
                    status VARCHAR(20) DEFAULT 'pending',
                    start_time TIMESTAMP,
                    end_time TIMESTAMP,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)

            cur.execute("""
                INSERT INTO tournaments (
                    tournament_id, name, tournament_type, description, config
                )
                VALUES (%s, %s, %s, %s, %s)
            """, (tournament_id, name, tournament_type, description, json.dumps(config)))

            self.db.conn.commit()

        logger.info(f"Created tournament: {name} ({tournament_type}) - ID: {tournament_id}")
        return tournament_id

    def run_learning_progression(
        self,
        scenario: str,
        red_model: str,
        blue_model: str,
        num_games: int = 5,
        rounds_per_game: int = 30,
        red_provider: str = None,
        blue_provider: str = None
    ) -> Dict:
        """
        Run a learning progression tournament where same agents play multiple times

        Args:
            scenario: Scenario ID
            red_model: Red team model
            blue_model: Blue team model
            num_games: Number of games to play
            rounds_per_game: Rounds per game
            red_provider: Optional red team provider
            blue_provider: Optional blue team provider

        Returns:
            Tournament results dict
        """
        tournament_id = self.create_tournament(
            name=f"Learning Progression: {scenario}",
            tournament_type="learning_progression",
            config={
                "scenario": scenario,
                "red_model": red_model,
                "blue_model": blue_model,
                "red_provider": red_provider,
                "blue_provider": blue_provider,
                "num_games": num_games,
                "rounds_per_game": rounds_per_game
            },
            description=f"AI agents learn across {num_games} games"
        )

        self.current_tournament_id = tournament_id
        self._update_tournament_status(tournament_id, 'running')

        logger.info("=" * 80)
        logger.info(f"TOURNAMENT: Learning Progression")
        logger.info(f"Scenario: {scenario}")
        logger.info(f"Red Team: {red_provider or 'auto'}/{red_model}")
        logger.info(f"Blue Team: {blue_provider or 'auto'}/{blue_model}")
        logger.info(f"Games: {num_games} x {rounds_per_game} rounds")
        logger.info("=" * 80)

        results = {
            'tournament_id': tournament_id,
            'games': [],
            'statistics': {
                'red_wins': 0,
                'blue_wins': 0,
                'draws': 0,
                'avg_red_score': 0,
                'avg_blue_score': 0,
                'improvement_trend': []
            }
        }

        try:
            for game_num in range(1, num_games + 1):
                logger.info(f"\n{'=' * 80}")
                logger.info(f"GAME {game_num}/{num_games} - Learning from previous games")
                logger.info(f"{'=' * 80}\n")

                # Create orchestrator for this game
                orchestrator = self.orchestrator_factory(
                    scenario=scenario,
                    red_model=red_model,
                    blue_model=blue_model,
                    red_provider=red_provider,
                    blue_provider=blue_provider,
                    max_rounds=rounds_per_game
                )

                # Run the game
                game_id = orchestrator.start_game(
                    scenario=scenario,
                    max_rounds=rounds_per_game
                )

                # Get game results
                game_result = self._get_game_result(game_id)

                # Link game to tournament
                self._link_game_to_tournament(tournament_id, game_id, game_num)

                # Track results
                results['games'].append(game_result)

                if game_result['winner'] == 'red':
                    results['statistics']['red_wins'] += 1
                elif game_result['winner'] == 'blue':
                    results['statistics']['blue_wins'] += 1
                else:
                    results['statistics']['draws'] += 1

                # Log progress
                logger.info(f"\nGame {game_num} Complete:")
                logger.info(f"  Winner: {game_result['winner']}")
                logger.info(f"  Score: Red {game_result['red_score']} - Blue {game_result['blue_score']}")
                logger.info(f"  Tournament Standing: Red {results['statistics']['red_wins']} - "
                          f"Blue {results['statistics']['blue_wins']} - "
                          f"Draws {results['statistics']['draws']}")

                # Brief pause between games
                if game_num < num_games:
                    logger.info(f"\nPausing 3 seconds before next game...")
                    time.sleep(3)

            # Calculate final statistics
            results['statistics'] = self._calculate_tournament_stats(results['games'])

            # Store tournament results
            self._store_tournament_results(tournament_id, results)

            self._update_tournament_status(tournament_id, 'completed')

            # Print final report
            self._print_tournament_report(results)

            return results

        except Exception as e:
            logger.error(f"Tournament failed: {e}", exc_info=True)
            self._update_tournament_status(tournament_id, 'failed')
            raise

    def run_model_comparison(
        self,
        scenario: str,
        matchups: List[Dict],
        rounds_per_game: int = 30
    ) -> Dict:
        """
        Run model comparison tournament

        Args:
            scenario: Scenario ID
            matchups: List of matchup dicts with red_model, blue_model, red_provider, blue_provider
            rounds_per_game: Rounds per game

        Returns:
            Tournament results

        Example matchups:
        [
            {"red_model": "gpt-4o", "blue_model": "claude-sonnet-4-5", "red_provider": "litellm"},
            {"red_model": "claude-opus", "blue_model": "gpt-4o"},
        ]
        """
        tournament_id = self.create_tournament(
            name=f"Model Comparison: {scenario}",
            tournament_type="model_comparison",
            config={
                "scenario": scenario,
                "matchups": matchups,
                "rounds_per_game": rounds_per_game
            },
            description=f"Compare {len(matchups)} different model configurations"
        )

        self.current_tournament_id = tournament_id
        self._update_tournament_status(tournament_id, 'running')

        logger.info("=" * 80)
        logger.info(f"TOURNAMENT: Model Comparison")
        logger.info(f"Scenario: {scenario}")
        logger.info(f"Matchups: {len(matchups)}")
        logger.info("=" * 80)

        results = {
            'tournament_id': tournament_id,
            'matchups': [],
            'leaderboard': []
        }

        try:
            for idx, matchup in enumerate(matchups, 1):
                logger.info(f"\n{'=' * 80}")
                logger.info(f"MATCHUP {idx}/{len(matchups)}")
                logger.info(f"Red: {matchup.get('red_provider', 'auto')}/{matchup['red_model']}")
                logger.info(f"Blue: {matchup.get('blue_provider', 'auto')}/{matchup['blue_model']}")
                logger.info(f"{'=' * 80}\n")

                orchestrator = self.orchestrator_factory(
                    scenario=scenario,
                    red_model=matchup['red_model'],
                    blue_model=matchup['blue_model'],
                    red_provider=matchup.get('red_provider'),
                    blue_provider=matchup.get('blue_provider'),
                    max_rounds=rounds_per_game
                )

                game_id = orchestrator.start_game(
                    scenario=scenario,
                    max_rounds=rounds_per_game
                )

                game_result = self._get_game_result(game_id)
                self._link_game_to_tournament(tournament_id, game_id, idx)

                matchup_result = {
                    'matchup_number': idx,
                    'red_model': matchup['red_model'],
                    'blue_model': matchup['blue_model'],
                    'red_provider': matchup.get('red_provider', 'auto'),
                    'blue_provider': matchup.get('blue_provider', 'auto'),
                    'game_result': game_result
                }

                results['matchups'].append(matchup_result)

                logger.info(f"\nMatchup {idx} Complete:")
                logger.info(f"  Winner: {game_result['winner']}")
                logger.info(f"  Score: Red {game_result['red_score']} - Blue {game_result['blue_score']}")

                if idx < len(matchups):
                    time.sleep(3)

            # Generate leaderboard
            results['leaderboard'] = self._generate_leaderboard(results['matchups'])

            self._store_tournament_results(tournament_id, results)
            self._update_tournament_status(tournament_id, 'completed')

            self._print_comparison_report(results)

            return results

        except Exception as e:
            logger.error(f"Tournament failed: {e}", exc_info=True)
            self._update_tournament_status(tournament_id, 'failed')
            raise

    def run_scenario_mastery(
        self,
        scenarios: List[str],
        red_model: str,
        blue_model: str,
        rounds_per_game: int = 30,
        red_provider: str = None,
        blue_provider: str = None
    ) -> Dict:
        """
        Test same models across multiple scenarios

        Args:
            scenarios: List of scenario IDs
            red_model: Red team model
            blue_model: Blue team model
            rounds_per_game: Rounds per game
            red_provider: Optional provider
            blue_provider: Optional provider

        Returns:
            Tournament results
        """
        tournament_id = self.create_tournament(
            name=f"Scenario Mastery: {red_model} vs {blue_model}",
            tournament_type="scenario_mastery",
            config={
                "scenarios": scenarios,
                "red_model": red_model,
                "blue_model": blue_model,
                "red_provider": red_provider,
                "blue_provider": blue_provider,
                "rounds_per_game": rounds_per_game
            },
            description=f"Test models across {len(scenarios)} scenarios"
        )

        self.current_tournament_id = tournament_id
        self._update_tournament_status(tournament_id, 'running')

        logger.info("=" * 80)
        logger.info(f"TOURNAMENT: Scenario Mastery")
        logger.info(f"Red: {red_provider or 'auto'}/{red_model}")
        logger.info(f"Blue: {blue_provider or 'auto'}/{blue_model}")
        logger.info(f"Scenarios: {len(scenarios)}")
        logger.info("=" * 80)

        results = {
            'tournament_id': tournament_id,
            'scenarios': [],
            'summary': {
                'red_wins': 0,
                'blue_wins': 0,
                'draws': 0
            }
        }

        try:
            for idx, scenario in enumerate(scenarios, 1):
                logger.info(f"\n{'=' * 80}")
                logger.info(f"SCENARIO {idx}/{len(scenarios)}: {scenario}")
                logger.info(f"{'=' * 80}\n")

                orchestrator = self.orchestrator_factory(
                    scenario=scenario,
                    red_model=red_model,
                    blue_model=blue_model,
                    red_provider=red_provider,
                    blue_provider=blue_provider,
                    max_rounds=rounds_per_game
                )

                game_id = orchestrator.start_game(
                    scenario=scenario,
                    max_rounds=rounds_per_game
                )

                game_result = self._get_game_result(game_id)
                self._link_game_to_tournament(tournament_id, game_id, idx)

                scenario_result = {
                    'scenario': scenario,
                    'game_result': game_result
                }

                results['scenarios'].append(scenario_result)

                if game_result['winner'] == 'red':
                    results['summary']['red_wins'] += 1
                elif game_result['winner'] == 'blue':
                    results['summary']['blue_wins'] += 1
                else:
                    results['summary']['draws'] += 1

                logger.info(f"\nScenario {scenario} Complete:")
                logger.info(f"  Winner: {game_result['winner']}")
                logger.info(f"  Overall: Red {results['summary']['red_wins']} - "
                          f"Blue {results['summary']['blue_wins']} - "
                          f"Draws {results['summary']['draws']}")

                if idx < len(scenarios):
                    time.sleep(3)

            self._store_tournament_results(tournament_id, results)
            self._update_tournament_status(tournament_id, 'completed')

            self._print_mastery_report(results)

            return results

        except Exception as e:
            logger.error(f"Tournament failed: {e}", exc_info=True)
            self._update_tournament_status(tournament_id, 'failed')
            raise

    # ============================================================================
    # Helper Methods
    # ============================================================================

    def _get_game_result(self, game_id: str) -> Dict:
        """Retrieve game results from database"""
        with self.db.get_cursor() as cur:
            cur.execute("""
                SELECT
                    game_id,
                    scenario,
                    red_team_model,
                    blue_team_model,
                    red_score,
                    blue_score,
                    winner,
                    start_time,
                    end_time,
                    EXTRACT(EPOCH FROM (end_time - start_time)) as duration_seconds
                FROM games
                WHERE game_id = %s
            """, (game_id,))

            row = cur.fetchone()
            if not row:
                raise ValueError(f"Game {game_id} not found")

            return {
                'game_id': row[0],
                'scenario': row[1],
                'red_model': row[2],
                'blue_model': row[3],
                'red_score': row[4],
                'blue_score': row[5],
                'winner': row[6],
                'start_time': row[7],
                'end_time': row[8],
                'duration_seconds': row[9]
            }

    def _link_game_to_tournament(self, tournament_id: str, game_id: str, game_number: int):
        """Link a game to a tournament"""
        with self.db.get_cursor() as cur:
            # Create table if doesn't exist
            cur.execute("""
                CREATE TABLE IF NOT EXISTS tournament_games (
                    tournament_id UUID REFERENCES tournaments(tournament_id),
                    game_id UUID REFERENCES games(game_id),
                    game_number INT NOT NULL,
                    PRIMARY KEY (tournament_id, game_id)
                )
            """)

            cur.execute("""
                INSERT INTO tournament_games (tournament_id, game_id, game_number)
                VALUES (%s, %s, %s)
            """, (tournament_id, game_id, game_number))

            self.db.conn.commit()

    def _update_tournament_status(self, tournament_id: str, status: str):
        """Update tournament status"""
        with self.db.get_cursor() as cur:
            if status == 'running':
                cur.execute("""
                    UPDATE tournaments
                    SET status = %s, start_time = NOW()
                    WHERE tournament_id = %s
                """, (status, tournament_id))
            elif status in ['completed', 'failed']:
                cur.execute("""
                    UPDATE tournaments
                    SET status = %s, end_time = NOW()
                    WHERE tournament_id = %s
                """, (status, tournament_id))
            else:
                cur.execute("""
                    UPDATE tournaments
                    SET status = %s
                    WHERE tournament_id = %s
                """, (status, tournament_id))

            self.db.conn.commit()

    def _store_tournament_results(self, tournament_id: str, results: Dict):
        """Store tournament results"""
        with self.db.get_cursor() as cur:
            cur.execute("""
                UPDATE tournaments
                SET config = config || jsonb_build_object('results', %s::jsonb)
                WHERE tournament_id = %s
            """, (json.dumps(results), tournament_id))

            self.db.conn.commit()

    def _calculate_tournament_stats(self, games: List[Dict]) -> Dict:
        """Calculate tournament statistics"""
        if not games:
            return {}

        red_wins = sum(1 for g in games if g['winner'] == 'red')
        blue_wins = sum(1 for g in games if g['winner'] == 'blue')
        draws = sum(1 for g in games if g['winner'] not in ['red', 'blue'])

        total_red_score = sum(g['red_score'] for g in games)
        total_blue_score = sum(g['blue_score'] for g in games)

        return {
            'total_games': len(games),
            'red_wins': red_wins,
            'blue_wins': blue_wins,
            'draws': draws,
            'avg_red_score': total_red_score / len(games),
            'avg_blue_score': total_blue_score / len(games),
            'total_red_score': total_red_score,
            'total_blue_score': total_blue_score,
            'red_win_rate': red_wins / len(games) * 100,
            'blue_win_rate': blue_wins / len(games) * 100
        }

    def _generate_leaderboard(self, matchups: List[Dict]) -> List[Dict]:
        """Generate leaderboard from matchups"""
        model_stats = defaultdict(lambda: {'wins': 0, 'losses': 0, 'draws': 0, 'total_score': 0, 'games': 0})

        for matchup in matchups:
            result = matchup['game_result']

            # Red team stats
            red_key = f"{matchup['red_provider']}/{matchup['red_model']}"
            model_stats[red_key]['games'] += 1
            model_stats[red_key]['total_score'] += result['red_score']

            if result['winner'] == 'red':
                model_stats[red_key]['wins'] += 1
            elif result['winner'] == 'blue':
                model_stats[red_key]['losses'] += 1
            else:
                model_stats[red_key]['draws'] += 1

            # Blue team stats
            blue_key = f"{matchup['blue_provider']}/{matchup['blue_model']}"
            model_stats[blue_key]['games'] += 1
            model_stats[blue_key]['total_score'] += result['blue_score']

            if result['winner'] == 'blue':
                model_stats[blue_key]['wins'] += 1
            elif result['winner'] == 'red':
                model_stats[blue_key]['losses'] += 1
            else:
                model_stats[blue_key]['draws'] += 1

        # Convert to leaderboard
        leaderboard = []
        for model, stats in model_stats.items():
            win_rate = stats['wins'] / stats['games'] * 100 if stats['games'] > 0 else 0
            avg_score = stats['total_score'] / stats['games'] if stats['games'] > 0 else 0

            leaderboard.append({
                'model': model,
                'wins': stats['wins'],
                'losses': stats['losses'],
                'draws': stats['draws'],
                'win_rate': win_rate,
                'avg_score': avg_score,
                'total_score': stats['total_score'],
                'games': stats['games']
            })

        # Sort by win rate, then avg score
        leaderboard.sort(key=lambda x: (x['win_rate'], x['avg_score']), reverse=True)

        return leaderboard

    def _print_tournament_report(self, results: Dict):
        """Print learning progression tournament report"""
        stats = results['statistics']

        logger.info("\n" + "=" * 80)
        logger.info("TOURNAMENT COMPLETE - LEARNING PROGRESSION")
        logger.info("=" * 80)
        logger.info(f"Total Games: {stats['total_games']}")
        logger.info(f"Red Wins: {stats['red_wins']} ({stats['red_win_rate']:.1f}%)")
        logger.info(f"Blue Wins: {stats['blue_wins']} ({stats['blue_win_rate']:.1f}%)")
        logger.info(f"Draws: {stats['draws']}")
        logger.info(f"Average Red Score: {stats['avg_red_score']:.1f}")
        logger.info(f"Average Blue Score: {stats['avg_blue_score']:.1f}")
        logger.info("=" * 80)

        # Game by game breakdown
        logger.info("\nGame History:")
        for i, game in enumerate(results['games'], 1):
            logger.info(f"  Game {i}: {game['winner']} won "
                       f"(R:{game['red_score']} B:{game['blue_score']})")

    def _print_comparison_report(self, results: Dict):
        """Print model comparison report"""
        logger.info("\n" + "=" * 80)
        logger.info("TOURNAMENT COMPLETE - MODEL COMPARISON")
        logger.info("=" * 80)

        logger.info("\nLEADERBOARD:")
        logger.info(f"{'Rank':<6}{'Model':<40}{'W-L-D':<12}{'Win%':<10}{'Avg Score':<12}")
        logger.info("-" * 80)

        for rank, entry in enumerate(results['leaderboard'], 1):
            wld = f"{entry['wins']}-{entry['losses']}-{entry['draws']}"
            logger.info(f"{rank:<6}{entry['model']:<40}{wld:<12}"
                       f"{entry['win_rate']:>6.1f}%   {entry['avg_score']:>8.1f}")

        logger.info("=" * 80)

    def _print_mastery_report(self, results: Dict):
        """Print scenario mastery report"""
        summary = results['summary']

        logger.info("\n" + "=" * 80)
        logger.info("TOURNAMENT COMPLETE - SCENARIO MASTERY")
        logger.info("=" * 80)
        logger.info(f"Total Scenarios: {len(results['scenarios'])}")
        logger.info(f"Red Wins: {summary['red_wins']}")
        logger.info(f"Blue Wins: {summary['blue_wins']}")
        logger.info(f"Draws: {summary['draws']}")
        logger.info("=" * 80)

        logger.info("\nScenario Results:")
        for result in results['scenarios']:
            game = result['game_result']
            logger.info(f"  {result['scenario']}: {game['winner']} won "
                       f"(R:{game['red_score']} B:{game['blue_score']})")
        logger.info("=" * 80)


if __name__ == "__main__":
    print("Tournament Manager module loaded successfully")
