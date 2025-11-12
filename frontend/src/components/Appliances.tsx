import React, { useEffect, useState, FormEvent } from 'react';
import { listAppliances, createAppliance, updateInterval, bulkDelete, listTasks, completeTask, Appliance, Task } from '../api';

export function Appliances() {
  const [appliances, setAppliances] = useState<Appliance[]>([]);
  const [newName, setNewName] = useState('');
  const [newInterval, setNewInterval] = useState<number | ''>('');
  const [selected, setSelected] = useState<Set<number>>(new Set());
  const [tasks, setTasks] = useState<Record<number, Task[]>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function refresh() {
    setLoading(true);
    try {
      const data = await listAppliances();
      setAppliances(data);
    } catch (e: any) { setError(e.message); }
    finally { setLoading(false); }
  }

  useEffect(() => { refresh(); }, []);

  async function onCreate(e: FormEvent) {
    e.preventDefault();
    if (!newName.trim()) return;
    try {
      await createAppliance(newName.trim(), newInterval === '' ? undefined : Number(newInterval));
      setNewName(''); setNewInterval('');
      await refresh();
    } catch (e: any) { setError(e.message); }
  }

  function toggle(id: number) {
    const s = new Set(selected);
    if (s.has(id)) s.delete(id); else s.add(id);
    setSelected(s);
  }

  async function onBulkDelete() {
    if (selected.size === 0) return;
    try {
      await bulkDelete(Array.from(selected));
      setSelected(new Set());
      await refresh();
    } catch (e: any) { setError(e.message); }
  }

  async function changeInterval(id: number, interval: number | null) {
    try { await updateInterval(id, interval); await refresh(); } catch (e: any) { setError(e.message); }
  }

  async function loadTasks(id: number) {
    try {
      const loaded: Task[] = await listTasks(id);
      setTasks(prev => ({ ...prev, [id]: loaded }));
    } catch (e: any) { setError(e.message); }
  }

  async function markComplete(task: Task) {
    try { await completeTask(task.id); await loadTasks(task.appliance_id); } catch (e: any) { setError(e.message); }
  }

  return (
    <div className="panel">
      <h2>Appliances <button className="inline" onClick={refresh} disabled={loading}>↻</button></h2>
      {error && <div className="error" onClick={()=>setError(null)}>{error}</div>}
      <form onSubmit={onCreate} className="row">
        <input value={newName} onChange={e => setNewName(e.target.value)} placeholder="Name" />
        <input value={newInterval} onChange={e => setNewInterval(e.target.value === '' ? '' : Number(e.target.value))} placeholder="Interval (days)" type="number" min={1} />
        <button type="submit">Add</button>
        <button type="button" disabled={selected.size===0} onClick={onBulkDelete}>Delete Selected ({selected.size})</button>
      </form>
      {loading && <p>Loading...</p>}
      <div className="grid">
        {appliances.map(a => {
          const overdue = tasks[a.id]?.some(t => !t.completed && new Date(t.due_date) < new Date());
          return (
            <div key={a.id} className={`card ${selected.has(a.id)?'selected':''} ${overdue?'overdue':''}`}>
              <label className="select-box"><input type="checkbox" checked={selected.has(a.id)} onChange={()=>toggle(a.id)} /></label>
              <h3>{a.name}</h3>
              <p>{a.cleaning_interval_days?`Every ${a.cleaning_interval_days} days`:'Unscheduled'}</p>
              <div className="actions">
                <button onClick={()=>changeInterval(a.id, a.cleaning_interval_days?null:7)}>{a.cleaning_interval_days? 'Unschedule':'Set 7d'}</button>
                <button onClick={()=>loadTasks(a.id)}>Tasks</button>
              </div>
              {tasks[a.id] && (
                <table className="tasks"><tbody>{tasks[a.id].map(t => (
                  <tr key={t.id} className={!t.completed && new Date(t.due_date) < new Date() ? 'due' : ''}>
                    <td>{t.due_date}</td><td>{t.completed?'✓':'Pending'}</td>
                    <td>{t.completed? t.completed_at?.slice(0,19).replace('T',' '): <button onClick={()=>markComplete(t)}>Complete</button>}</td>
                  </tr>
                ))}</tbody></table>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
