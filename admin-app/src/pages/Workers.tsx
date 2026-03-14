import React, { useCallback, useEffect, useState } from 'react';
import { getWorkers, createWorker, type Worker } from '../api';

export function Workers() {
  const [list, setList] = useState<Worker[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: '', phone: '', external_id: '' });

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getWorkers();
      setList(data);
      setError('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError('');
    try {
      await createWorker({ name: form.name || null, phone: form.phone || null, external_id: form.external_id || null });
      setForm({ name: '', phone: '', external_id: '' });
      setShowForm(false);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create');
    }
  }

  return (
    <>
      <h1 style={{ marginTop: 0 }}>Workers</h1>
      {error && <p className="error-msg">{error}</p>}
      <button type="button" onClick={() => setShowForm(true)} style={{ marginBottom: '1rem' }}>Add worker</button>

      {showForm && (
        <div className="card" style={{ marginBottom: '1.5rem' }}>
          <h2 style={{ marginTop: 0 }}>New worker</h2>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Name</label>
              <input value={form.name} onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))} />
            </div>
            <div className="form-group">
              <label>Phone</label>
              <input value={form.phone} onChange={(e) => setForm((f) => ({ ...f, phone: e.target.value }))} />
            </div>
            <div className="form-group">
              <label>External ID (device id)</label>
              <input value={form.external_id} onChange={(e) => setForm((f) => ({ ...f, external_id: e.target.value }))} />
            </div>
            <div className="actions">
              <button type="submit">Create</button>
              <button type="button" className="secondary" onClick={() => setShowForm(false)}>Cancel</button>
            </div>
          </form>
        </div>
      )}

      {loading ? (
        <p>Loading…</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Phone</th>
              <th>External ID</th>
            </tr>
          </thead>
          <tbody>
            {list.map((w) => (
              <tr key={w.id}>
                <td>{w.id}</td>
                <td>{w.name ?? '—'}</td>
                <td>{w.phone ?? '—'}</td>
                <td>{w.external_id ?? '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </>
  );
}
