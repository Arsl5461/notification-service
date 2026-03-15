// Use env if set; otherwise when app is on port 3000, call API on port 8000
function getApiBase(): string {
  if (process.env.REACT_APP_API_URL) return process.env.REACT_APP_API_URL;
  if (typeof window !== 'undefined' && window.location.port === '3000') {
    return 'http://localhost:8000';
  }
  return '';
}
const API_BASE = getApiBase() + '/api';

function getToken(): string | null {
  return localStorage.getItem('adminToken');
}

export async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers: HeadersInit = { 'Content-Type': 'application/json', ...options.headers };
  const token = getToken();
  if (token) (headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
  const res = await fetch(API_BASE + path, { ...options, headers });
  if (res.status === 401) {
    localStorage.removeItem('adminToken');
    window.location.href = '/';
    throw new Error('Unauthorized');
  }
  const text = await res.text();
  let data: unknown;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    throw new Error(text || res.statusText);
  }
  if (!res.ok) {
    const detail = (data as { detail?: string })?.detail;
    throw new Error(typeof detail === 'string' ? detail : JSON.stringify(data));
  }
  return data as T;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export function login(payload: LoginPayload) {
  return api<{ access_token: string; token_type: string }>('/auth/login', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function getMe() {
  return api<{ id: number; email: string; full_name: string | null; company_id: number | null }>('/auth/me');
}

export interface Company {
  id: number;
  name: string;
}

export function getCompany() {
  return api<Company>('/companies/me');
}

export interface Location {
  id: number;
  company_id: number;
  name: string;
  code: string | null;
  address: string | null;
  latitude: number | null;
  longitude: number | null;
  timezone: string;
  is_active: boolean;
}

export function getLocations() {
  return api<Location[]>('/locations');
}

export function createLocation(data: {
  name: string;
  code?: string | null;
  address?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  timezone?: string;
}) {
  return api<Location>('/locations', { method: 'POST', body: JSON.stringify(data) });
}

export function updateLocation(
  id: number,
  data: Partial<{ name: string; code: string | null; address: string | null; timezone: string; is_active: boolean }>
) {
  return api<Location>(`/locations/${id}`, { method: 'PATCH', body: JSON.stringify(data) });
}

export function deleteLocation(id: number) {
  return api<void>(`/locations/${id}`, { method: 'DELETE' });
}

export interface Worker {
  id: number;
  company_id: number;
  external_id: string | null;
  name: string | null;
  phone: string | null;
  created_at: string;
}

export function getWorkers(locationId?: number) {
  const q = locationId != null ? `?location_id=${locationId}` : '';
  return api<Worker[]>(`/workers${q}`);
}

export function createWorker(data: { name?: string | null; phone?: string | null; external_id?: string | null }) {
  return api<Worker>('/workers', { method: 'POST', body: JSON.stringify(data) });
}

export interface Schedule {
  id: number;
  location_id: number;
  name: string;
  message_title: string;
  message_body: string;
  send_time: string;
  is_active: boolean;
}

export function getSchedules(locationId?: number) {
  const q = locationId != null ? `?location_id=${locationId}` : '';
  return api<Schedule[]>(`/schedules${q}`);
}

export function createSchedule(data: {
  location_id: number;
  name: string;
  message_title: string;
  message_body: string;
  send_time: string;
}) {
  return api<Schedule>('/schedules', { method: 'POST', body: JSON.stringify(data) });
}

export function updateSchedule(
  id: number,
  data: Partial<{ name: string; message_title: string; message_body: string; send_time: string; is_active: boolean }>
) {
  return api<Schedule>(`/schedules/${id}`, { method: 'PATCH', body: JSON.stringify(data) });
}

export function deleteSchedule(id: number) {
  return api<void>(`/schedules/${id}`, { method: 'DELETE' });
}

export function getLocationWorkers(locationId: number) {
  return api<Worker[]>(`/locations/${locationId}/workers`);
}

export function assignWorkersToLocation(locationId: number, workerIds: number[]) {
  return api<{ assigned: number; location_id: number }>(`/locations/${locationId}/assign-workers`, {
    method: 'POST',
    body: JSON.stringify({ worker_ids: workerIds }),
  });
}

export function sendTestNotification(
  locationId: number,
  data: { title?: string; body?: string } = {}
) {
  return api<{ sent: boolean; topic: string; title: string; body: string }>(
    `/locations/${locationId}/send-test`,
    { method: 'POST', body: JSON.stringify({ title: data.title ?? 'Test notification', body: data.body ?? 'This is a test message from the admin.' }) }
  );
}
