import React, { useState } from 'react';
import { login, setToken } from '../api';
import '../styles/Login.css';

export default function Login({ onLoginSuccess }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await login(username, password);
      console.log('🔍 API Response:', response); // DEBUG
      console.log('🔍 Response role:', response.role); // DEBUG
      
      setToken(response.access_token);

      // Decode JWT payload to extract org_id (no signature verification needed client-side)
      const payloadBase64 = response.access_token.split('.')[1];
      const payload = JSON.parse(atob(payloadBase64));

      const userData = {
        username: username,
        role: response.role,
        org_id: payload.org_id || null,
      };
      console.log('💾 Storing user data:', userData);
      
      localStorage.setItem('user', JSON.stringify(userData));
      localStorage.setItem('token', response.access_token);
      
      onLoginSuccess();
    } catch (err) {
      console.error('❌ Login error:', err);
      setError('Invalid credentials. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <h1>Advanced RAG Engine</h1>
          <p>Sign in to your account</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          {error && <div className="error-message">{error}</div>}

          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              id="username"
              type="text"
              placeholder="Enter your username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={loading}
            />
          </div>

          <button 
            type="submit" 
            className="login-btn"
            disabled={loading}
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>
      </div>
    </div>
  );
}