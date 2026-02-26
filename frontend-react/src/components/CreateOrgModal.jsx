import React, { useState } from 'react';
import { createOrg } from '../api';
import Modal from './Modal';
import '../styles/Modal.css';

export default function CreateOrgModal({ isOpen, onClose, onSuccess }) {
  const [orgId, setOrgId] = useState('');
  const [orgName, setOrgName] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (!orgId.trim() || !orgName.trim()) {
        setError('Organization ID and Name are required');
        setLoading(false);
        return;
      }

      await createOrg(orgId, orgName);
      onSuccess();
      setOrgId('');
      setOrgName('');
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
        setError('Failed to create organization');
      }
      console.error('Create org error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal isOpen={isOpen} title="Create Organization" onClose={onClose}>
      <form onSubmit={handleSubmit} className="modal-form">
        {error && <div className="modal-error">{error}</div>}

        <div className="form-group">
          <label htmlFor="org-id">Organization ID</label>
          <input
            id="org-id"
            type="text"
            placeholder="e.g., acme-corp"
            value={orgId}
            onChange={(e) => setOrgId(e.target.value)}
            disabled={loading}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="org-name">Organization Name</label>
          <input
            id="org-name"
            type="text"
            placeholder="e.g., ACME Corporation"
            value={orgName}
            onChange={(e) => setOrgName(e.target.value)}
            disabled={loading}
            required
          />
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