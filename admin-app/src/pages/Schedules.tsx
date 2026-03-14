import React, { useCallback, useEffect, useState } from 'react';
import {
  getLocations,
  getSchedules,
  createSchedule,
  updateSchedule,
  deleteSchedule,
  type Location,
  type Schedule,
} from '../api';

export function Schedules() {
  const [locations, setLocations] = useState<Location[]>([]);
  const [list, setList] = useState<Schedule[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [editing, setEditing] = useState<Schedule | null>(null);
  const [formVisible, setFormVisible] = useState(false);
  const [form, setForm] = useState({
    location_id: 0,
    name: '',
    message_title: '',
    message_body: '',
    send_time: '09:00',
  });

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [locs, scheds] = await Promise.all([getLocations(), getSchedules()]);
      setLocations(locs);
      setList(scheds);
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
    setForm({
      location_id: locations[0]?.id ?? 0,
      name: '',
      message_title: '',
      message_body: '',
      send_time: '09:00',
    });
  }

  function openEdit(s: Schedule) {
    setEditing(s);
    setFormVisible(true);
    setForm({
      location_id: s.location_id,
      name: s.name,
      message_title: s.message_title,
      message_body: s.message_body,
      send_time: s.send_time.length === 5 ? s.send_time : s.send_time.slice(0, 5),
    });
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError('');
    try {
      if (editing) {
        await updateSchedule(editing.id, {
          name: form.name,
          message_title: form.message_title,
          message_body: form.message_body,
          send_time: form.send_time,
        });
      } else {
        await createSchedule({
          location_id: form.location_id,
          name: form.name,
          message_title: form.message_title,
          message_body: form.message_body,
          send_time: form.send_time,
        });
      }
      setEditing(null);
      setFormVisible(false);
      setForm({ location_id: locations[0]?.id ?? 0, name: '', message_title: '', message_body: '', send_time: '09:00' });
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save');
    }
  }

  async function handleDelete(s: Schedule) {
    if (!window.confirm(`Delete schedule "${s.name}"?`)) return;
    try {
      await deleteSchedule(s.id);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete');
    }
  }

  const locationName = (id: number) => locations.find((l) => l.id === id)?.name ?? id;

  return (
    <>
      <h1 style={{ marginTop: 0 }}>Scheduled Alerts</h1>
      {error && <p className="error-msg">{error}</p>}
      <button type="button" onClick={openCreate} style={{ marginBottom: '1rem' }}>Add schedule</button>

      {formVisible && (
        <div className="card" style={{ marginBottom: '1.5rem' }}>
          <h2 style={{ marginTop: 0 }}>{editing ? 'Edit schedule' : 'New schedule'}</h2>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Location</label>
              <select
                value={form.location_id}
                onChange={(e) => setForm((f) => ({ ...f, location_id: Number(e.target.value) }))}
                disabled={!!editing}
              >
                {locations.map((loc) => (
                  <option key={loc.id} value={loc.id}>{loc.name}</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>Name</label>
              <input value={form.name} onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))} placeholder="e.g. Morning check-in" required />
            </div>
            <div className="form-group">
              <label>Message title</label>
              <input value={form.message_title} onChange={(e) => setForm((f) => ({ ...f, message_title: e.target.value }))} required />
            </div>
            <div className="form-group">
              <label>Message body</label>
              <textarea value={form.message_body} onChange={(e) => setForm((f) => ({ ...f, message_body: e.target.value }))} rows={3} required />
            </div>
            <div className="form-group">
              <label>Send time (HH:MM)</label>
              <input type="time" value={form.send_time} onChange={(e) => setForm((f) => ({ ...f, send_time: e.target.value }))} required />
            </div>
            <div className="actions">
              <button type="submit">{editing ? 'Update' : 'Create'}</button>
              <button type="button" className="secondary" onClick={() => { setEditing(null); setFormVisible(false); setForm({ location_id: locations[0]?.id ?? 0, name: '', message_title: '', message_body: '', send_time: '09:00' }); }}>
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
              <th>Location</th>
              <th>Name</th>
              <th>Time</th>
              <th>Title</th>
              <th>Active</th>
              <th style={{ width: 140 }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {list.map((s) => (
              <tr key={s.id}>
                <td>{locationName(s.location_id)}</td>
                <td>{s.name}</td>
                <td>{s.send_time}</td>
                <td>{s.message_title}</td>
                <td>{s.is_active ? 'Yes' : 'No'}</td>
                <td>
                  <div className="actions">
                    <button type="button" className="secondary" onClick={() => openEdit(s)}>Edit</button>
                    <button type="button" className="danger" onClick={() => handleDelete(s)}>Delete</button>
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
