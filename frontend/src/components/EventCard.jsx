import { useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../api/client'
import { useAuth } from '../context/useAuth'

function EventCard({ event, isFavourited = false, favouriteId = null, onFavouriteChange }) {
  const { user } = useAuth()
  const [fav, setFav] = useState(isFavourited)
  const [favId, setFavId] = useState(favouriteId)
  const [loading, setLoading] = useState(false)

  const date = new Date(event.start_time)
  const dateStr = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
  const timeStr = date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })

  async function toggleFav(e) {
    e.preventDefault()
    if (!user || loading) return
    setLoading(true)
    try {
      if (fav && favId) {
        await api.delete(`/api/v1/favourites/${favId}/`)
        setFav(false)
        setFavId(null)
        onFavouriteChange?.({ removed: true, eventId: event.id })
      } else {
        const data = await api.post('/api/v1/favourites/', { event: event.id })
        setFav(true)
        setFavId(data.id)
        onFavouriteChange?.({ removed: false, eventId: event.id, favouriteId: data.id })
      }
    } catch {
      // silently ignore (e.g. not logged in)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Link to={`/event/${event.id}`} className="event-card">
      <span className="event-card-sport">{event.sport_name}</span>
      <span className="event-card-name">{event.name}</span>
      <div className="event-card-meta">
        <span>{event.venue_name}</span>
        <span>{dateStr} · {timeStr}</span>
      </div>
      {user && (
        <span
          className="heart"
          onClick={toggleFav}
          title={fav ? 'Remove from favourites' : 'Add to favourites'}
          style={{ opacity: loading ? 0.5 : 1 }}
        >
          {fav ? '❤️' : '♡'}
        </span>
      )}
    </Link>
  )
}

export default EventCard
