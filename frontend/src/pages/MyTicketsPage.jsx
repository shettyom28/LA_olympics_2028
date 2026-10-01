import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import api from '../api/client'
import { useAuth } from '../context/useAuth'

function formatDate(dateString) {
  return new Date(dateString).toLocaleDateString('en-GB', { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' })
}

function formatTime(dateString) {
  return new Date(dateString).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' })
}

export default function MyTicketsPage() {
  const { user } = useAuth()
  const { data: tickets = [], isLoading, isError } = useQuery({
    queryKey: ['my-tickets', user?.username],
    queryFn: () => api.get('/api/v1/tickets/'),
    enabled: !!user,
  })

  if (isLoading) return <p className="page-status">Loading tickets…</p>
  if (isError)   return <p className="page-status">Could not load tickets.</p>

  return (
    <div className="page-container">
      <h1 className="page-title">Your Tickets</h1>
      <p className="page-subtitle">{tickets.length} booked</p>

      {tickets.length === 0 && (
        <p className="page-status">
          Nothing booked yet.{' '}
          <Link to="/schedule" style={{ color: '#b91c1c' }}>Browse the schedule</Link>
        </p>
      )}

      {tickets.length > 0 && (
        <div className="ticket-list">
          {tickets.map(ticket => (
            <div key={ticket.id} className="ticket-card">
              <div className="ticket-card-left">
                <span className="ticket-sport">{ticket.event_sport}</span>
                <Link to={`/event/${ticket.event}`} className="ticket-event-name">
                  {ticket.event_name}
                </Link>
                <span className="ticket-venue">📍 {ticket.event_venue}</span>
              </div>
              <div className="ticket-card-right">
                <span className="ticket-date">{ticket.event_start_time ? formatDate(ticket.event_start_time) : '—'}</span>
                <span className="ticket-time">{ticket.event_start_time ? formatTime(ticket.event_start_time) : '—'}</span>
                <span className="ticket-booked">Booked {formatDate(ticket.booked_at)}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
