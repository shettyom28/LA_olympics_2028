import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useSearchParams } from 'react-router-dom'
import api from '../api/client'
import EventCard from '../components/EventCard'
import { useAuth } from '../context/useAuth'

export default function SchedulePage() {
  const { user } = useAuth()
  const [searchParams] = useSearchParams()
  const [sportFilter, setSportFilter] = useState('')
  const [venueFilter, setVenueFilter] = useState(
    searchParams.get('venue') ? decodeURIComponent(searchParams.get('venue')) : ''
  )
  const [dateFilter, setDateFilter] = useState('')

  const { data: events = [], isLoading, isError } = useQuery({
    queryKey: ['events'],
    queryFn: () => api.get('/api/v1/events/'),
  })

  // Build a map of eventId → favouriteId so EventCard knows which are already liked
  const { data: favourites = [] } = useQuery({
    queryKey: ['my-favourites', user?.username],
    queryFn: () => api.get('/api/v1/favourites/'),
    enabled: !!user,
  })
  const favEventMap = Object.fromEntries(
    favourites.filter(f => f.event).map(f => [f.event, f.id])
  )

  if (isLoading) return <p className="page-status">Loading events…</p>
  if (isError)   return <p className="page-status">Failed to load events.</p>

  const sports = [...new Set(events.map(e => e.sport_name).filter(Boolean))]
  const venues = [...new Set(events.map(e => e.venue_name).filter(Boolean))]
  const dates  = [...new Set(events.map(e => e.start_time?.slice(0, 10)).filter(Boolean))].sort()

  const filtered = events.filter(e => {
    const matchSport = !sportFilter || e.sport_name === sportFilter
    const matchVenue = !venueFilter || e.venue_name === venueFilter
    const matchDate  = !dateFilter  || e.start_time?.startsWith(dateFilter)
    return matchSport && matchVenue && matchDate
  })

  return (
    <div className="page-container">
      <h1 className="page-title">Event Schedule</h1>
      <p className="page-subtitle">{filtered.length} event{filtered.length !== 1 ? 's' : ''}</p>

      <div className="filters">
        <select value={sportFilter} onChange={e => setSportFilter(e.target.value)}>
          <option value="">All sports</option>
          {sports.map(s => <option key={s} value={s}>{s}</option>)}
        </select>

        <select value={venueFilter} onChange={e => setVenueFilter(e.target.value)}>
          <option value="">All venues</option>
          {venues.map(v => <option key={v} value={v}>{v}</option>)}
        </select>

        <select value={dateFilter} onChange={e => setDateFilter(e.target.value)}>
          <option value="">All dates</option>
          {dates.map(d => <option key={d} value={d}>{d}</option>)}
        </select>

        {(sportFilter || venueFilter || dateFilter) && (
          <button className="filter-reset" onClick={() => { setSportFilter(''); setVenueFilter(''); setDateFilter('') }}>
            Clear filters
          </button>
        )}
      </div>

      <div className="event-list">
        {filtered.map(event => (
          <EventCard
            key={event.id}
            event={event}
            isFavourited={event.id in favEventMap}
            favouriteId={favEventMap[event.id] ?? null}
          />
        ))}
        {filtered.length === 0 && <p className="page-status">No events match those filters.</p>}
      </div>
    </div>
  )
}
