import React, { useState, useEffect, useRef } from 'react';
import { submitQuery, getQueryResult, listQueries, getQueryLogs, getQueryMetrics } from '../api';
import '../styles/QueryPage.css';

const POLL_INTERVAL_MS = 2500;

export default function QueryPage({ user }) {
  const [query, setQuery] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [history, setHistory] = useState([]);
  const [selected, setSelected] = useState(null);  // selected query for detail panel
  const [logs, setLogs] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [activeTab, setActiveTab] = useState('answer');
  const pollRef = useRef(null);
  const org_id = user?.org_id;

  useEffect(() => {
    if (org_id) fetchHistory();
    return () => clearInterval(pollRef.current);
  }, [org_id]);

  const fetchHistory = async () => {
    try {
      const data = await listQueries(org_id);
      setHistory(data.queries || []);
    } catch (e) {
      console.error('Failed to load query history', e);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    setSubmitting(true);
    setError('');
    try {
      const res = await submitQuery(org_id, query.trim());
      setQuery('');
      // Add pending entry to history immediately
      const pending = {
        query_id: res.query_id,
        query_text: query.trim(),
        status: 'pending',
        answer: null,
        created_at: new Date().toISOString(),
        completed_at: null,
      };
      setHistory(prev => [pending, ...prev]);
      setSelected(pending);
      setLogs([]);
      setMetrics(null);
      setActiveTab('answer');
      startPolling(res.query_id);
    } catch (e) {
      setError(e.response?.data?.detail || 'Failed to submit query');
    } finally {
      setSubmitting(false);
    }
  };

  const startPolling = (query_id) => {
    clearInterval(pollRef.current);
    pollRef.current = setInterval(async () => {
      try {
        const result = await getQueryResult(org_id, query_id);
        setHistory(prev => prev.map(q => q.query_id === query_id ? result : q));
        setSelected(prev => prev?.query_id === query_id ? result : prev);
        if (result.status === 'done' || result.status === 'failed') {
          clearInterval(pollRef.current);
        }
      } catch (e) {
        clearInterval(pollRef.current);
      }
    }, POLL_INTERVAL_MS);
  };

  const handleSelectQuery = async (q) => {
    setSelected(q);
    setLogs([]);
    setMetrics(null);
    setActiveTab('answer');
    if (q.status === 'pending' || q.status === 'processing') {
      startPolling(q.query_id);
    }
  };

  const handleLoadLogs = async () => {
    if (!selected) return;
    try {
      const data = await getQueryLogs(org_id, selected.query_id);
      setLogs(data.logs || []);
      setActiveTab('logs');
    } catch (e) {
      setError('Failed to load logs');
    }
  };

  const handleLoadMetrics = async () => {
    if (!selected) return;
    try {
      const data = await getQueryMetrics(org_id, selected.query_id);
      setMetrics(data);
      setActiveTab('metrics');
    } catch (e) {
      setError('Metrics not available yet');
    }
  };

  const statusBadge = (status) => (
    <span className={`status-badge status-${status}`}>{status}</span>
  );

  return (
    <div className="query-page">
      {/* Left panel — query input + history */}
      <div className="query-sidebar">
        <h2 className="sidebar-title">Knowledge Base Query</h2>
        <p className="sidebar-org">Org: <strong>{org_id}</strong></p>

        <form className="query-form" onSubmit={handleSubmit}>
          <textarea
            className="query-input"
            rows={4}
            placeholder="Ask a question about your organization's knowledge base..."
            value={query}
            onChange={e => setQuery(e.target.value)}
            disabled={submitting}
          />
          {error && <div className="query-error">{error}</div>}
          <button className="query-submit-btn" type="submit" disabled={submitting || !query.trim()}>
            {submitting ? 'Submitting...' : 'Ask'}
          </button>
        </form>

        <div className="query-history">
          <div className="history-header">
            <span>Recent Queries</span>
            <button className="refresh-btn" onClick={fetchHistory}>↻</button>
          </div>
          {history.length === 0 && <p className="empty-state">No queries yet</p>}
          {history.map(q => (
            <div
              key={q.query_id}
              className={`history-item ${selected?.query_id === q.query_id ? 'active' : ''}`}
              onClick={() => handleSelectQuery(q)}
            >
              <div className="history-item-text">{q.query_text.slice(0, 80)}{q.query_text.length > 80 ? '…' : ''}</div>
              <div className="history-item-meta">
                {statusBadge(q.status)}
                <span className="history-time">{new Date(q.created_at).toLocaleTimeString()}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Right panel — result detail */}
      <div className="query-detail">
        {!selected ? (
          <div className="detail-empty">
            <p>Submit a query or select one from the history to see results.</p>
          </div>
        ) : (
          <>
            <div className="detail-header">
              <p className="detail-question">{selected.query_text}</p>
              <div className="detail-meta">
                {statusBadge(selected.status)}
                <span className="detail-time">{new Date(selected.created_at).toLocaleString()}</span>
              </div>
            </div>

            <div className="detail-tabs">
              <button className={`detail-tab ${activeTab === 'answer' ? 'active' : ''}`} onClick={() => setActiveTab('answer')}>Answer</button>
              {(user?.role === 'editor' || user?.role === 'admin') && (
                <>
                  <button className={`detail-tab ${activeTab === 'logs' ? 'active' : ''}`} onClick={handleLoadLogs}>Pipeline Logs</button>
                  <button className={`detail-tab ${activeTab === 'metrics' ? 'active' : ''}`} onClick={handleLoadMetrics}>Metrics</button>
                </>
              )}
            </div>

            {activeTab === 'answer' && (
              <div className="detail-answer">
                {(selected.status === 'pending' || selected.status === 'processing') && (
                  <div className="processing-indicator">
                    <span className="spinner" /> Processing your query...
                  </div>
                )}
                {selected.status === 'done' && (
                  <div className="answer-text">{selected.answer}</div>
                )}
                {selected.status === 'failed' && (
                  <div className="answer-error">
                    <strong>Query failed:</strong> {selected.error_message}
                  </div>
                )}
              </div>
            )}

            {activeTab === 'logs' && (
              <div className="detail-logs">
                {logs.length === 0 ? (
                  <p className="empty-state">No logs available</p>
                ) : (
                  <table className="logs-table">
                    <thead>
                      <tr><th>Step</th><th>Status</th><th>Duration</th><th>Details</th><th>Time</th></tr>
                    </thead>
                    <tbody>
                      {logs.map((l, i) => (
                        <tr key={i}>
                          <td><code>{l.step}</code></td>
                          <td><span className={`status-badge status-${l.status}`}>{l.status}</span></td>
                          <td>{l.duration_ms != null ? `${l.duration_ms}ms` : '—'}</td>
                          <td className="log-details">{l.details || '—'}</td>
                          <td>{new Date(l.timestamp).toLocaleTimeString()}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            )}

            {activeTab === 'metrics' && (
              <div className="detail-metrics">
                {!metrics ? (
                  <p className="empty-state">Metrics not available</p>
                ) : (
                  <div className="metrics-grid">
                    <div className="metric-card"><span className="metric-label">Retrieved Chunks</span><span className="metric-value">{metrics.retrieval_count ?? '—'}</span></div>
                    <div className="metric-card"><span className="metric-label">Reranked Chunks</span><span className="metric-value">{metrics.reranked_count ?? '—'}</span></div>
                    <div className="metric-card"><span className="metric-label">ROUGE-1</span><span className="metric-value">{metrics.rouge1 ?? '—'}</span></div>
                    <div className="metric-card"><span className="metric-label">ROUGE-L</span><span className="metric-value">{metrics.rougeL ?? '—'}</span></div>
                    <div className="metric-card"><span className="metric-label">Total Duration</span><span className="metric-value">{metrics.total_duration_ms != null ? `${metrics.total_duration_ms}ms` : '—'}</span></div>
                    <div className="metric-card"><span className="metric-label">Guardrail Blocked</span><span className={`metric-value ${metrics.guardrail_blocked ? 'blocked' : 'passed'}`}>{metrics.guardrail_blocked ? 'Yes' : 'No'}</span></div>
                  </div>
                )}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
