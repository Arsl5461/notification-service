import React, { useCallback, useEffect, useState } from 'react';
import {
  getLocations,
  createLocation,
  updateLocation,
  deleteLocation,
  type Location,
} from '../api';

export function Locations() {
  const [list, setList] = useState<Location[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [editing, setEditing] = useState<Location | null>(null);
  const [formVisible, setFormVisible] = useState(false);
  const [form, setForm] = useState({
    name: '',
    code: '',
    address: '',
    timezone: 'UTC',
  });

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getLocations();
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

  function openCreate() {
    setEditing(null);
    setFormVisible(true);
    setForm({ name: '', code: '', address: '', timezone: 'UTC' });
  }

  function openEdit(loc: Location) {
    setEditing(loc);
    setFormVisible(true);
    setForm({
      name: loc.name,
      code: loc.code ?? '',
      address: loc.address ?? '',
      timezone: loc.timezone ?? 'UTC',
    });
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError('');
    try {
      if (editing) {
        await updateLocation(editing.id, {
          name: form.name,
          code: form.code || null,
          address: form.address || null,
          timezone: form.timezone,
        });
      } else {
        await createLocation({
          name: form.name,
          code: form.code || null,
          address: form.address || null,
          timezone: form.timezone,
        });
      }
      setEditing(null);
      setFormVisible(false);
      setForm({ name: '', code: '', address: '', timezone: 'UTC' });
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save');
    }
  }

  async function handleDelete(loc: Location) {
    if (!window.confirm(`Delete location "${loc.name}"?`)) return;
    try {
      await deleteLocation(loc.id);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete');
    }
  }

  return (
    <>
      <h1 style={{ marginTop: 0 }}>Locations</h1>
      {error && <p className="error-msg">{error}</p>}
      <button type="button" onClick={openCreate} style={{ marginBottom: '1rem' }}>
        Add location
      </button>

      {formVisible && (
        <div className="card" style={{ marginBottom: '1.5rem' }}>
          <h2 style={{ marginTop: 0 }}>{editing ? 'Edit location' : 'New location'}</h2>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Name</label>
              <input value={form.name} onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))} required />
            </div>
            <div className="form-group">
              <label>Code</label>
              <input value={form.code} onChange={(e) => setForm((f) => ({ ...f, code: e.target.value }))} placeholder="e.g. BRANCH-A" />
            </div>
            <div className="form-group">
              <label>Address</label>
              <input value={form.address} onChange={(e) => setForm((f) => ({ ...f, address: e.target.value }))} />
            </div>
            <div className="form-group">
              <label>Timezone</label>
              <input value={form.timezone} onChange={(e) => setForm((f) => ({ ...f, timezone: e.target.value }))} />
            </div>
            <div className="actions">
              <button type="submit">{editing ? 'Update' : 'Create'}</button>
              <button type="button" className="secondary" onClick={() => { setEditing(null); setFormVisible(false); setForm({ name: '', code: '', address: '', timezone: 'UTC' }); }}>
                Cancel
              </button>
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
              <th>Name</th>
              <th>Code</th>
              <th>Timezone</th>
              <th style={{ width: 140 }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {list.map((loc) => (
              <tr key={loc.id}>
                <td>{loc.name}</td>
                <td>{loc.code ?? '—'}</td>
                <td>{loc.timezone}</td>
                <td>
                  <div className="actions">
                    <button type="button" className="secondary" onClick={() => openEdit(loc)}>Edit</button>
                    <button type="button" className="danger" onClick={() => handleDelete(loc)}>Delete</button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </>
  );
}
