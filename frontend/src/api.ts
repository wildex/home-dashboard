export const API_BASE = (typeof import !== 'undefined' && (import.meta as any)?.env?.VITE_API_BASE) || (window as any).API_BASE || 'http://127.0.0.1:8000';

export interface Appliance { id: number; name: string; cleaning_interval_days: number | null; created_at: string; }
export interface Task { id: number; appliance_id: number; due_date: string; completed: boolean; completed_at: string | null; }
export interface TemperatureReading { id: number; recorded_at: string; value_c: number; room: string; }
export interface DashboardData { due_tasks: Array<{ id: number; due_date: string; completed: boolean; completed_at: string | null; appliance: Appliance }>; recent_temps: TemperatureReading[]; recent_temps_by_room: Record<string, TemperatureReading[]>; }

async function json<T>(p: Promise<Response>): Promise<T> {
  const res = await p;
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`HTTP ${res.status}: ${text}`);
  }
  return res.json() as Promise<T>;
}

export function getDashboard(): Promise<DashboardData> {
  return json<DashboardData>(fetch(`${API_BASE}/api/dashboard`));
}
export function listAppliances(): Promise<Appliance[]> {
  return json<Appliance[]>(fetch(`${API_BASE}/api/appliances/`));
}
export function createAppliance(name: string, interval?: number): Promise<Appliance> {
  return json<Appliance>(fetch(`${API_BASE}/api/appliances/`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name, cleaning_interval_days: interval ?? null })
  }));
}
export function updateInterval(id: number, interval: number | null): Promise<Appliance> {
  return json<Appliance>(fetch(`${API_BASE}/api/appliances/${id}/interval`, {
    method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ cleaning_interval_days: interval })
  }));
}
export function bulkDelete(ids: number[]): Promise<{ deleted: number }> {
  return json<{ deleted: number }>(fetch(`${API_BASE}/api/appliances/bulk-delete`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ ids })
  }));
}
export function listTasks(applianceId: number): Promise<Task[]> {
  return json<Task[]>(fetch(`${API_BASE}/api/appliances/${applianceId}/tasks`));
}
export function completeTask(taskId: number): Promise<Task> {
  return json<Task>(fetch(`${API_BASE}/api/tasks/${taskId}`, {
    method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ completed: true })
  }));
}
export function addTemp(value_c: number, room: string): Promise<TemperatureReading> {
  return json<TemperatureReading>(fetch(`${API_BASE}/api/temperature/`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ value_c, room })
  }));
}
export function clearTemps(room?: string): Promise<{ deleted: number }> {
  const url = new URL(`${API_BASE}/api/temperature/`);
  if (room) url.searchParams.set('room', room);
  return json<{ deleted: number }>(fetch(url, { method: 'DELETE' }));
}
