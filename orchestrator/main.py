"""
Project Icarus - Main Entry Point
AI Red Team vs Blue Team Cyber Range
"""

import os
import sys
import logging
import time
from dotenv import load_dotenv

from src.database import GameDatabase
from src.red_team_agent import RedTeamAgent
from src.blue_team_agent import BlueTeamAgent
from src.orchestrator import GameOrchestrator
from src.scenario_manager import ScenarioManager

# Load environment variables
load_dotenv()

# Configure logging
log_level = os.getenv('LOG_LEVEL', 'INFO')
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/orchestrator.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Main entry point"""
    logger.info("=" * 80)
    logger.info("PROJECT ICARUS - AI Cyber Range")
    logger.info("AI Red Team vs Blue Team Competition")
    logger.info("=" * 80)

    # Get configuration from environment
    database_url = os.getenv('DATABASE_URL')
    anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
    red_team_model = os.getenv('RED_TEAM_MODEL', 'claude-sonnet-4-5-20250929')
    blue_team_model = os.getenv('BLUE_TEAM_MODEL', 'claude-sonnet-4-5-20250929')
    scenario_id = os.getenv('SCENARIO_ID', 'dvwa_basic_pentest')
    max_rounds = int(os.getenv('MAX_ROUNDS', '30'))
    command_timeout = int(os.getenv('COMMAND_TIMEOUT', '30'))

    # Load scenarios
    scenario_manager = ScenarioManager()
    scenario = scenario_manager.get_scenario(scenario_id)

    if not scenario:
        logger.error(f"Scenario '{scenario_id}' not found")
        logger.info("Available scenarios:")
        for s in scenario_manager.list_scenarios():
            logger.info(f"  - {s['id']}: {s['name']}")
        sys.exit(1)

    logger.info(f"Loaded scenario: {scenario['name']}")
    logger.info(f"Difficulty: {scenario['difficulty']}")
    logger.info(f"Target container: {scenario['target_container']}")

    # Validate configuration
    if not database_url:
        logger.error("DATABASE_URL environment variable not set")
        sys.exit(1)

    if not anthropic_api_key:
        logger.error("ANTHROPIC_API_KEY environment variable not set")
        sys.exit(1)

    logger.info(f"Configuration:")
    logger.info(f"  Red Team Model: {red_team_model}")
    logger.info(f"  Blue Team Model: {blue_team_model}")
    logger.info(f"  Max Rounds: {max_rounds}")
    logger.info(f"  Command Timeout: {command_timeout}s")

    # Wait for database to be ready
    logger.info("Waiting for database connection...")
    for attempt in range(30):
        try:
            db = GameDatabase(database_url)
            logger.info("Database connection established")
            break
        except Exception as e:
            if attempt < 29:
                logger.warning(f"Database not ready, retrying... ({attempt + 1}/30)")
                time.sleep(2)
            else:
                logger.error(f"Failed to connect to database after 30 attempts: {e}")
                sys.exit(1)

    # Wait for containers to be ready
    logger.info("Waiting for game containers to be ready...")
    time.sleep(10)

    try:
        # Initialize AI agents
        logger.info("Initializing AI agents...")
        red_agent = RedTeamAgent(
            api_key=anthropic_api_key,
            model=red_team_model
        )
        logger.info("Red Team agent initialized")

        blue_agent = BlueTeamAgent(
            api_key=anthropic_api_key,
            model=blue_team_model
        )
        logger.info("Blue Team agent initialized")

        # Initialize orchestrator
        orchestrator = GameOrchestrator(
            database=db,
            red_agent=red_agent,
            blue_agent=blue_agent,
            command_timeout=command_timeout
        )
        logger.info("Orchestrator initialized")

        # Start game
        logger.info(f"Starting game with scenario: {scenario_id}")
        logger.info(f"Description: {scenario['description']}")

        game_id = orchestrator.start_game(
            scenario=scenario_id,
            max_rounds=max_rounds
        )

        logger.info(f"Game {game_id} completed")
        logger.info("=" * 80)
        logger.info("GAME SESSION COMPLETE")
        logger.info("=" * 80)

    except KeyboardInterrupt:
        logger.info("\nGame interrupted by user")
        if orchestrator.current_game_id:
            db.end_game(orchestrator.current_game_id, winner=None)
        sys.exit(0)

    except Exception as e:
        logger.error(f"Fatal error during game execution: {e}", exc_info=True)
        if orchestrator.current_game_id:
            db.end_game(orchestrator.current_game_id, winner=None)
        sys.exit(1)

    finally:
        # Cleanup
        if db:
            db.close()


if __name__ == "__main__":
    main()
