import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import api from '../api/client'

export default function VenuesPage() {
  const { data: venues = [], isLoading, isError } = useQuery({
    queryKey: ['venues'],
    queryFn: () => api.get('/api/v1/venues/'),
  })

  const { data: events = [] } = useQuery({
    queryKey: ['events'],
    queryFn: () => api.get('/api/v1/events/'),
  })

  if (isLoading) return <p className="page-status">Loading venues…</p>
  if (isError)   return <p className="page-status">Failed to load venues.</p>

  const eventCountByVenueId = events.reduce((acc, e) => {
    if (e.venue) acc[e.venue] = (acc[e.venue] || 0) + 1
    return acc
  }, {})

  return (
    <div className="page-container">
      <p className="lb-tag">OLYMPICS 2028</p>
      <h1 className="page-title">Venues</h1>
      <p className="page-subtitle">{venues.length} official venue{venues.length !== 1 ? 's' : ''} · Los Angeles, CA</p>

      {venues.length === 0 && (
        <p className="page-status">No venues available yet.</p>
      )}

      <div className="venues-grid">
        {venues.map(venue => {
          const count = eventCountByVenueId[venue.id] || 0
          const mapUrl = `https://www.openstreetmap.org/search?query=${encodeURIComponent(venue.location)}`
          return (
            <div key={venue.id} className="venue-card">
              <div className="venue-card-top">
                <h2 className="venue-name">{venue.name}</h2>
                <span className="venue-capacity-badge">{venue.capacity.toLocaleString()} seats</span>
              </div>
              <p className="venue-location">📍 {venue.location}</p>
              <div className="venue-card-footer">
                <Link to={`/schedule?venue=${encodeURIComponent(venue.name)}`} className="venue-events-link">
                  {count} event{count !== 1 ? 's' : ''}
                </Link>
                <a href={mapUrl} target="_blank" rel="noopener noreferrer" className="venue-map-link">
                  View on map →
                </a>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
