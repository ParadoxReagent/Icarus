import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001';

function LiveMonitor({ socket }) {
  const [runningGames, setRunningGames] = useState([]);
  const [selectedGame, setSelectedGame] = useState(null);
  const [liveData, setLiveData] = useState(null);

  const fetchRunningGames = useCallback(async () => {
    try {
      const response = await axios.get(`${API_URL}/api/games?status=running`);
      setRunningGames(response.data.games);

      // Auto-select first running game if none selected
      if (!selectedGame && response.data.games.length > 0) {
        setSelectedGame(response.data.games[0].game_id);
      }
    } catch (err) {
      console.error('Error fetching running games:', err);
    }
  }, [selectedGame]);

  const fetchGameData = useCallback(async (gameId) => {
    try {
      const [gameRes, roundsRes] = await Promise.all([
        axios.get(`${API_URL}/api/games/${gameId}`),
        axios.get(`${API_URL}/api/games/${gameId}/rounds`)
      ]);

      setLiveData({
        game: gameRes.data,
        rounds: roundsRes.data.rounds
      });
    } catch (err) {
      console.error('Error fetching game data:', err);
    }
  }, []);

  const handleLiveUpdate = useCallback((data) => {
    console.log('Live update:', data);
    if (selectedGame) {
      fetchGameData(selectedGame);
    }
  }, [selectedGame, fetchGameData]);

  const handleRoundComplete = useCallback((data) => {
    console.log('Round complete:', data);
    if (selectedGame) {
      fetchGameData(selectedGame);
    }
  }, [selectedGame, fetchGameData]);

  const handleGameOver = useCallback((data) => {
    console.log('Game over:', data);
    if (selectedGame) {
      fetchGameData(selectedGame);
    }
    // Refresh running games list
    fetchRunningGames();
  }, [selectedGame, fetchGameData, fetchRunningGames]);

  useEffect(() => {
    fetchRunningGames();
    const interval = setInterval(fetchRunningGames, 3000);
    return () => clearInterval(interval);
  }, [fetchRunningGames]);

  useEffect(() => {
    if (selectedGame && socket) {
      socket.emit('join_game', { game_id: selectedGame });

      socket.on('game_update', handleLiveUpdate);
      socket.on('round_complete', handleRoundComplete);
      socket.on('game_over', handleGameOver);

      // Fetch initial data
      fetchGameData(selectedGame);

      return () => {
        socket.emit('leave_game', { game_id: selectedGame });
        socket.off('game_update');
        socket.off('round_complete');
        socket.off('game_over');
      };
    }
  }, [selectedGame, socket, handleLiveUpdate, handleRoundComplete, handleGameOver, fetchGameData]);

  if (runningGames.length === 0) {
    return (
      <div className="card">
        <h2>Live Monitor</h2>
        <div className="empty-state">
          <h3>No games currently running</h3>
          <p>Start a new game to see live updates here</p>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="card">
        <h2>🔴 Live Monitor</h2>
        <div style={{ marginTop: '1rem' }}>
          <label style={{ display: 'block', marginBottom: '0.5rem', color: '#a0aec0' }}>
            Select Running Game:
          </label>
          <select
            value={selectedGame || ''}
            onChange={(e) => setSelectedGame(e.target.value)}
            style={{
              width: '100%',
              padding: '0.75rem',
              background: '#252d4a',
              border: '1px solid #4a5568',
              borderRadius: '0.5rem',
              color: '#e0e0e0',
              fontSize: '1rem'
            }}
          >
            {runningGames.map((game) => (
              <option key={game.game_id} value={game.game_id}>
                {game.scenario} - {game.game_id.substring(0, 8)} (Started: {new Date(game.start_time).toLocaleTimeString()})
              </option>
            ))}
          </select>
        </div>
      </div>

      {liveData && (
        <>
          <div className="card">
            <h2>Current Status</h2>
            <div className="score-display">
              <div className="team-score">
                <div className="team-label">RED TEAM</div>
                <div className="score red-team">{liveData.game.red_score}</div>
              </div>
              <div style={{ fontSize: '2rem', alignSelf: 'center', color: '#a0aec0' }}>VS</div>
              <div className="team-score">
                <div className="team-label">BLUE TEAM</div>
                <div className="score blue-team">{liveData.game.blue_score}</div>
              </div>
            </div>
            <div style={{ textAlign: 'center', marginTop: '1rem' }}>
              <div style={{ fontSize: '1.2rem', marginBottom: '0.5rem' }}>
                Round {liveData.game.round_count}
              </div>
              <div style={{ color: '#a0aec0' }}>
                {liveData.game.scenario} • {liveData.game.status.toUpperCase()}
              </div>
            </div>
          </div>

          <div className="card">
            <h2>Latest Activity</h2>
            {liveData.rounds.length > 0 ? (
              <div>
                {liveData.rounds.slice(-5).reverse().map((round) => (
                  <div key={round.round_id} style={{ marginBottom: '1rem', background: '#252d4a', padding: '1rem', borderRadius: '0.5rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
                      <span style={{ fontWeight: 'bold', color: '#667eea' }}>
                        Round {round.round_number}
                      </span>
                      <span className="phase-badge">{round.phase}</span>
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                      <div>
                        <div style={{ fontSize: '0.85rem', color: '#fc8181', marginBottom: '0.25rem' }}>
                          🔴 Red: {round.red_success ? '✓' : '✗'}
                        </div>
                        <div className="action-command" style={{ fontSize: '0.8rem', padding: '0.5rem' }}>
                          {round.red_action}
                        </div>
                      </div>
                      <div>
                        <div style={{ fontSize: '0.85rem', color: '#63b3ed', marginBottom: '0.25rem' }}>
                          🔵 Blue: {round.blue_success ? '✓' : '✗'}
                        </div>
                        <div className="action-command" style={{ fontSize: '0.8rem', padding: '0.5rem' }}>
                          {round.blue_action}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="empty-state">Waiting for first round...</div>
            )}
          </div>
        </>
      )}
    </div>
  );
}

export default LiveMonitor;
