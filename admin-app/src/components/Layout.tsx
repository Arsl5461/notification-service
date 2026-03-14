
import { Link, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
export function Layout() {
  const { user, logout } = useAuth();
  const location = useLocation();
  const nav = [
    { to: '/locations', label: 'Locations' },
    { to: '/workers', label: 'Workers' },
    { to: '/schedules', label: 'Schedules' },
  ];

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <header
        style={{
          background: '#1e293b',
          color: 'white',
          padding: '0.75rem 1.5rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '0.5rem',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
          <Link to="/" style={{ color: 'white', fontWeight: 700, fontSize: '1.125rem' }}>
            Company Admin
          </Link>
          <nav style={{ display: 'flex', gap: '1rem' }}>
            {nav.map(({ to, label }) => (
              <Link
                key={to}
                to={to}
                style={{
                  color: location.pathname === to ? '#93c5fd' : 'rgba(255,255,255,0.9)',
                  padding: '0.25rem 0.5rem',
                  borderRadius: 4,
                }}
              >
                {label}
              </Link>
            ))}
          </nav>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <span style={{ fontSize: '0.875rem', opacity: 0.9 }}>{user?.email}</span>
          <button type="button" onClick={logout} className="secondary">
            Log out
          </button>
        </div>
      </header>
      <main style={{ flex: 1, padding: '1.5rem', maxWidth: 1200, margin: '0 auto', width: '100%' }}>
        <Outlet />
      </main>
    </div>
  );
}
