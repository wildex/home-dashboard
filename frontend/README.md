# Home Dashboard React Frontend

## Setup
```bash
npm install
npm run dev
```
Visit http://localhost:5173

Set API base (optional): create `.env.local` with:
```
VITE_API_BASE=http://127.0.0.1:8000
```

## Scripts
- `npm run dev` start Vite dev server
- `npm run build` production build
- `npm run preview` preview production build
- `npm run typecheck` run TypeScript compiler in no-emit mode

## Theming
A dark theme is provided via MUI ThemeProvider (see `src/theme.ts`). Global reset comes from `<CssBaseline />`. You can adjust palette or component overrides in that file.

If you prefer to avoid MUI, remove the ThemeProvider/CssBaseline wrapper in `src/main.tsx` and uninstall the MUI + emotion packages.

## Features
- Dashboard view (overdue tasks + recent temperature)
- Appliance CRUD: create, interval toggle (set 7d / unschedule), bulk delete
- Task listing & completion
- Inline refresh buttons & overdue highlighting

## Next Ideas
- Routing (React Router) for detailed appliance page
- Form validation & toasts
- WebSocket for live temperature
- Dark/light theme toggle
- Replace manual fetch wrappers with React Query for caching
