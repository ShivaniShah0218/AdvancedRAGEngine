import React, { useState, useEffect } from 'react';
import Login from './components/Login';
import Navigation from './components/Navigation';
import Dashboard from './components/Dashboard';
import { setToken } from './api';
import './styles/App.css';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in
    const storedUser = localStorage.getItem('user');
    const storedToken = localStorage.getItem('token');
    
    if (storedUser && storedToken) {
      try {
        const parsedUser = JSON.parse(storedUser);
        setUser(parsedUser);
        // CRITICAL: Restore token to axios defaults
        setToken(storedToken);
        console.log('✅ Restored user from localStorage:', parsedUser);
      } catch (err) {
        console.error('❌ Failed to restore session:', err);
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
      const user = JSON.parse(storedUser);
      setUser(user);
      setToken(storedToken);
      console.log('✅ Login successful, user:', user);
    }
  };

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('user');
    localStorage.removeItem('token');
    setToken(null);
    console.log('✅ User logged out');
  };

  if (loading) return <div className="app-loading">Loading...</div>;

  return (
    <div className="app">
      {user ? (
        <>
          <Navigation user={user} onLogout={handleLogout} />
          <Dashboard user={user} />
        </>
      ) : (
        <Login onLoginSuccess={handleLoginSuccess} />
      )}
    </div>
  );
}

export default App;