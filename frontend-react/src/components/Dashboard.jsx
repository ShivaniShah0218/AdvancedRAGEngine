import React, { useState, useEffect } from 'react';
import { listOrgs } from '../api';
import CreateOrgModal from './CreateOrgModal';
import CreateUserModal from './CreateUserModal';
import UserManagementModal from './UserManagementModal';
import '../styles/Dashboard.css';

export default function Dashboard({ user }) {
  const [orgs, setOrgs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  const [showCreateOrgModal, setShowCreateOrgModal] = useState(false);
  const [showCreateUserModal, setShowCreateUserModal] = useState(false);
  const [showUserManagementModal, setShowUserManagementModal] = useState(false);
  const [selectedOrgId, setSelectedOrgId] = useState('');

  useEffect(() => {
    const token = localStorage.getItem('token');
    console.log('Token in localStorage:', token ? 'EXISTS' : 'MISSING');
    console.log('Full user object:', user);
    fetchOrgs();
  }, []);

  const fetchOrgs = async () => {
    try {
      setLoading(true);
      const data = await listOrgs();
      setOrgs(data.orgs || []);
    } catch (err) {
      console.error('ListOrgs error:', err);
      setError('Failed to load organizations');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateOrgSuccess = () => {
    fetchOrgs();
    setShowCreateOrgModal(false);
  };

  const handleCreateUserClick = (orgId) => {
    setSelectedOrgId(orgId);
    setShowCreateUserModal(true);
  };

  const handleCreateUserSuccess = () => {
    fetchOrgs();
    setShowCreateUserModal(false);
  };

  const handleUserManagementClick = (orgId) => {
    setSelectedOrgId(orgId);
    setShowUserManagementModal(true);
  };

  const isAdmin = user?.role === 'admin';
  const isEditor = user?.role === 'editor';

  if (loading) return <div className="dashboard-loading">Loading...</div>;

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <p className="welcome-text">Welcome, {user?.username}!</p>
      </div>

      {error && <div className="dashboard-error">{error}</div>}

      <div className="dashboard-grid">
        {/* Admin section - Create Organization */}
        {isAdmin && (
          <div className="dashboard-card admin-card">
            <div className="card-header">
              <h3>👨‍💼 Admin Controls</h3>
            </div>
            <div className="card-body">
              <p>Create and manage organizations</p>
              <button 
                className="card-btn admin-btn"
                onClick={() => setShowCreateOrgModal(true)}
              >
                + Create Organization
              </button>
            </div>
          </div>
        )}

        {/* Organizations section */}
        <div className="dashboard-card">
          <div className="card-header">
            <h3>🏢 Organizations</h3>
            <span className="badge">{orgs.length}</span>
          </div>
          <div className="card-body">
            {orgs.length > 0 ? (
              <div className="org-list">
                {orgs.map((org) => (
                  <div key={org.org_id} className="org-item-card">
                    <div className="org-info">
                      <span className="org-name">{org.name}</span>
                      {isAdmin && <span className="org-id">{org.org_id}</span>}
                    </div>
                    <div className="org-actions">
                      {(isAdmin || isEditor) && (
                        <>
                          <button 
                            className="btn-small btn-primary"
                            onClick={() => handleCreateUserClick(org.org_id)}
                            title="Create new user"
                          >
                            + User
                          </button>
                          <button 
                            className="btn-small btn-secondary"
                            onClick={() => handleUserManagementClick(org.org_id)}
                            title="View and manage users"
                          >
                            👥 Users
                          </button>
                        </>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="empty-state">No organizations found</p>
            )}
          </div>
        </div>

        {/* User profile */}
        <div className="dashboard-card user-card">
          <div className="card-header">
            <h3>👤 User Profile</h3>
          </div>
          <div className="card-body profile-info">
            <div className="info-row">
              <span className="label">Username:</span>
              <span className="value">{user?.username}</span>
            </div>
            <div className="info-row">
              <span className="label">Role:</span>
              <span className={`value role-badge ${user?.role}`}>{user?.role}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Modals */}
      <CreateOrgModal 
        isOpen={showCreateOrgModal}
        onClose={() => setShowCreateOrgModal(false)}
        onSuccess={handleCreateOrgSuccess}
      />

      <CreateUserModal 
        isOpen={showCreateUserModal}
        onClose={() => setShowCreateUserModal(false)}
        orgId={selectedOrgId}
        currentUserRole={user?.role}
        onSuccess={handleCreateUserSuccess}
      />

      <UserManagementModal 
        isOpen={showUserManagementModal}
        onClose={() => setShowUserManagementModal(false)}
        orgId={selectedOrgId}
        onUserDeleted={() => fetchOrgs()}
      />
    </div>
  );
}