import React, { useEffect, useState, FormEvent } from 'react';
import { getDashboard, DashboardData, addTemp, clearTemps, completeTask } from '../api';
import { Box, Button, Card, CardContent, Typography, TextField, Stack, Chip } from '@mui/material';

export function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [tempValue, setTempValue] = useState<number | ''>('');
  const [room, setRoom] = useState('вітальня');
  const [clearing, setClearing] = useState(false);
  const [completingId, setCompletingId] = useState<number | null>(null);

  async function load() {
    setLoading(true);
    try { const result = await getDashboard(); setData(result); } catch (e: any) { setError(e.message); } finally { setLoading(false); }
  }
  useEffect(() => { load(); const id = setInterval(load, 15000); return ()=>clearInterval(id); }, []);

  async function submitTemp(e: FormEvent) {
    e.preventDefault();
    if (tempValue === '' || isNaN(Number(tempValue))) return;
    try { await addTemp(Number(tempValue), room.trim() || 'default'); setTempValue(''); await load(); } catch (e: any) { setError(e.message); }
  }
  async function clear(roomFilter?: string) {
    setClearing(true);
    try { await clearTemps(roomFilter); await load(); } catch (e: any) { setError(e.message); } finally { setClearing(false); }
  }
  async function markDueComplete(id: number) {
    try {
      setCompletingId(id);
      await completeTask(id);
      await load();
    } catch (e: any) { setError(e.message); }
    finally { setCompletingId(null); }
  }

  function renderCharts() {
    if (!data) return null;
    const rooms = Object.keys(data.recent_temps_by_room).sort();
    if (rooms.length === 0) return <Typography variant="body2">Немає даних температури.</Typography>;
    return (
      <Box display="grid" gap={2} gridTemplateColumns="repeat(auto-fill,minmax(340px,1fr))" mt={1}>
        {rooms.map(rm => {
          const readings = data.recent_temps_by_room[rm];
          const values = readings.map(r => r.value_c);
          const min = Math.min(...values);
          const max = Math.max(...values);
          const range = max - min || 1;
          const axisWidth = 16; // increased axis space
          const ticksCount = 5;
          const ticks = Array.from({length: ticksCount}, (_, i) => min + (range * i / (ticksCount - 1)));
          const points = readings.map((r, i) => {
            const x = axisWidth + (i / Math.max(1, readings.length - 1)) * (100 - axisWidth);
            const y = 100 - ((r.value_c - min) / range) * 100;
            return `${x},${y}`;
          }).join(' ');
          return (
            <Card key={rm} variant="outlined" sx={{ backgroundColor:'background.default' }}>
              <CardContent sx={{ display:'flex', flexDirection:'column', gap:1 }}>
                <Stack direction="row" justifyContent="space-between" alignItems="center">
                  <Typography variant="subtitle1" fontWeight={600}>{rm}</Typography>
                  <Button size="small" variant="text" disabled={clearing} onClick={()=>clear(rm)}>Очистити</Button>
                </Stack>
                <Box component="svg" viewBox={`0 0 120 100`} preserveAspectRatio="none" sx={{ width:'100%', height:200, background:'#10151a', border:'1px solid', borderColor:'divider', borderRadius:1 }}>
                  {/* Axis line */}
                  <line x1={axisWidth} y1={0} x2={axisWidth} y2={100} stroke="#2d3a46" strokeWidth={1} />
                  {/* Horizontal grid & labels */}
                  {ticks.map(t => {
                    const y = 100 - ((t - min) / range) * 100;
                    return (
                      <g key={t.toFixed(2)}>
                        <line x1={axisWidth} y1={y} x2={120} y2={y} stroke="#2d3a46" strokeWidth={0.6} strokeDasharray="2 2" />
                        <text x={axisWidth - 3} y={y + 3} fontSize={8} fill="#94a3b8" textAnchor="end">{t.toFixed(1)}</text>
                      </g>
                    );
                  })}
                  <polyline points={points} fill="none" stroke="#4dabf7" strokeWidth={2.4} />
                </Box>
                <Stack direction="row" justifyContent="space-between" sx={{ fontSize:12, opacity:.85 }}>
                  <span>{readings[readings.length-1]?.value_c.toFixed(1)}°C остання</span>
                  <span>Діапазон {min.toFixed(1)}–{max.toFixed(1)}°C</span>
                </Stack>
              </CardContent>
            </Card>
          );
        })}
      </Box>
    );
  }

  return (
    <Box component={Card} className="panel" variant="outlined" sx={{ backgroundColor:'background.paper', mb:2 }}>
      <CardContent>
        <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h5">Панель</Typography>
          <Button size="small" variant="text" onClick={load} disabled={loading}>Оновити</Button>
        </Stack>
        {error && <Chip color="error" label={error} onDelete={()=>setError(null)} sx={{ mb:2 }} />}
        <Box component="form" onSubmit={submitTemp} mb={2} display="flex" flexWrap="wrap" gap={1}>
          <TextField size="small" label="Температура °C" type="number" value={tempValue} onChange={e=>setTempValue(e.target.value === '' ? '' : Number(e.target.value))} />
          <TextField size="small" label="Кімната" value={room} onChange={e=>setRoom(e.target.value)} />
          <Button type="submit" variant="contained">Додати температуру</Button>
          <Button type="button" variant="outlined" disabled={clearing} onClick={()=>clear(undefined)}>Очистити все</Button>
        </Box>
        {!data && <Typography variant="body2">{loading? 'Завантаження...' : 'Немає даних'}</Typography>}
        {data && (
          <>
            <Box mb={2}>
              <Typography variant="h6">Завдання до виконання</Typography>
              {data.due_tasks.length === 0 ? <Typography variant="body2">Немає завдань.</Typography> : (
                <Box component="ul" sx={{ pl:3, m:0, listStyle:'disc' }}>
                  {data.due_tasks.map(t => (
                    <li key={t.id} style={{ marginBottom: 4 }}>
                      {t.appliance.name}: {t.due_date}{' '}
                      <Button size="small" variant="outlined" disabled={completingId===t.id} onClick={()=>markDueComplete(t.id)}>
                        {completingId===t.id ? '...' : 'Завершити'}
                      </Button>
                    </li>
                  ))}
                </Box>
              )}
            </Box>
            <Box>
              <Typography variant="h6">Температура (за кімнатами)</Typography>
              {renderCharts()}
            </Box>
          </>
        )}
      </CardContent>
    </Box>
  );
}
