"""
Project Icarus Dashboard - Backend API
Real-time game monitoring and replay system
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
import psycopg2
import psycopg2.extras
import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Database connection
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://gamemaster:secure_password_here@database:5432/cyberrange')


def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(DATABASE_URL)


# ============================================================================
# REST API Endpoints
# ============================================================================

@app.route('/')
def home():
    """API home endpoint"""
    return jsonify({
        'message': 'Project Icarus Dashboard API',
        'version': '2.0.0',
        'endpoints': {
            'games': '/api/games',
            'game_detail': '/api/games/<game_id>',
            'rounds': '/api/games/<game_id>/rounds',
            'events': '/api/games/<game_id>/events',
            'commands': '/api/games/<game_id>/commands',
            'stats': '/api/stats',
            'leaderboard': '/api/leaderboard',
            'replay': '/api/games/<game_id>/replay'
        },
        'websocket': {
            'connect': 'ws://localhost:5001',
            'events': ['join_game', 'game_update', 'round_complete', 'game_over']
        }
    })


@app.route('/api/health')
def health():
    """Health check endpoint"""
    try:
        conn = get_db_connection()
        conn.close()
        return jsonify({'status': 'healthy', 'database': 'connected'})
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500


@app.route('/api/games')
def list_games():
    """List all games with pagination"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        status = request.args.get('status')  # running, completed

        offset = (page - 1) * per_page

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Build query
        query = """
            SELECT
                game_id,
                start_time,
                end_time,
                red_team_model,
                blue_team_model,
                scenario,
                red_score,
                blue_score,
                winner,
                status,
                EXTRACT(EPOCH FROM (COALESCE(end_time, NOW()) - start_time)) as duration_seconds
            FROM games
        """

        params = []
        if status:
            query += " WHERE status = %s"
            params.append(status)

        query += " ORDER BY start_time DESC LIMIT %s OFFSET %s"
        params.extend([per_page, offset])

        cur.execute(query, params)
        games = cur.fetchall()

        # Get total count
        count_query = "SELECT COUNT(*) FROM games"
        if status:
            count_query += " WHERE status = %s"
            cur.execute(count_query, [status] if status else [])
        else:
            cur.execute(count_query)
        total = cur.fetchone()['count']

        conn.close()

        return jsonify({
            'games': [dict(g) for g in games],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/games/<game_id>')
def get_game(game_id):
    """Get detailed game information"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Get game details
        cur.execute("""
            SELECT
                game_id,
                start_time,
                end_time,
                red_team_model,
                blue_team_model,
                scenario,
                red_score,
                blue_score,
                winner,
                status,
                config,
                EXTRACT(EPOCH FROM (COALESCE(end_time, NOW()) - start_time)) as duration_seconds
            FROM games
            WHERE game_id = %s
        """, (game_id,))

        game = cur.fetchone()

        if not game:
            conn.close()
            return jsonify({'error': 'Game not found'}), 404

        # Get round count
        cur.execute("SELECT COUNT(*) as count FROM rounds WHERE game_id = %s", (game_id,))
        round_count = cur.fetchone()['count']

        # Get event count
        cur.execute("SELECT COUNT(*) as count FROM events WHERE game_id = %s", (game_id,))
        event_count = cur.fetchone()['count']

        conn.close()

        result = dict(game)
        result['round_count'] = round_count
        result['event_count'] = event_count

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/games/<game_id>/rounds')
def get_rounds(game_id):
    """Get all rounds for a game"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cur.execute("""
            SELECT
                round_id,
                round_number,
                timestamp,
                phase,
                red_reasoning,
                red_action,
                red_success,
                red_points_earned,
                blue_reasoning,
                blue_action,
                blue_success,
                blue_points_earned,
                red_execution_time_ms,
                blue_execution_time_ms
            FROM rounds
            WHERE game_id = %s
            ORDER BY round_number ASC
        """, (game_id,))

        rounds = cur.fetchall()
        conn.close()

        return jsonify({
            'game_id': game_id,
            'rounds': [dict(r) for r in rounds]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/games/<game_id>/events')
def get_events(game_id):
    """Get all events for a game"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cur.execute("""
            SELECT
                event_id,
                round_id,
                timestamp,
                event_type,
                team,
                description,
                points_awarded,
                metadata
            FROM events
            WHERE game_id = %s
            ORDER BY timestamp ASC
        """, (game_id,))

        events = cur.fetchall()
        conn.close()

        return jsonify({
            'game_id': game_id,
            'events': [dict(e) for e in events]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/games/<game_id>/commands')
def get_commands(game_id):
    """Get all commands for a game"""
    try:
        limit = int(request.args.get('limit', 100))
        team = request.args.get('team')  # red or blue

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        query = """
            SELECT
                log_id,
                round_id,
                timestamp,
                team,
                container,
                command,
                exit_code,
                stdout,
                stderr,
                execution_time_ms
            FROM command_log
            WHERE game_id = %s
        """

        params = [game_id]
        if team:
            query += " AND team = %s"
            params.append(team)

        query += " ORDER BY timestamp DESC LIMIT %s"
        params.append(limit)

        cur.execute(query, params)
        commands = cur.fetchall()
        conn.close()

        return jsonify({
            'game_id': game_id,
            'commands': [dict(c) for c in commands]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/games/<game_id>/replay')
def get_replay(game_id):
    """Get complete game data for replay"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Get game info
        cur.execute("SELECT * FROM games WHERE game_id = %s", (game_id,))
        game = cur.fetchone()

        if not game:
            conn.close()
            return jsonify({'error': 'Game not found'}), 404

        # Get all rounds with full details
        cur.execute("""
            SELECT * FROM rounds
            WHERE game_id = %s
            ORDER BY round_number ASC
        """, (game_id,))
        rounds = cur.fetchall()

        # Get all events
        cur.execute("""
            SELECT * FROM events
            WHERE game_id = %s
            ORDER BY timestamp ASC
        """, (game_id,))
        events = cur.fetchall()

        conn.close()

        return jsonify({
            'game': dict(game),
            'rounds': [dict(r) for r in rounds],
            'events': [dict(e) for e in events]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats')
def get_stats():
    """Get overall statistics"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Total games
        cur.execute("SELECT COUNT(*) as total FROM games")
        total_games = cur.fetchone()['total']

        # Games by status
        cur.execute("""
            SELECT status, COUNT(*) as count
            FROM games
            GROUP BY status
        """)
        games_by_status = {row['status']: row['count'] for row in cur.fetchall()}

        # Win statistics
        cur.execute("""
            SELECT winner, COUNT(*) as count
            FROM games
            WHERE winner IS NOT NULL
            GROUP BY winner
        """)
        wins_by_team = {row['winner']: row['count'] for row in cur.fetchall()}

        # Average scores
        cur.execute("""
            SELECT
                AVG(red_score) as avg_red_score,
                AVG(blue_score) as avg_blue_score,
                AVG(EXTRACT(EPOCH FROM (end_time - start_time))) as avg_duration_seconds
            FROM games
            WHERE status = 'completed'
        """)
        averages = cur.fetchone()

        # Scenarios played
        cur.execute("""
            SELECT scenario, COUNT(*) as count
            FROM games
            GROUP BY scenario
            ORDER BY count DESC
        """)
        scenarios = [dict(row) for row in cur.fetchall()]

        conn.close()

        return jsonify({
            'total_games': total_games,
            'games_by_status': games_by_status,
            'wins_by_team': wins_by_team,
            'averages': dict(averages) if averages else {},
            'scenarios': scenarios
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/leaderboard')
def get_leaderboard():
    """Get leaderboard of top games"""
    try:
        metric = request.args.get('metric', 'red_score')  # red_score, blue_score, duration
        limit = int(request.args.get('limit', 10))

        valid_metrics = ['red_score', 'blue_score', 'duration_seconds']
        if metric not in valid_metrics:
            metric = 'red_score'

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        if metric == 'duration_seconds':
            order_col = "EXTRACT(EPOCH FROM (end_time - start_time))"
        else:
            order_col = metric

        cur.execute(f"""
            SELECT
                game_id,
                start_time,
                scenario,
                red_team_model,
                blue_team_model,
                red_score,
                blue_score,
                winner,
                EXTRACT(EPOCH FROM (end_time - start_time)) as duration_seconds
            FROM games
            WHERE status = 'completed'
            ORDER BY {order_col} DESC
            LIMIT %s
        """, (limit,))

        leaderboard = cur.fetchall()
        conn.close()

        return jsonify({
            'metric': metric,
            'leaderboard': [dict(g) for g in leaderboard]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# WebSocket Events
# ============================================================================

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f'Client connected: {request.sid}')
    emit('connected', {'message': 'Connected to Project Icarus Dashboard'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f'Client disconnected: {request.sid}')


@socketio.on('join_game')
def handle_join_game(data):
    """Join a game room for real-time updates"""
    game_id = data.get('game_id')
    if game_id:
        join_room(game_id)
        emit('joined_game', {'game_id': game_id})
        print(f'Client {request.sid} joined game {game_id}')


@socketio.on('leave_game')
def handle_leave_game(data):
    """Leave a game room"""
    game_id = data.get('game_id')
    if game_id:
        leave_room(game_id)
        emit('left_game', {'game_id': game_id})
        print(f'Client {request.sid} left game {game_id}')


# ============================================================================
# Utility functions for orchestrator to call
# ============================================================================

def broadcast_game_update(game_id, data):
    """Broadcast game update to all clients watching this game"""
    socketio.emit('game_update', data, room=game_id)


def broadcast_round_complete(game_id, round_data):
    """Broadcast round completion"""
    socketio.emit('round_complete', round_data, room=game_id)


def broadcast_game_over(game_id, final_data):
    """Broadcast game over"""
    socketio.emit('game_over', final_data, room=game_id)


if __name__ == '__main__':
    print("Starting Project Icarus Dashboard API...")
    print(f"API: http://localhost:5001")
    print(f"WebSocket: ws://localhost:5001")
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)
