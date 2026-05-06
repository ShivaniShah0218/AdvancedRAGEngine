import React, { useState, useEffect } from 'react';
import Login from './components/Login';
import Navigation from './components/Navigation';
import Dashboard from './components/Dashboard';
import QueryPage from './components/QueryPage';
import { setToken } from './api';
import './styles/App.css';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState('dashboard'); // 'dashboard' | 'query'

  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    const storedToken = localStorage.getItem('token');
    if (storedUser && storedToken) {
      try {
        const parsedUser = JSON.parse(storedUser);
        setUser(parsedUser);
        setToken(storedToken);
      } catch (err) {
        localStorage.removeItem('user');
        localStorage.removeItem('token');
      }
    }
    setLoading(false);
  }, []);

  const handleLoginSuccess = () => {
    const storedUser = localStorage.getItem('user');
    const storedToken = localStorage.getItem('token');
    if (storedUser && storedToken) {
      const u = JSON.parse(storedUser);
      setUser(u);
      setToken(storedToken);
    }
  };

  const handleLogout = () => {
    setUser(null);
    setPage('dashboard');
    localStorage.removeItem('user');
    localStorage.removeItem('token');
    setToken(null);
  };

  if (loading) return <div className="app-loading">Loading...</div>;

  return (
    <div className="app">
      {user ? (
        <>
          <Navigation user={user} onLogout={handleLogout} page={page} onNavigate={setPage} />
          {page === 'dashboard' && <Dashboard user={user} onNavigate={setPage} />}
          {page === 'query' && <QueryPage user={user} />}
        </>
      ) : (
        <Login onLoginSuccess={handleLoginSuccess} />
      )}
    </div>
  );
}

export default App;
