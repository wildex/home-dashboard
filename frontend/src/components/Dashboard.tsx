import React, { useEffect, useState, FormEvent } from 'react';
import { getDashboard, DashboardData, addTemp, clearTemps } from '../api';

export function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [tempValue, setTempValue] = useState<number | ''>('');
  const [room, setRoom] = useState('living');
  const [clearing, setClearing] = useState(false);

  async function load() {
    setLoading(true);
    try {
      const result: DashboardData = await getDashboard();
      setData(result);
    } catch (e: any) { setError(e.message); }
    finally { setLoading(false); }
  }
  useEffect(() => { load(); const id = setInterval(load, 15000); return ()=>clearInterval(id); }, []);

  async function submitTemp(e: FormEvent) {
    e.preventDefault();
    if (tempValue === '' || isNaN(Number(tempValue))) return;
    try { await addTemp(Number(tempValue), room.trim() || 'default'); setTempValue(''); await load(); } catch (e: any) { setError(e.message); }
  }

  async function clear(roomFilter?: string) {
    setClearing(true);
    try { await clearTemps(roomFilter); await load(); } catch (e: any) { setError(e.message); }
    finally { setClearing(false); }
  }

  function renderCharts() {
    if (!data) return null;
    const rooms = Object.keys(data.recent_temps_by_room).sort();
    if (rooms.length === 0) return <p>No temperature data.</p>;
    return (
      <div className="charts">
        {rooms.map(rm => {
          const readings = data.recent_temps_by_room[rm];
          const values = readings.map(r => r.value_c);
          const min = Math.min(...values);
          const max = Math.max(...values);
          const range = max - min || 1;
          const points = readings.map((r, i) => {
            const x = (i / Math.max(1, readings.length - 1)) * 100;
            const y = 100 - ((r.value_c - min) / range) * 100;
            return `${x},${y}`;
          }).join(' ');
          return (
            <div key={rm} className="chart-card">
              <div className="chart-header">
                <strong>{rm}</strong>
                <button className="inline" disabled={clearing} onClick={()=>clear(rm)}>Clear</button>
              </div>
              <svg viewBox="0 0 100 100" preserveAspectRatio="none" className="line-chart">
                <polyline points={points} fill="none" stroke="#4dabf7" strokeWidth="2" />
              </svg>
              <div className="chart-meta">
                <span>{readings[readings.length-1]?.value_c.toFixed(1)}°C latest</span>
                <span>Range {min.toFixed(1)}–{max.toFixed(1)}°C</span>
              </div>
            </div>
          );
        })}
      </div>
    );
  }

  return (
    <div className="panel">
      <h2>Dashboard <button className="inline" onClick={load} disabled={loading}>↻</button></h2>
      {error && <div className="error" onClick={()=>setError(null)}>{error}</div>}
      <form onSubmit={submitTemp} className="row">
        <input type="number" step="0.1" placeholder="Temp °C" value={tempValue} onChange={e=>setTempValue(e.target.value === '' ? '' : Number(e.target.value))} />
        <input placeholder="Room" value={room} onChange={e=>setRoom(e.target.value)} />
        <button type="submit">Add Temp</button>
        <button type="button" disabled={clearing} onClick={()=>clear(undefined)}>Clear All</button>
      </form>
      {!data && <p>{loading? 'Loading...':'No data'}</p>}
      {data && (
        <>
          <section>
            <h3>Due Tasks</h3>
            {data.due_tasks.length === 0 ? <p>No tasks due.</p> : (
              <ul>{data.due_tasks.map(t => <li key={t.id}>{t.appliance.name}: {t.due_date}</li>)}</ul>
            )}
          </section>
          <section>
            <h3>Temperature (per room)</h3>
            {renderCharts()}
          </section>
        </>
      )}
    </div>
  );
}
