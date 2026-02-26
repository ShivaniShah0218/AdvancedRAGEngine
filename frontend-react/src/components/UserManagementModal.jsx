import React, { useState, useEffect } from 'react';
import { listUsers, deleteUser } from '../api';
import Modal from './Modal';
import '../styles/Modal.css';

export default function UserManagementModal({ isOpen, onClose, orgId, onUserDeleted }) {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [deleting, setDeleting] = useState(null);

  useEffect(() => {
    if (isOpen && orgId) {
      fetchUsers();
    }
  }, [isOpen, orgId]);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await listUsers(orgId);
      setUsers(data.users || []);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteUser = async (username) => {
    if (!window.confirm(`Are you sure you want to delete user "${username}"?`)) {
      return;
    }

    try {
      setDeleting(username);
      await deleteUser(orgId, username);
      setUsers(users.filter(u => u.username !== username));
      onUserDeleted();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to delete user');
    } finally {
      setDeleting(null);
    }
  };

  return (
    <Modal isOpen={isOpen} title={`Users in Organization`} onClose={onClose}>
      <div className="user-management">
        {error && <div className="modal-error">{error}</div>}

        {loading ? (
          <div className="loading-state">Loading users...</div>
        ) : users.length > 0 ? (
          <table className="users-table">
            <thead>
              <tr>
                <th>Username</th>
                <th>Role</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user) => (
                <tr key={user.username}>
                  <td>{user.username}</td>
                  <td>
                    <span className={`role-badge ${user.role}`}>
                      {user.role}
                    </span>
                  </td>
                  <td>
                    <button
                      onClick={() => handleDeleteUser(user.username)}
                      className="btn-delete"
                      disabled={deleting === user.username}
                    >
                      {deleting === user.username ? 'Deleting...' : 'Delete'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="empty-state">No users found in this organization</div>
        )}
      </div>
    </Modal>
  );
}