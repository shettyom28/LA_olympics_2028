import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import api from '../api/client'
import AthleteCard from '../components/AthleteCard'
import { useAuth } from '../context/useAuth'

export default function AthletesPage() {
  const { user } = useAuth()
  const [search, setSearch] = useState('')
  const [sportFilter, setSportFilter] = useState('')

  const { data: athletes = [], isLoading, isError } = useQuery({
    queryKey: ['athletes'],
    queryFn: () => api.get('/api/v1/athletes/'),
  })

  // Build a map of athleteId → favouriteId so AthleteCard knows which are already liked
  const { data: favourites = [] } = useQuery({
    queryKey: ['my-favourites', user?.username],
    queryFn: () => api.get('/api/v1/favourites/'),
    enabled: !!user,
  })
  const favAthleteMap = Object.fromEntries(
    favourites.filter(f => f.athlete).map(f => [f.athlete, f.id])
  )

  const sports = [...new Set(athletes.map(a => a.sport_name).filter(Boolean))]

  const filtered = athletes.filter(a => {
    const matchSearch = !search ||
      (a.full_name || a.username).toLowerCase().includes(search.toLowerCase()) ||
      a.country_name?.toLowerCase().includes(search.toLowerCase())
    const matchSport = !sportFilter || a.sport_name === sportFilter
    return matchSearch && matchSport
  })

  if (isLoading) return <p className="page-status">Loading athletes…</p>
  if (isError)   return <p className="page-status">Failed to load athletes.</p>

  return (
    <div className="page-container">
      <p className="lb-tag">OLYMPICS 2028</p>
      <h1 className="page-title">Athletes</h1>
      <p className="page-subtitle">{filtered.length} athlete{filtered.length !== 1 ? 's' : ''}</p>

      <div className="filters">
        <input
          type="text"
          className="athletes-search"
          placeholder="Search by name or country…"
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
        <select value={sportFilter} onChange={e => setSportFilter(e.target.value)}>
          <option value="">All sports</option>
          {sports.map(s => <option key={s} value={s}>{s}</option>)}
        </select>
        {(search || sportFilter) && (
          <button className="filter-reset" onClick={() => { setSearch(''); setSportFilter('') }}>
            Clear
          </button>
        )}
      </div>

      <div className="athletes-grid">
        {filtered.map(athlete => (
          <AthleteCard
            key={athlete.id}
            athlete={athlete}
            isFavourited={athlete.id in favAthleteMap}
            favouriteId={favAthleteMap[athlete.id] ?? null}
          />
        ))}
        {filtered.length === 0 && (
          <p className="page-status">No athletes match your search.</p>
        )}
      </div>
    </div>
  )
}
