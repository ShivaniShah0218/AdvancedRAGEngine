import React, { useState } from 'react';
import { setToken } from '../api';
import '../styles/Navigation.css';

export default function Navigation({ user, onLogout, page, onNavigate }) {
  const [menuOpen, setMenuOpen] = useState(false);

  const handleLogout = () => {
    localStorage.removeItem('user');
    localStorage.removeItem('token');
    setToken(null);
    onLogout();
    setMenuOpen(false);
  };

  const navTo = (p) => {
    onNavigate(p);
    setMenuOpen(false);
  };

  return (
    <nav className="navbar">
      <div className="nav-container">
        <div className="nav-brand">
          <h2>RAG Engine</h2>
        </div>

        <div className="nav-links">
          <button
            className={`nav-link ${page === 'dashboard' ? 'active' : ''}`}
            onClick={() => navTo('dashboard')}
          >
            Dashboard
          </button>
          {/* Query page available to all roles that belong to an org */}
          {user?.org_id && (
            <button
              className={`nav-link ${page === 'query' ? 'active' : ''}`}
              onClick={() => navTo('query')}
            >
              Query
            </button>
          )}
        </div>

        <button
          className="nav-toggle"
          onClick={() => setMenuOpen(!menuOpen)}
        >
          <span></span>
          <span></span>
          <span></span>
        </button>

        <div className={`nav-menu ${menuOpen ? 'active' : ''}`}>
          <div className="nav-user">
            <span className="user-info">
              <span className="username">{user?.username}</span>
              <span className={`user-badge ${user?.role}`}>{user?.role}</span>
            </span>
            <button onClick={handleLogout} className="logout-btn">
              Logout
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}
