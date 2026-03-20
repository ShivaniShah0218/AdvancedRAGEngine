import React, { useState, useEffect, useRef } from 'react';
import Modal from './Modal';
import { listDocuments, uploadDocument, deleteDocument, listKBAuditLogs } from '../api';

export default function KnowledgeBaseModal({ isOpen, onClose, orgId }) {
  const [documents, setDocuments] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [activeTab, setActiveTab] = useState('documents');
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const fileInputRef = useRef(null);

  useEffect(() => {
    if (isOpen && orgId) {
      fetchDocuments();
      fetchAuditLogs();
    }
  }, [isOpen, orgId]);

  const fetchDocuments = async () => {
    try {
      const data = await listDocuments(orgId);
      setDocuments(data.documents || []);
    } catch (err) {
      setError('Failed to load documents');
    }
  };

  const fetchAuditLogs = async () => {
    try {
      const data = await listKBAuditLogs(orgId);
      setAuditLogs(data.logs || []);
    } catch (err) {
      console.error('Failed to load audit logs', err);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setUploading(true);
    setError('');
    setSuccess('');
    try {
      await uploadDocument(orgId, file);
      setSuccess(`"${file.name}" uploaded successfully`);
      fetchDocuments();
      fetchAuditLogs();
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed');
    } finally {
      setUploading(false);
      fileInputRef.current.value = '';
    }
  };

  const handleDelete = async (doc) => {
    if (!window.confirm(`Delete "${doc.filename}"?`)) return;
    setError('');
    setSuccess('');
    try {
      await deleteDocument(orgId, doc.doc_id);
      setSuccess(`"${doc.filename}" deleted`);
      fetchDocuments();
      fetchAuditLogs();
    } catch (err) {
      setError(err.response?.data?.detail || 'Delete failed');
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={`Knowledge Base — ${orgId}`}>
      <div className="kb-tabs">
        <button
          className={`kb-tab ${activeTab === 'documents' ? 'active' : ''}`}
          onClick={() => setActiveTab('documents')}
        >
          📄 Documents
        </button>
        <button
          className={`kb-tab ${activeTab === 'audit' ? 'active' : ''}`}
          onClick={() => setActiveTab('audit')}
        >
          📋 Audit Log
        </button>
      </div>

      {error && <div className="modal-error">{error}</div>}
      {success && <div className="modal-success">{success}</div>}

      {activeTab === 'documents' && (
        <div className="kb-documents">
          <div className="kb-upload-row">
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.txt,.doc,.docx,.csv,.xlsx,.xls"
              onChange={handleFileUpload}
              disabled={uploading}
              style={{ display: 'none' }}
              id="kb-file-input"
            />
            <label htmlFor="kb-file-input" className={`btn-upload ${uploading ? 'disabled' : ''}`}>
              {uploading ? 'Uploading...' : '+ Add Document'}
            </label>
          </div>

          {documents.length === 0 ? (
            <p className="empty-state">No documents in this knowledge base yet.</p>
          ) : (
            <table className="kb-table">
              <thead>
                <tr>
                  <th>Filename</th>
                  <th>Uploaded by</th>
                  <th>Date</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {documents.map((doc) => (
                  <tr key={doc.doc_id}>
                    <td>{doc.filename}</td>
                    <td>{doc.uploaded_by}</td>
                    <td>{new Date(doc.uploaded_at).toLocaleString()}</td>
                    <td>
                      <button className="btn-danger-small" onClick={() => handleDelete(doc)}>
                        🗑 Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      {activeTab === 'audit' && (
        <div className="kb-audit">
          {auditLogs.length === 0 ? (
            <p className="empty-state">No audit log entries yet.</p>
          ) : (
            <table className="kb-table">
              <thead>
                <tr>
                  <th>Action</th>
                  <th>Document</th>
                  <th>Performed by</th>
                  <th>Timestamp</th>
                </tr>
              </thead>
              <tbody>
                {auditLogs.map((log) => (
                  <tr key={log.id}>
                    <td>
                      <span className={`action-badge ${log.action}`}>{log.action}</span>
                    </td>
                    <td>{log.details || log.doc_id || '—'}</td>
                    <td>{log.performed_by}</td>
                    <td>{new Date(log.timestamp).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </Modal>
  );
}
