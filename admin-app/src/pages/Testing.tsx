import { useCallback, useEffect, useState } from 'react';
import {
  getLocations,
  getWorkers,
  getLocationWorkers,
  assignWorkersToLocation,
  sendTestNotification,
  getSchedules,
  type Location,
  type Worker,
  type Schedule,
} from '../api';

export function Testing() {
  const [locations, setLocations] = useState<Location[]>([]);
  const [workers, setWorkers] = useState<Worker[]>([]);
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const [assignLocationId, setAssignLocationId] = useState<number>(0);
  const [selectedWorkerIds, setSelectedWorkerIds] = useState<number[]>([]);
  const [locationWorkers, setLocationWorkers] = useState<Worker[]>([]);
  const [assignLoading, setAssignLoading] = useState(false);

  const [sendLocationId, setSendLocationId] = useState<number>(0);
  const [sendTitle, setSendTitle] = useState('Test notification');
  const [sendBody, setSendBody] = useState('This is a test message from the admin.');
  const [sendLoading, setSendLoading] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [locs, wks, scheds] = await Promise.all([
        getLocations(),
        getWorkers(),
        getSchedules(),
      ]);
      setLocations(locs);
      setWorkers(wks);
      setSchedules(scheds);
      setError('');
      if (locs.length && !assignLocationId) setAssignLocationId(locs[0].id);
      if (locs.length && !sendLocationId) setSendLocationId(locs[0].id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    if (!assignLocationId) {
      setLocationWorkers([]);
      return;
    }
    getLocationWorkers(assignLocationId)
      .then(setLocationWorkers)
      .catch(() => setLocationWorkers([]));
  }, [assignLocationId]);

  function toggleWorker(id: number) {
    setSelectedWorkerIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  }

  async function handleAssign() {
    if (!assignLocationId || !selectedWorkerIds.length) {
      setError('Select a location and at least one worker.');
      return;
    }
    setError('');
    setSuccess('');
    setAssignLoading(true);
    try {
      await assignWorkersToLocation(assignLocationId, selectedWorkerIds);
      setSuccess(`Assigned ${selectedWorkerIds.length} worker(s) to location.`);
      setSelectedWorkerIds([]);
      const list = await getLocationWorkers(assignLocationId);
      setLocationWorkers(list);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to assign');
    } finally {
      setAssignLoading(false);
    }
  }

  async function handleSendTest() {
    if (!sendLocationId) {
      setError('Select a location to send the test.');
      return;
    }
    setError('');
    setSuccess('');
    setSendLoading(true);
    try {
      await sendTestNotification(sendLocationId, { title: sendTitle, body: sendBody });
      setSuccess('Test notification sent to all workers at this location.');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send');
    } finally {
      setSendLoading(false);
    }
  }

  const locationName = (id: number) => locations.find((l) => l.id === id)?.name ?? id;

  if (loading) {
    return <p>Loading…</p>;
  }

  return (
    <>
      <h1 style={{ marginTop: 0 }}>Testing</h1>
      <p style={{ color: '#64748b', marginBottom: '1.5rem' }}>
        Assign workers to locations and send test notifications. Scheduled alerts become{' '}
        <strong>inactive</strong> after they are sent at their scheduled time.
      </p>
      {error && <p className="error-msg">{error}</p>}
      {success && <p className="success-msg">{success}</p>}

      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <h2 style={{ marginTop: 0 }}>1. Assign workers to a location</h2>
        <p style={{ fontSize: '0.9rem', color: '#64748b', marginBottom: '1rem' }}>
          Workers assigned to a location will receive notifications sent to that location.
        </p>
        <div className="form-group">
          <label>Location</label>
          <select
            value={assignLocationId || ''}
            onChange={(e) => setAssignLocationId(Number(e.target.value))}
          >
            {locations.map((loc) => (
              <option key={loc.id} value={loc.id}>{loc.name}</option>
            ))}
          </select>
        </div>
        <div className="form-group">
          <label>Workers to assign</label>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '0.5rem' }}>
            {workers.map((w) => (
              <label key={w.id} style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                <input
                  type="checkbox"
                  checked={selectedWorkerIds.includes(w.id)}
                  onChange={() => toggleWorker(w.id)}
                />
                <span>{w.name || w.phone || `Worker #${w.id}`}</span>
              </label>
            ))}
          </div>
          {workers.length === 0 && <span style={{ color: '#64748b' }}>No workers. Add workers first.</span>}
        </div>
        <div className="actions" style={{ marginBottom: '1rem' }}>
          <button type="button" onClick={handleAssign} disabled={assignLoading || !selectedWorkerIds.length}>
            {assignLoading ? 'Assigning…' : 'Assign to location'}
          </button>
        </div>
        {assignLocationId > 0 && (
          <>
            <h3 style={{ marginBottom: '0.5rem' }}>Workers at this location</h3>
            {locationWorkers.length === 0 ? (
              <p style={{ color: '#64748b', fontSize: '0.9rem' }}>None assigned yet.</p>
            ) : (
              <ul style={{ margin: 0, paddingLeft: '1.25rem' }}>
                {locationWorkers.map((w) => (
                  <li key={w.id}>{w.name || w.phone || `Worker #${w.id}`}</li>
                ))}
              </ul>
            )}
          </>
        )}
      </div>

      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <h2 style={{ marginTop: 0 }}>2. Send test notification by location</h2>
        <p style={{ fontSize: '0.9rem', color: '#64748b', marginBottom: '1rem' }}>
          Sends a notification now to all devices subscribed to the selected location&apos;s topic.
        </p>
        <div className="form-group">
          <label>Location</label>
          <select
            value={sendLocationId || ''}
            onChange={(e) => setSendLocationId(Number(e.target.value))}
          >
            {locations.map((loc) => (
              <option key={loc.id} value={loc.id}>{loc.name}</option>
            ))}
          </select>
        </div>
        <div className="form-group">
          <label>Title</label>
          <input value={sendTitle} onChange={(e) => setSendTitle(e.target.value)} />
        </div>
        <div className="form-group">
          <label>Body</label>
          <textarea value={sendBody} onChange={(e) => setSendBody(e.target.value)} rows={2} />
        </div>
        <div className="actions">
          <button type="button" onClick={handleSendTest} disabled={sendLoading}>
            {sendLoading ? 'Sending…' : 'Send test now'}
          </button>
        </div>
      </div>

      <div className="card">
        <h2 style={{ marginTop: 0 }}>3. Schedules &ndash; active until sent</h2>
        <p style={{ fontSize: '0.9rem', color: '#64748b', marginBottom: '1rem' }}>
          When the scheduled time is reached and the notification is sent to all, the schedule is
          automatically set to <strong>inactive</strong> and will not run again.
        </p>
        {schedules.length === 0 ? (
          <p style={{ color: '#64748b' }}>No schedules. Create one in Schedules.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Location</th>
                <th>Name</th>
                <th>Time</th>
                <th>Active</th>
              </tr>
            </thead>
            <tbody>
              {schedules.map((s) => (
                <tr key={s.id}>
                  <td>{locationName(s.location_id)}</td>
                  <td>{s.name}</td>
                  <td>{s.send_time}</td>
                  <td>{s.is_active ? 'Yes' : 'No (already sent)'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </>
  );
}
