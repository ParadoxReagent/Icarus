import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001';

function GameDetail({ gameId, onBack, socket }) {
  const [game, setGame] = useState(null);
  const [rounds, setRounds] = useState([]);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('rounds'); // rounds, events

  useEffect(() => {
    fetchGameData();

    // Join game room for real-time updates
    if (socket) {
      socket.emit('join_game', { game_id: gameId });

      socket.on('game_update', handleGameUpdate);
      socket.on('round_complete', handleRoundComplete);

      return () => {
        socket.emit('leave_game', { game_id: gameId });
        socket.off('game_update');
        socket.off('round_complete');
      };
    }
  }, [gameId, socket]);

  const fetchGameData = async () => {
    try {
      const [gameRes, roundsRes, eventsRes] = await Promise.all([
        axios.get(`${API_URL}/api/games/${gameId}`),
        axios.get(`${API_URL}/api/games/${gameId}/rounds`),
        axios.get(`${API_URL}/api/games/${gameId}/events`)
      ]);

      setGame(gameRes.data);
      setRounds(roundsRes.data.rounds);
      setEvents(eventsRes.data.events);
      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  const handleGameUpdate = (data) => {
    console.log('Game update:', data);
    fetchGameData();
  };

  const handleRoundComplete = (data) => {
    console.log('Round complete:', data);
    fetchGameData();
  };

  if (loading) {
    return <div className="loading">Loading game details...</div>;
  }

  if (error) {
    return <div className="error">Error loading game: {error}</div>;
  }

  return (
    <div>
      <button className="button" onClick={onBack} style={{ marginBottom: '1rem' }}>
        ← Back to Games
      </button>

      {/* Game Overview */}
      <div className="card">
        <h2>Game Details</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginTop: '1rem' }}>
          <div>
            <div className="info-label">Game ID</div>
            <div className="info-value" style={{ fontFamily: 'monospace' }}>{gameId.substring(0, 13)}...</div>
          </div>
          <div>
            <div className="info-label">Scenario</div>
            <div className="info-value">{game.scenario}</div>
          </div>
          <div>
            <div className="info-label">Status</div>
            <div className={`status-badge status-${game.status}`}>{game.status.toUpperCase()}</div>
          </div>
          <div>
            <div className="info-label">Rounds Played</div>
            <div className="info-value">{game.round_count}</div>
          </div>
        </div>
      </div>

      {/* Score Display */}
      <div className="card">
        <h2>Current Scores</h2>
        <div className="score-display">
          <div className="team-score">
            <div className="team-label">RED TEAM</div>
            <div className="score red-team">{game.red_score}</div>
            <div style={{ fontSize: '0.9rem', color: '#a0aec0', marginTop: '0.5rem' }}>
              {game.red_team_model}
            </div>
          </div>
          <div style={{ fontSize: '2rem', alignSelf: 'center', color: '#a0aec0' }}>VS</div>
          <div className="team-score">
            <div className="team-label">BLUE TEAM</div>
            <div className="score blue-team">{game.blue_score}</div>
            <div style={{ fontSize: '0.9rem', color: '#a0aec0', marginTop: '0.5rem' }}>
              {game.blue_team_model}
            </div>
          </div>
        </div>
        {game.winner && (
          <div style={{ textAlign: 'center', marginTop: '1rem', fontSize: '1.2rem', fontWeight: 'bold' }}>
            Winner: <span className={game.winner === 'red' ? 'red-team' : 'blue-team'}>
              {game.winner.toUpperCase()} TEAM
            </span>
          </div>
        )}
      </div>

      {/* Tabs */}
      <div className="card">
        <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem', borderBottom: '2px solid #252d4a' }}>
          <button
            className="button"
            onClick={() => setActiveTab('rounds')}
            style={{ background: activeTab === 'rounds' ? '#667eea' : 'transparent', border: 'none' }}
          >
            Rounds ({rounds.length})
          </button>
          <button
            className="button"
            onClick={() => setActiveTab('events')}
            style={{ background: activeTab === 'events' ? '#667eea' : 'transparent', border: 'none' }}
          >
            Events ({events.length})
          </button>
        </div>

        {activeTab === 'rounds' && (
          <div className="rounds-list">
            {rounds.length === 0 ? (
              <div className="empty-state">No rounds yet</div>
            ) : (
              rounds.map((round) => (
                <div key={round.round_id} className="round-item">
                  <div className="round-header">
                    <div>
                      <span className="round-number">Round {round.round_number}</span>
                      <span className="phase-badge" style={{ marginLeft: '1rem' }}>{round.phase}</span>
                    </div>
                    <span style={{ fontSize: '0.85rem', color: '#a0aec0' }}>
                      {new Date(round.timestamp).toLocaleTimeString()}
                    </span>
                  </div>

                  <div className="team-actions">
                    {/* Red Team */}
                    <div className="team-action red">
                      <h4>
                        🔴 Red Team
                        <span className={`success-indicator ${round.red_success ? 'success' : 'failure'}`} />
                      </h4>
                      {round.red_reasoning && (
                        <div style={{ fontSize: '0.85rem', marginBottom: '0.5rem', color: '#a0aec0' }}>
                          {round.red_reasoning.substring(0, 150)}...
                        </div>
                      )}
                      <div className="action-command">{round.red_action}</div>
                      {round.red_points_earned !== 0 && (
                        <div style={{ marginTop: '0.5rem', color: round.red_points_earned > 0 ? '#48bb78' : '#f56565' }}>
                          {round.red_points_earned > 0 ? '+' : ''}{round.red_points_earned} points
                        </div>
                      )}
                    </div>

                    {/* Blue Team */}
                    <div className="team-action blue">
                      <h4>
                        🔵 Blue Team
                        <span className={`success-indicator ${round.blue_success ? 'success' : 'failure'}`} />
                      </h4>
                      {round.blue_reasoning && (
                        <div style={{ fontSize: '0.85rem', marginBottom: '0.5rem', color: '#a0aec0' }}>
                          {round.blue_reasoning.substring(0, 150)}...
                        </div>
                      )}
                      <div className="action-command">{round.blue_action}</div>
                      {round.blue_points_earned !== 0 && (
                        <div style={{ marginTop: '0.5rem', color: round.blue_points_earned > 0 ? '#48bb78' : '#f56565' }}>
                          {round.blue_points_earned > 0 ? '+' : ''}{round.blue_points_earned} points
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === 'events' && (
          <div>
            {events.length === 0 ? (
              <div className="empty-state">No events yet</div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {events.map((event) => (
                  <div key={event.event_id} style={{ background: '#252d4a', padding: '1rem', borderRadius: '0.5rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                      <span style={{ fontWeight: 'bold', color: event.team === 'red' ? '#fc8181' : '#63b3ed' }}>
                        {event.team.toUpperCase()} TEAM
                      </span>
                      <span style={{ fontSize: '0.85rem', color: '#a0aec0' }}>
                        {new Date(event.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                    <div style={{ marginBottom: '0.5rem' }}>{event.description}</div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem' }}>
                      <span style={{ color: '#a0aec0' }}>{event.event_type}</span>
                      <span style={{ color: event.points_awarded > 0 ? '#48bb78' : event.points_awarded < 0 ? '#f56565' : '#a0aec0' }}>
                        {event.points_awarded > 0 ? '+' : ''}{event.points_awarded} points
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default GameDetail;
