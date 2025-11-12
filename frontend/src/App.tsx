import { Appliances } from './components/Appliances';
import { Dashboard } from './components/Dashboard';
import './app.css';

export default function App() {
  return (
    <div className="layout">
      <header><h1>Home Dashboard</h1></header>
      <main>
        <Dashboard />
        <Appliances />
      </main>
    </div>
  );
}
