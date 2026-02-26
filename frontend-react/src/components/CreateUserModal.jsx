import React, { useState } from 'react';
import { createUser } from '../api';
import Modal from './Modal';
import '../styles/Modal.css';

export default function CreateUserModal({ isOpen, onClose, orgId, currentUserRole, onSuccess }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('viewer');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  // Determine available roles based on current user's role
  const getAvailableRoles = () => {
    if (currentUserRole === 'admin') {
      return [
        { value: 'viewer', label: 'Viewer' },
        { value: 'editor', label: 'Editor' },
        { value: 'admin', label: 'Admin' }
      ];
    } else if (currentUserRole === 'editor') {
      return [
        { value: 'viewer', label: 'Viewer' },
        { value: 'editor', label: 'Editor' }
      ];
    }
    // Fallback for other roles (shouldn't happen)
    return [{ value: 'viewer', label: 'Viewer' }];
  };

  const availableRoles = getAvailableRoles();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (!username.trim() || !password.trim()) {
        setError('Username and Password are required');
        setLoading(false);
        return;
      }

      await createUser(orgId, username, password, role);
      onSuccess();
      setUsername('');
      setPassword('');
      setRole('viewer');
      onClose();
    } catch (err) {
      // Handle Pydantic validation errors
      const errorData = err.response?.data;
      if (Array.isArray(errorData?.detail)) {
        // Validation error with array of errors
        const messages = errorData.detail.map(e => e.msg).join(', ');
        setError(messages);
      } else if (errorData?.detail) {
        // Simple error message
        setError(errorData.detail);
      } else {
        setError('Failed to create user');
      }
      console.error('Create user error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal isOpen={isOpen} title="Create User" onClose={onClose}>
      <form onSubmit={handleSubmit} className="modal-form">
        {error && <div className="modal-error">{error}</div>}

        <div className="form-group">
          <label htmlFor="username">Username</label>
          <input
            id="username"
            type="text"
            placeholder="Enter username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            disabled={loading}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="password">Password</label>
          <input
            id="password"
            type="password"
            placeholder="Enter password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            disabled={loading}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="role">Role</label>
          <select
            id="role"
            value={role}
            onChange={(e) => setRole(e.target.value)}
            disabled={loading}
          >
            {availableRoles.map((roleOption) => (
              <option key={roleOption.value} value={roleOption.value}>
                {roleOption.label}
              </option>
            ))}
          </select>
        </div>

        <div className="modal-actions">
          <button type="button" className="btn-cancel" onClick={onClose} disabled={loading}>
            Cancel
          </button>
          <button type="submit" className="btn-submit" disabled={loading}>
            {loading ? 'Creating...' : 'Create'}
          </button>
        </div>
      </form>
    </Modal>
  );
}