import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import api from '../api/client'
import MedalBadge from '../components/MedalBadge'
import { useAuth } from '../context/useAuth'

export default function EventDetailPage() {
  const { id } = useParams()
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const [booking, setBooking] = useState(false)
  const [booked, setBooked] = useState(false)
  const [bookError, setBookError] = useState('')

  const { data: event, isLoading, isError } = useQuery({
    queryKey: ['event', id],
    queryFn: () => api.get(`/api/v1/events/${id}/`),
  })

  if (isLoading) return <p className="page-status">Loading event…</p>
  if (isError || !event) return <p className="page-status">Event not found.</p>

  const start = new Date(event.start_time)
  const dateStr = start.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' })
  const timeStr = start.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })

  const hasResults = event.results && event.results.length > 0

  async function handleBook() {
    if (!user) return
    setBooking(true)
    setBookError('')
    try {
      await api.post('/api/v1/tickets/book/', { event_id: event.id })
      setBooked(true)
      queryClient.invalidateQueries({ queryKey: ['my-tickets', user.username] })
    } catch (err) {
      setBookError(err.message || 'Booking failed.')
    } finally {
      setBooking(false)
    }
  }

  return (
    <div className="page-container">
      <Link to="/schedule" className="back-link">← Back to Schedule</Link>

      <div className="event-detail-header">
        <span className="event-card-sport">{event.sport_name}</span>
        <h1 className="page-title">{event.name}</h1>
      </div>

      <div className="detail-layout">
        {/* Results table */}
        <div className="detail-main">
          <h2 className="section-heading">Results</h2>
          {hasResults ? (
            <table className="data-table">
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>Athlete</th>
                  <th>Medal</th>
                  <th>Score</th>
                </tr>
              </thead>
              <tbody>
                {event.results.map(result => (
                  <tr key={result.id}>
                    <td>{result.rank ?? '—'}</td>
                    <td className="td-bold">{result.athlete_name}</td>
                    <td><MedalBadge medal={result.medal} /></td>
                    <td className="td-mono">{result.score || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p className="page-status">Results not yet available.</p>
          )}
        </div>

        {/* Sidebar */}
        <aside className="detail-sidebar">
          <h3 className="sidebar-title">Details</h3>
          <div className="sidebar-row">
            <span className="sidebar-label">Venue</span>
            <span>{event.venue_name}</span>
          </div>
          <div className="sidebar-row">
            <span className="sidebar-label">Date</span>
            <span>{dateStr}</span>
          </div>
          <div className="sidebar-row">
            <span className="sidebar-label">Time</span>
            <span>{timeStr}</span>
          </div>
          <div className="sidebar-row">
            <span className="sidebar-label">Capacity</span>
            <span>{event.ticket_capacity} seats</span>
          </div>

          {bookError && <p className="book-error">{bookError}</p>}
          {!user ? (
            <Link to="/login" className="btn-book" style={{ textAlign: 'center' }}>Login to book</Link>
          ) : booked ? (
            <p className="booked-msg">Ticket booked!</p>
          ) : (
            <button className="btn-book" disabled={booking} onClick={handleBook}>
              {booking ? 'Booking…' : 'Book ticket'}
            </button>
          )}
        </aside>
      </div>
    </div>
  )
}
