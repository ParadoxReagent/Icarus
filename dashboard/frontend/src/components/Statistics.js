import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001';

function Statistics() {
  const [stats, setStats] = useState(null);
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchStatistics();
  }, []);

  const fetchStatistics = async () => {
    try {
      const [statsRes, leaderboardRes] = await Promise.all([
        axios.get(`${API_URL}/api/stats`),
        axios.get(`${API_URL}/api/leaderboard?metric=red_score&limit=10`)
      ]);

      setStats(statsRes.data);
      setLeaderboard(leaderboardRes.data.leaderboard);
      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading statistics...</div>;
  }

  if (error) {
    return <div className="error">Error loading statistics: {error}</div>;
  }

  return (
    <div>
      <div className="card">
        <h2>Overall Statistics</h2>
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-value">{stats.total_games}</div>
            <div className="stat-label">Total Games</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.games_by_status?.running || 0}</div>
            <div className="stat-label">Running</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.games_by_status?.completed || 0}</div>
            <div className="stat-label">Completed</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.wins_by_team?.red || 0}</div>
            <div className="stat-label red-team">Red Wins</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.wins_by_team?.blue || 0}</div>
            <div className="stat-label blue-team">Blue Wins</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">
              {stats.averages?.avg_red_score ? Math.round(stats.averages.avg_red_score) : 0}
            </div>
            <div className="stat-label">Avg Red Score</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">
              {stats.averages?.avg_blue_score ? Math.round(stats.averages.avg_blue_score) : 0}
            </div>
            <div className="stat-label">Avg Blue Score</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">
              {stats.averages?.avg_duration_seconds
                ? `${Math.floor(stats.averages.avg_duration_seconds / 60)}m`
                : '0m'}
            </div>
            <div className="stat-label">Avg Duration</div>
          </div>
        </div>
      </div>

      <div className="card">
        <h2>Scenarios</h2>
        <div style={{ display: 'grid', gap: '1rem' }}>
          {stats.scenarios && stats.scenarios.length > 0 ? (
            stats.scenarios.map((scenario) => (
              <div key={scenario.scenario} style={{ background: '#252d4a', padding: '1rem', borderRadius: '0.5rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>{scenario.scenario}</span>
                  <span style={{ color: '#667eea', fontWeight: 'bold' }}>{scenario.count} games</span>
                </div>
              </div>
            ))
          ) : (
            <div className="empty-state">No scenario data</div>
          )}
        </div>
      </div>

      <div className="card">
        <h2>Leaderboard - Top Scoring Red Teams</h2>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '2px solid #667eea' }}>
                <th style={{ padding: '0.75rem', textAlign: 'left' }}>#</th>
                <th style={{ padding: '0.75rem', textAlign: 'left' }}>Game ID</th>
                <th style={{ padding: '0.75rem', textAlign: 'left' }}>Scenario</th>
                <th style={{ padding: '0.75rem', textAlign: 'right' }}>Red Score</th>
                <th style={{ padding: '0.75rem', textAlign: 'right' }}>Blue Score</th>
                <th style={{ padding: '0.75rem', textAlign: 'left' }}>Winner</th>
              </tr>
            </thead>
            <tbody>
              {leaderboard.map((game, index) => (
                <tr key={game.game_id} style={{ borderBottom: '1px solid #252d4a' }}>
                  <td style={{ padding: '0.75rem' }}>{index + 1}</td>
                  <td style={{ padding: '0.75rem', fontFamily: 'monospace', fontSize: '0.85rem' }}>
                    {game.game_id.substring(0, 8)}...
                  </td>
                  <td style={{ padding: '0.75rem' }}>{game.scenario}</td>
                  <td style={{ padding: '0.75rem', textAlign: 'right', color: '#fc8181', fontWeight: 'bold' }}>
                    {game.red_score}
                  </td>
                  <td style={{ padding: '0.75rem', textAlign: 'right', color: '#63b3ed', fontWeight: 'bold' }}>
                    {game.blue_score}
                  </td>
                  <td style={{ padding: '0.75rem' }}>
                    <span className={game.winner === 'red' ? 'red-team' : 'blue-team'}>
                      {game.winner ? game.winner.toUpperCase() : '-'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default Statistics;
