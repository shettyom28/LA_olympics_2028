import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useParams, Link, useNavigate } from 'react-router-dom'
import api from '../api/client'
import { useAuth } from '../context/useAuth'

const ROLE_LABELS = { staff: 'Staff', athlete: 'Athlete', spectator: 'Spectator' }
const ROLE_COLORS = { staff: '#f59e0b', athlete: '#3b82f6', spectator: '#10b981' }

function formatDate(dateString) {
  return new Date(dateString).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })
}

function ProfilePage() {
  const { username } = useParams()
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const isOwn = user?.username === username

  const { data: profile, isLoading: loadingProfile, error } = useQuery({
    queryKey: ['profiles', username],
    queryFn: () => api.get(`/api/v1/profiles/${username}/`),
  })

  const { data: athletes } = useQuery({
    queryKey: ['athletes'],
    queryFn: () => api.get('/api/v1/athletes/'),
  })

  // Own-profile only: booked tickets
  const { data: tickets = [] } = useQuery({
    queryKey: ['my-tickets', user?.username],
    queryFn: () => api.get('/api/v1/tickets/'),
    enabled: isOwn,
  })

  // Own-profile only: favourites
  const { data: favourites = [] } = useQuery({
    queryKey: ['my-favourites', user?.username],
    queryFn: () => api.get('/api/v1/favourites/'),
    enabled: isOwn,
  })

  const athleteProfile = athletes?.find(a => a.username === username)
  const likedEvents    = favourites.filter(f => f.event)
  const likedAthletes  = favourites.filter(f => f.athlete)

  async function handleLogout() {
    await logout()
    navigate('/')
  }

  async function removeFavourite(favId) {
    await api.delete(`/api/v1/favourites/${favId}/`)
    queryClient.invalidateQueries({ queryKey: ['my-favourites', user?.username] })
  }

  if (loadingProfile) return <div className="page-container"><p>Loading…</p></div>
  if (error)          return <div className="page-container"><p>User not found.</p></div>

  const role       = profile?.role || 'spectator'
  const roleLabel  = ROLE_LABELS[role] || role
  const roleColor  = ROLE_COLORS[role] || '#64748b'
  const joinedDate = profile?.date_joined
    ? new Date(profile.date_joined).toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' })
    : '—'

  return (
    <div className="profile-page">
      {/* Header banner */}
      <div className="profile-banner">
        <div className="profile-banner-inner">
          <div className="profile-avatar">
            {username?.[0]?.toUpperCase()}
          </div>
          <div className="profile-identity">
            <h1 className="profile-username">{username}</h1>
            <span className="profile-role-badge" style={{ background: roleColor }}>
              {roleLabel}
            </span>
            {profile?.country_name && (
              <span className="profile-country">{profile.country_name}</span>
            )}
          </div>
          {isOwn && (
            <button className="profile-logout-btn" onClick={handleLogout}>
              Logout
            </button>
          )}
        </div>
      </div>

      <div className="profile-body">
        {/* Stats row */}
        <div className="profile-stats">
          <div className="profile-stat">
            <span className="profile-stat-value">{joinedDate}</span>
            <span className="profile-stat-label">Member since</span>
          </div>
          {isOwn && (
            <>
              <div className="profile-stat">
                <span className="profile-stat-value">{tickets.length}</span>
                <span className="profile-stat-label">Tickets booked</span>
              </div>
              <div className="profile-stat">
                <span className="profile-stat-value">{likedEvents.length}</span>
                <span className="profile-stat-label">Saved events</span>
              </div>
              <div className="profile-stat">
                <span className="profile-stat-value">{likedAthletes.length}</span>
                <span className="profile-stat-label">Following</span>
              </div>
            </>
          )}
        </div>

        {/* Athlete section */}
        {athleteProfile && (
          <div className="profile-card">
            <h2 className="profile-card-title">Athlete Profile</h2>
            <div className="profile-athlete-info">
              <div className="profile-info-row">
                <span className="profile-info-label">Sport</span>
                <span className="profile-info-value">{athleteProfile.sport_name}</span>
              </div>
              <div className="profile-info-row">
                <span className="profile-info-label">Country</span>
                <span className="profile-info-value">{athleteProfile.country_name}</span>
              </div>
              {athleteProfile.bio && (
                <div className="profile-info-row">
                  <span className="profile-info-label">Bio</span>
                  <span className="profile-info-value">{athleteProfile.bio}</span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* My Tickets — own profile only */}
        {isOwn && (
          <div className="profile-card">
            <h2 className="profile-card-title">
              My Tickets
              <Link to="/my-tickets" style={{ fontSize: '0.85rem', marginLeft: '1rem', color: '#b91c1c', fontWeight: 400 }}>
                View all
              </Link>
            </h2>
            {tickets.length === 0 ? (
              <p className="profile-empty">No tickets yet. <Link to="/schedule">Browse the schedule</Link></p>
            ) : (
              <ul className="profile-list">
                {tickets.slice(0, 5).map(t => (
                  <li key={t.id} className="profile-list-item">
                    <Link to={`/event/${t.event}`} className="profile-list-name">{t.event_name}</Link>
                    {t.event_start_time && (
                      <span className="profile-list-meta">{formatDate(t.event_start_time)}</span>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}

        {/* Liked events — own profile only */}
        {isOwn && (
          <div className="profile-card">
            <h2 className="profile-card-title">Saved Events</h2>
            {likedEvents.length === 0 ? (
              <p className="profile-empty">No saved events yet.</p>
            ) : (
              <ul className="profile-list">
                {likedEvents.map(f => (
                  <li key={f.id} className="profile-list-item">
                    <Link to={`/event/${f.event}`} className="profile-list-name">{f.event_name}</Link>
                    {f.event_start_time && (
                      <span className="profile-list-meta">{formatDate(f.event_start_time)}</span>
                    )}
                    <button
                      className="profile-list-remove"
                      onClick={() => removeFavourite(f.id)}
                      title="Remove"
                    >
                      ✕
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}

        {/* Liked athletes — own profile only */}
        {isOwn && likedAthletes.length > 0 && (
          <div className="profile-card">
            <h2 className="profile-card-title">Following</h2>
            <ul className="profile-list">
              {likedAthletes.map(f => (
                <li key={f.id} className="profile-list-item">
                  <span className="profile-list-name">{f.athlete_name}</span>
                  <span className="profile-list-meta">{f.athlete_sport}</span>
                  <button
                    className="profile-list-remove"
                    onClick={() => removeFavourite(f.id)}
                    title="Unfollow"
                  >
                    ✕
                  </button>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Account info */}
        <div className="profile-card">
          <h2 className="profile-card-title">Account</h2>
          <div className="profile-info-row">
            <span className="profile-info-label">Username</span>
            <span className="profile-info-value">@{username}</span>
          </div>
          <div className="profile-info-row">
            <span className="profile-info-label">Role</span>
            <span className="profile-info-value" style={{ color: roleColor, fontWeight: 600 }}>{roleLabel}</span>
          </div>
          {profile?.country_name && (
            <div className="profile-info-row">
              <span className="profile-info-label">Country</span>
              <span className="profile-info-value">{profile.country_name}</span>
            </div>
          )}
        </div>

        {/* Quick links */}
        <div className="profile-card">
          <h2 className="profile-card-title">Explore</h2>
          <div className="profile-links">
            <Link to="/schedule" className="profile-link-btn">View Schedule</Link>
            <Link to="/athletes" className="profile-link-btn">Browse Athletes</Link>
            <Link to="/leaderboard" className="profile-link-btn">Leaderboard</Link>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ProfilePage
