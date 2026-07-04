import { NavLink } from 'react-router-dom';
import { Icon, Shield } from './icons';

const NAV = [
  { to: '/', label: 'Overview', icon: 'overview' },
  { to: '/registry', label: 'Registry', icon: 'registry' },
  { to: '/leaderboard', label: 'Leaderboard', icon: 'leaderboard' },
  { to: '/adoption', label: 'Adoption', icon: 'adoption' },
  { to: '/context', label: 'Context', icon: 'context' },
];

export function Sidebar() {
  return (
    <nav className="sidebar">
      <div className="sidebar-wordmark">
        <Shield />
        <span className="sidebar-brand">sovereign</span>
      </div>
      <div className="sidebar-section">PLATFORM</div>
      {NAV.map((item) => (
        <NavLink
          key={item.to}
          to={item.to}
          end={item.to === '/'}
          className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}
        >
          <Icon name={item.icon} />
          <span>{item.label}</span>
        </NavLink>
      ))}
    </nav>
  );
}
