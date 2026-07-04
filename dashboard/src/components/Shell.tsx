import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';

export function Shell() {
  return (
    <div className="shell">
      <Sidebar />
      <div className="main">
        <Outlet />
      </div>
    </div>
  );
}
