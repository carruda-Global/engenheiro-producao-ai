import { NavLink } from 'react-router-dom';

const agents = [
  { id: 'spec-analyst', label: 'Spec Analyst', icon: '🔍' },
  { id: 'procurement', label: 'Procurement', icon: '🛒' },
  { id: 'inventory', label: 'Inventory', icon: '📦' },
  { id: 'logistics', label: 'Logistics', icon: '🚚' },
  { id: 'field-execution', label: 'Field Execution', icon: '🏗️' },
];

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <strong>🏗️ Eng. Producao AI</strong>
        <span className="version">v1.0</span>
      </div>
      <nav>
        <NavLink to="/" end className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
          📊 Dashboard
        </NavLink>
        <div className="nav-section">Agentes</div>
        {agents.map((a) => (
          <NavLink
            key={a.id}
            to={`/agent/${a.id}`}
            className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
          >
            {a.icon} {a.label}
          </NavLink>
        ))}
        <NavLink to="/subscription" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
          💳 Planos
        </NavLink>
      </nav>
    </aside>
  );
}
