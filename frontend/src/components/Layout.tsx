import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

const nav = [
  { to: '/', label: 'Dashboard' },
  { to: '/assets', label: 'Assets' },
  { to: '/locations', label: 'Locations' },
  { to: '/categories', label: 'Categories' },
  { to: '/departments', label: 'Departments' },
]

export default function Layout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b border-[var(--border)] bg-[var(--card)] px-6 py-4 flex items-center justify-between">
        <nav className="flex items-center gap-6">
          <span className="font-semibold text-[var(--accent)]">Asset Tracker</span>
          {nav.map(({ to, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                `text-sm ${isActive ? 'text-[var(--accent)]' : 'text-[var(--muted)] hover:text-white'}`
              }
            >
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="flex items-center gap-4">
          <span className="text-sm text-[var(--muted)]">{user?.email}</span>
          <button
            type="button"
            onClick={handleLogout}
            className="text-sm text-[var(--muted)] hover:text-white"
          >
            Log out
          </button>
        </div>
      </header>
      <main className="flex-1 p-6">
        <Outlet />
      </main>
    </div>
  )
}
