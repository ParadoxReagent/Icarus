import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001';

function GameList({ onSelectGame }) {
  const [games, setGames] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all'); // all, running, completed

  useEffect(() => {
    fetchGames();
    const interval = setInterval(fetchGames, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, [filter]);

  const fetchGames = async () => {
    try {
      const params = filter !== 'all' ? { status: filter } : {};
      const response = await axios.get(`${API_URL}/api/games`, { params });
      setGames(response.data.games);
      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading games...</div>;
  }

  if (error) {
    return <div className="error">Error loading games: {error}</div>;
  }

  return (
    <div>
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h2>Game History</h2>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button
              className={`button ${filter === 'all' ? '' : 'secondary'}`}
              onClick={() => setFilter('all')}
              style={{ background: filter === 'all' ? '#667eea' : '#4a5568' }}
            >
              All
            </button>
            <button
              className={`button ${filter === 'running' ? '' : 'secondary'}`}
              onClick={() => setFilter('running')}
              style={{ background: filter === 'running' ? '#667eea' : '#4a5568' }}
            >
              Running
            </button>
            <button
              className={`button ${filter === 'completed' ? '' : 'secondary'}`}
              onClick={() => setFilter('completed')}
              style={{ background: filter === 'completed' ? '#667eea' : '#4a5568' }}
            >
              Completed
            </button>
          </div>
        </div>

        {games.length === 0 ? (
          <div className="empty-state">
            <h3>No games found</h3>
            <p>Start a new game to see it here</p>
          </div>
        ) : (
          <div className="game-list">
            {games.map((game) => (
              <div
                key={game.game_id}
                className="game-item"
                onClick={() => onSelectGame(game.game_id)}
              >
                <div className="game-header">
                  <span className="game-id">{game.game_id.substring(0, 8)}</span>
                  <span className={`status-badge status-${game.status}`}>
                    {game.status.toUpperCase()}
                  </span>
                </div>

                <div className="game-info">
                  <div className="info-item">
                    <span className="info-label">Scenario</span>
                    <span className="info-value">{game.scenario}</span>
                  </div>
                  <div className="info-item">
                    <span className="info-label">Red Score</span>
                    <span className="info-value red-team">{game.red_score}</span>
                  </div>
                  <div className="info-item">
                    <span className="info-label">Blue Score</span>
                    <span className="info-value blue-team">{game.blue_score}</span>
                  </div>
                  <div className="info-item">
                    <span className="info-label">Winner</span>
                    <span className="info-value">
                      {game.winner ? game.winner.toUpperCase() : 'TBD'}
                    </span>
                  </div>
                  <div className="info-item">
                    <span className="info-label">Duration</span>
                    <span className="info-value">
                      {game.duration_seconds
                        ? `${Math.floor(game.duration_seconds / 60)}m ${Math.floor(game.duration_seconds % 60)}s`
                        : 'In progress'}
                    </span>
                  </div>
                  <div className="info-item">
                    <span className="info-label">Started</span>
                    <span className="info-value">
                      {new Date(game.start_time).toLocaleString()}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default GameList;
