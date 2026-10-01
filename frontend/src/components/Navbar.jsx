import { useState, useRef, useEffect } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { useAuth } from '../context/useAuth'
import api from '../api/client'

function Navbar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [staffOpen, setStaffOpen] = useState(false)
  const dropdownRef = useRef(null)

  const { data: profile } = useQuery({
    queryKey: ['profiles', user?.username],
    queryFn: () => api.get(`/api/v1/profiles/${user.username}/`),
    enabled: !!user,
  })
  const isStaff = profile?.role === 'staff'

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClick(e) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setStaffOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClick)
    return () => document.removeEventListener('mousedown', handleClick)
  }, [])

  // Close dropdown on route change
  useEffect(() => { setStaffOpen(false) }, [location.pathname])

  async function handleLogout() {
    await logout()
    navigate('/')
  }

  function navLink(to, label) {
    const active = location.pathname === to
    return (
      <li>
        <Link to={to} className={active ? 'nav-active' : ''}>{label}</Link>
      </li>
    )
  }

  return (
    <nav className="app-navbar">
      <div className="app-navbar-brand">
        <Link to="/" className="app-navbar-logo">Olympics 2028</Link>
      </div>

      <ul className="app-navbar-links">
        {navLink('/schedule', 'Schedule')}
        {navLink('/athletes', 'Athletes')}
        {navLink('/leaderboard', 'Leaderboard')}
        {navLink('/venues', 'Venues')}
      </ul>

      <div className="app-navbar-auth">
        {user ? (
          <>
            <Link to="/my-tickets" className={`app-navbar-icon-link${location.pathname === '/my-tickets' ? ' active' : ''}`} title="My Tickets">
              Tickets
            </Link>

            {isStaff && (
              <div className="staff-dropdown" ref={dropdownRef}>
                <button
                  className={`staff-dropdown-btn${staffOpen ? ' open' : ''}`}
                  onClick={() => setStaffOpen(o => !o)}
                >
                  Staff {staffOpen ? '▴' : '▾'}
                </button>
                {staffOpen && (
                  <div className="staff-dropdown-menu">
                    <Link to="/admin" className="staff-dropdown-item">Dashboard</Link>
                    <Link to="/admin?tab=events" className="staff-dropdown-item">Events</Link>
                    <Link to="/admin?tab=results" className="staff-dropdown-item">Results</Link>
                    <Link to="/admin?tab=accommodations" className="staff-dropdown-item">Accommodations</Link>
                    <Link to="/admin?tab=sports" className="staff-dropdown-item">Sports</Link>
                    <Link to="/admin?tab=venues" className="staff-dropdown-item">Venues</Link>
                  </div>
                )}
              </div>
            )}

            <Link to={`/profile/${user.username}`} className="app-navbar-user">
              {user.username}
            </Link>
            <button className="app-navbar-btn" onClick={handleLogout}>Logout</button>
          </>
        ) : (
          <>
            <Link to="/login" className="app-navbar-btn outline">Login</Link>
            <Link to="/register" className="app-navbar-btn">Register</Link>
          </>
        )}
      </div>
    </nav>
  )
}

export default Navbar
