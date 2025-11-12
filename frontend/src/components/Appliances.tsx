import React, { useEffect, useState, FormEvent } from 'react';
import { listAppliances, createAppliance, updateInterval, bulkDelete, listTasks, completeTask, Appliance, Task } from '../api';
import { Box, Button, TextField, Checkbox, Card, CardContent, Typography, Table, TableBody, TableCell, TableRow, TableHead, Stack, Chip } from '@mui/material';

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
    s.has(id) ? s.delete(id) : s.add(id);
    setSelected(s);
  }

  async function onBulkDelete() {
    if (!selected.size) return;
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
    try { const loaded = await listTasks(id); setTasks(prev => ({ ...prev, [id]: loaded })); } catch (e: any) { setError(e.message); }
  }

  async function markComplete(task: Task) {
    try { await completeTask(task.id); await loadTasks(task.appliance_id); } catch (e: any) { setError(e.message); }
  }

  return (
    <Box className="panel" component={Card} variant="outlined" sx={{ backgroundColor: 'background.paper', mb: 2 }}>
      <CardContent>
        <Stack direction="row" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h5">Прилади</Typography>
          <Button size="small" variant="text" disabled={loading} onClick={refresh}>Оновити</Button>
        </Stack>
        {error && <Chip color="error" label={error} onDelete={()=>setError(null)} sx={{ mb:2 }} />}
        <Box component="form" onSubmit={onCreate} mb={2} display="flex" flexWrap="wrap" gap={1}>
          <TextField size="small" label="Назва" value={newName} onChange={e=>setNewName(e.target.value)} />
          <TextField size="small" label="Інтервал (дні)" type="number" inputProps={{ min:1 }} value={newInterval} onChange={e=>setNewInterval(e.target.value === '' ? '' : Number(e.target.value))} />
          <Button type="submit" variant="contained">Додати</Button>
          <Button type="button" variant="outlined" color="error" disabled={!selected.size} onClick={onBulkDelete}>Видалити вибрані ({selected.size})</Button>
        </Box>
        {loading && <Typography variant="body2">Завантаження...</Typography>}
        <Box display="grid" gap={2} gridTemplateColumns="repeat(auto-fill,minmax(260px,1fr))">
          {appliances.map(a => {
            const overdue = tasks[a.id]?.some(t => !t.completed && new Date(t.due_date) < new Date());
            return (
              <Card key={a.id} variant="outlined" sx={{ borderColor: selected.has(a.id)? 'primary.main': overdue? 'error.main': 'divider' }}>
                <CardContent sx={{ display:'flex', flexDirection:'column', gap:1 }}>
                  <Stack direction="row" alignItems="center" gap={1}>
                    <Checkbox checked={selected.has(a.id)} onChange={()=>toggle(a.id)} />
                    <Typography variant="subtitle1" fontWeight={600}>{a.name}</Typography>
                  </Stack>
                  <Typography variant="body2" color="text.secondary">
                    {a.cleaning_interval_days ? `Кожні ${a.cleaning_interval_days} днів` : 'Без розкладу'}
                  </Typography>
                  <Stack direction="row" flexWrap="wrap" gap={1}>
                    <Button size="small" variant="contained" onClick={()=>changeInterval(a.id, a.cleaning_interval_days? null : 7)}>
                      {a.cleaning_interval_days ? 'Скасувати' : 'Встановити 7 днів'}
                    </Button>
                    <Button size="small" variant="outlined" onClick={()=>loadTasks(a.id)}>Завдання</Button>
                  </Stack>
                  {tasks[a.id] && (
                    <Table size="small" sx={{ mt:1 }}>
                      <TableHead>
                        <TableRow>
                          <TableCell>Термін</TableCell>
                          <TableCell>Статус</TableCell>
                          <TableCell>Дія</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {tasks[a.id].map(t => {
                          const pastDue = !t.completed && new Date(t.due_date) < new Date();
                          return (
                            <TableRow key={t.id} selected={pastDue}>
                              <TableCell>{t.due_date}</TableCell>
                              <TableCell>{t.completed ? '✓' : 'Очікує'}</TableCell>
                              <TableCell>
                                {t.completed ? (t.completed_at?.slice(0,19).replace('T',' ')) : (
                                  <Button size="small" variant="text" onClick={()=>markComplete(t)}>Завершити</Button>
                                )}
                              </TableCell>
                            </TableRow>
                          );
                        })}
                      </TableBody>
                    </Table>
                  )}
                </CardContent>
              </Card>
            );
          })}
        </Box>
      </CardContent>
    </Box>
  );
}
