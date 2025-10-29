import React, { useState, useEffect } from 'react';
import { io } from 'socket.io-client';
import GameList from './components/GameList';
import GameDetail from './components/GameDetail';
import Statistics from './components/Statistics';
import LiveMonitor from './components/LiveMonitor';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001';

function App() {
  const [view, setView] = useState('games'); // games, stats, live
  const [selectedGame, setSelectedGame] = useState(null);
  const [socket, setSocket] = useState(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    // Initialize WebSocket connection
    const newSocket = io(API_URL);

    newSocket.on('connect', () => {
      console.log('Connected to dashboard');
      setConnected(true);
    });

    newSocket.on('disconnect', () => {
      console.log('Disconnected from dashboard');
      setConnected(false);
    });

    setSocket(newSocket);

    return () => newSocket.close();
  }, []);

  const handleSelectGame = (gameId) => {
    setSelectedGame(gameId);
    setView('detail');
  };

  const handleBackToList = () => {
    setSelectedGame(null);
    setView('games');
  };

  return (
    <div className="app">
      <header className="header">
        <h1>⚔️ Project Icarus Dashboard</h1>
        <p>AI Red Team vs Blue Team Cyber Range - Real-time Monitoring</p>
        <div className="nav">
          <button
            className={`nav-button ${view === 'games' || view === 'detail' ? 'active' : ''}`}
            onClick={() => setView('games')}
          >
            Games
          </button>
          <button
            className={`nav-button ${view === 'stats' ? 'active' : ''}`}
            onClick={() => setView('stats')}
          >
            Statistics
          </button>
          <button
            className={`nav-button ${view === 'live' ? 'active' : ''}`}
            onClick={() => setView('live')}
          >
            Live Monitor
          </button>
          <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <div style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              background: connected ? '#48bb78' : '#f56565'
            }} />
            <span style={{ fontSize: '0.9rem' }}>
              {connected ? 'Connected' : 'Disconnected'}
            </span>
          </div>
        </div>
      </header>

      <div className="container">
        {view === 'games' && !selectedGame && (
          <GameList onSelectGame={handleSelectGame} />
        )}

        {view === 'detail' && selectedGame && (
          <GameDetail gameId={selectedGame} onBack={handleBackToList} socket={socket} />
        )}

        {view === 'stats' && (
          <Statistics />
        )}

        {view === 'live' && (
          <LiveMonitor socket={socket} />
        )}
      </div>
    </div>
  );
}

export default App;
