import { useState, useEffect } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useSearchParams } from 'react-router-dom'
import api from '../api/client'
import { useAuth } from '../context/useAuth'

const TABS = [
  { id: 'events',          label: 'Events',          desc: 'Create & delete events' },
  { id: 'results',         label: 'Results',         desc: 'Record athlete results' },
  { id: 'accommodations',  label: 'Accommodations',  desc: 'Manage athlete housing' },
  { id: 'sports',          label: 'Sports',          desc: 'Add sport disciplines' },
  { id: 'venues',          label: 'Venues',          desc: 'Add competition venues' },
]

export default function AdminPage() {
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const [searchParams, setSearchParams] = useSearchParams()
  const [tab, setTab] = useState(searchParams.get('tab') || 'events')

  // Sync tab from URL query param (used by navbar dropdown)
  useEffect(() => {
    const t = searchParams.get('tab')
    if (t && TABS.find(x => x.id === t)) setTab(t)
  }, [searchParams])

  function switchTab(t) {
    setTab(t)
    setSearchParams({ tab: t })
  }

  const { data: profile, isLoading: loadingProfile } = useQuery({
    queryKey: ['profiles', user?.username],
    queryFn: () => api.get(`/api/v1/profiles/${user.username}/`),
    enabled: !!user,
  })

  if (!user || loadingProfile) return <div className="page-container"><p>Loading…</p></div>
  if (profile?.role !== 'staff') {
    return (
      <div className="page-container">
        <h1 className="page-title">Access Denied</h1>
        <p className="page-status">This page is restricted to staff members.</p>
      </div>
    )
  }

  const activeTab = TABS.find(t => t.id === tab) || TABS[0]

  return (
    <div className="admin-layout">
      {/* Sidebar */}
      <aside className="admin-sidebar">
        <div className="admin-sidebar-header">
          <span className="admin-sidebar-title">Staff Panel</span>
          <span className="admin-sidebar-user">@{user.username}</span>
        </div>
        <nav className="admin-sidebar-nav">
          {TABS.map(t => (
            <button
              key={t.id}
              className={`admin-sidebar-item${tab === t.id ? ' active' : ''}`}
              onClick={() => switchTab(t.id)}
            >
              <span className="admin-sidebar-label">{t.label}</span>
            </button>
          ))}
        </nav>
      </aside>

      {/* Main content */}
      <div className="admin-main">
        <div className="admin-main-header">
          <h1 className="admin-main-title">{activeTab.label}</h1>
          <p className="admin-main-desc">{activeTab.desc}</p>
        </div>

        <div className="admin-panel">
          {tab === 'events'         && <EventsTab qc={queryClient} />}
          {tab === 'sports'         && <SportsTab qc={queryClient} />}
          {tab === 'venues'         && <VenuesTab qc={queryClient} />}
          {tab === 'results'        && <ResultsTab qc={queryClient} />}
          {tab === 'accommodations' && <AccommodationsTab qc={queryClient} />}
        </div>
      </div>
    </div>
  )
}

// ── Events Tab ────────────────────────────────────────────────────────────────

function EventsTab({ qc }) {
  const [form, setForm] = useState({ name: '', sport: '', venue: '', start_time: '', end_time: '', ticket_capacity: 100 })
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  const { data: events = [] } = useQuery({ queryKey: ['events'], queryFn: () => api.get('/api/v1/events/') })
  const { data: sports = [] } = useQuery({ queryKey: ['sports'], queryFn: () => api.get('/api/v1/sports/') })
  const { data: venues = [] } = useQuery({ queryKey: ['venues'], queryFn: () => api.get('/api/v1/venues/') })

  async function handleCreate(e) {
    e.preventDefault()
    setSaving(true); setError('')
    try {
      await api.post('/api/v1/events/', form)
      qc.invalidateQueries({ queryKey: ['events'] })
      setForm({ name: '', sport: '', venue: '', start_time: '', end_time: '', ticket_capacity: 100 })
    } catch (err) { setError(err.message) }
    finally { setSaving(false) }
  }

  async function handleDelete(id) {
    if (!confirm('Delete this event?')) return
    await api.delete(`/api/v1/events/${id}/`)
    qc.invalidateQueries({ queryKey: ['events'] })
  }

  return (
    <div>
      <h2 className="admin-section-title">Create Event</h2>
      <form className="admin-form" onSubmit={handleCreate}>
        {error && <p className="admin-error">{error}</p>}
        <input placeholder="Event name" value={form.name} onChange={e => setForm(f => ({...f, name: e.target.value}))} required />
        <select value={form.sport} onChange={e => setForm(f => ({...f, sport: e.target.value}))} required>
          <option value="">Select sport</option>
          {sports.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
        </select>
        <select value={form.venue} onChange={e => setForm(f => ({...f, venue: e.target.value}))} required>
          <option value="">Select venue</option>
          {venues.map(v => <option key={v.id} value={v.id}>{v.name}</option>)}
        </select>
        <label>Start time <input type="datetime-local" value={form.start_time} onChange={e => setForm(f => ({...f, start_time: e.target.value}))} required /></label>
        <label>End time <input type="datetime-local" value={form.end_time} onChange={e => setForm(f => ({...f, end_time: e.target.value}))} required /></label>
        <label>Ticket capacity <input type="number" min="1" value={form.ticket_capacity} onChange={e => setForm(f => ({...f, ticket_capacity: parseInt(e.target.value)}))} required /></label>
        <button type="submit" className="admin-btn-primary" disabled={saving}>{saving ? 'Creating…' : 'Create Event'}</button>
      </form>

      <h2 className="admin-section-title" style={{marginTop:'32px'}}>All Events ({events.length})</h2>
      <table className="data-table">
        <thead><tr><th>Name</th><th>Sport</th><th>Venue</th><th>Date</th><th>Capacity</th><th></th></tr></thead>
        <tbody>
          {events.map(ev => (
            <tr key={ev.id}>
              <td className="td-bold">{ev.name}</td>
              <td>{ev.sport_name}</td>
              <td>{ev.venue_name}</td>
              <td>{new Date(ev.start_time).toLocaleDateString('en-GB')}</td>
              <td>{ev.ticket_capacity}</td>
              <td><button className="admin-btn-danger" onClick={() => handleDelete(ev.id)}>Delete</button></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

// ── Sports Tab ────────────────────────────────────────────────────────────────

function SportsTab({ qc }) {
  const [form, setForm] = useState({ name: '', description: '' })
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  const { data: sports = [] } = useQuery({ queryKey: ['sports'], queryFn: () => api.get('/api/v1/sports/') })

  async function handleCreate(e) {
    e.preventDefault()
    setSaving(true); setError('')
    try {
      await api.post('/api/v1/sports/', form)
      qc.invalidateQueries({ queryKey: ['sports'] })
      setForm({ name: '', description: '' })
    } catch (err) { setError(err.message) }
    finally { setSaving(false) }
  }

  return (
    <div>
      <h2 className="admin-section-title">Add Sport</h2>
      <form className="admin-form" onSubmit={handleCreate}>
        {error && <p className="admin-error">{error}</p>}
        <input placeholder="Sport name" value={form.name} onChange={e => setForm(f => ({...f, name: e.target.value}))} required />
        <textarea placeholder="Description (optional)" value={form.description} onChange={e => setForm(f => ({...f, description: e.target.value}))} />
        <button type="submit" className="admin-btn-primary" disabled={saving}>{saving ? 'Adding…' : 'Add Sport'}</button>
      </form>

      <h2 className="admin-section-title" style={{marginTop:'32px'}}>All Sports</h2>
      <table className="data-table">
        <thead><tr><th>Name</th><th>Description</th></tr></thead>
        <tbody>
          {sports.map(s => (
            <tr key={s.id}>
              <td className="td-bold">{s.name}</td>
              <td>{s.description || '—'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

// ── Venues Tab ────────────────────────────────────────────────────────────────

function VenuesTab({ qc }) {
  const [form, setForm] = useState({ name: '', location: '', capacity: 1000 })
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  const { data: venues = [] } = useQuery({ queryKey: ['venues'], queryFn: () => api.get('/api/v1/venues/') })

  async function handleCreate(e) {
    e.preventDefault()
    setSaving(true); setError('')
    try {
      await api.post('/api/v1/venues/', form)
      qc.invalidateQueries({ queryKey: ['venues'] })
      setForm({ name: '', location: '', capacity: 1000 })
    } catch (err) { setError(err.message) }
    finally { setSaving(false) }
  }

  return (
    <div>
      <h2 className="admin-section-title">Add Venue</h2>
      <form className="admin-form" onSubmit={handleCreate}>
        {error && <p className="admin-error">{error}</p>}
        <input placeholder="Venue name" value={form.name} onChange={e => setForm(f => ({...f, name: e.target.value}))} required />
        <input placeholder="Location" value={form.location} onChange={e => setForm(f => ({...f, location: e.target.value}))} required />
        <label>Capacity <input type="number" min="1" value={form.capacity} onChange={e => setForm(f => ({...f, capacity: parseInt(e.target.value)}))} required /></label>
        <button type="submit" className="admin-btn-primary" disabled={saving}>{saving ? 'Adding…' : 'Add Venue'}</button>
      </form>

      <h2 className="admin-section-title" style={{marginTop:'32px'}}>All Venues</h2>
      <table className="data-table">
        <thead><tr><th>Name</th><th>Location</th><th>Capacity</th></tr></thead>
        <tbody>
          {venues.map(v => (
            <tr key={v.id}>
              <td className="td-bold">{v.name}</td>
              <td>{v.location}</td>
              <td>{v.capacity}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

// ── Results Tab ───────────────────────────────────────────────────────────────

function ResultsTab({ qc }) {
  const [form, setForm] = useState({ event: '', athlete: '', rank: '', medal: 'N', score: '' })
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  const { data: events = [] }   = useQuery({ queryKey: ['events'],   queryFn: () => api.get('/api/v1/events/') })
  const { data: athletes = [] } = useQuery({ queryKey: ['athletes'], queryFn: () => api.get('/api/v1/athletes/') })

  async function handleCreate(e) {
    e.preventDefault()
    setSaving(true); setError('')
    try {
      const payload = { ...form, rank: form.rank ? parseInt(form.rank) : null }
      await api.post('/api/v1/results/', payload)
      qc.invalidateQueries({ queryKey: ['events'] })
      setForm({ event: '', athlete: '', rank: '', medal: 'N', score: '' })
    } catch (err) { setError(err.message) }
    finally { setSaving(false) }
  }

  return (
    <div>
      <h2 className="admin-section-title">Add Result</h2>
      <form className="admin-form" onSubmit={handleCreate}>
        {error && <p className="admin-error">{error}</p>}
        <select value={form.event} onChange={e => setForm(f => ({...f, event: e.target.value}))} required>
          <option value="">Select event</option>
          {events.map(ev => <option key={ev.id} value={ev.id}>{ev.name}</option>)}
        </select>
        <select value={form.athlete} onChange={e => setForm(f => ({...f, athlete: e.target.value}))} required>
          <option value="">Select athlete</option>
          {athletes.map(a => <option key={a.id} value={a.id}>{a.full_name || a.username} ({a.country_name})</option>)}
        </select>
        <select value={form.medal} onChange={e => setForm(f => ({...f, medal: e.target.value}))}>
          <option value="N">No medal</option>
          <option value="G">Gold</option>
          <option value="S">Silver</option>
          <option value="B">Bronze</option>
        </select>
        <input placeholder="Rank (optional)" type="number" min="1" value={form.rank} onChange={e => setForm(f => ({...f, rank: e.target.value}))} />
        <input placeholder="Score (optional)" value={form.score} onChange={e => setForm(f => ({...f, score: e.target.value}))} />
        <button type="submit" className="admin-btn-primary" disabled={saving}>{saving ? 'Saving…' : 'Add Result'}</button>
      </form>
    </div>
  )
}

// ── Accommodations Tab ────────────────────────────────────────────────────────

function AccommodationsTab({ qc }) {
  const [form, setForm] = useState({ name: '', location: '', capacity: 10 })
  const [assignForm, setAssignForm] = useState({ accommodation: '', athlete: '' })
  const [error, setError] = useState('')
  const [assignError, setAssignError] = useState('')
  const [saving, setSaving] = useState(false)
  const [assigning, setAssigning] = useState(false)

  const { data: accommodations = [] } = useQuery({ queryKey: ['accommodations'], queryFn: () => api.get('/api/v1/accommodations/') })
  const { data: athletes = [] }       = useQuery({ queryKey: ['athletes'],       queryFn: () => api.get('/api/v1/athletes/') })

  async function handleCreate(e) {
    e.preventDefault()
    setSaving(true); setError('')
    try {
      await api.post('/api/v1/accommodations/', form)
      qc.invalidateQueries({ queryKey: ['accommodations'] })
      setForm({ name: '', location: '', capacity: 10 })
    } catch (err) { setError(err.message) }
    finally { setSaving(false) }
  }

  async function handleAssign(e) {
    e.preventDefault()
    setAssigning(true); setAssignError('')
    try {
      await api.post(`/api/v1/accommodations/${assignForm.accommodation}/assign/`, { athlete_id: assignForm.athlete })
      qc.invalidateQueries({ queryKey: ['accommodations'] })
      setAssignForm({ accommodation: '', athlete: '' })
    } catch (err) { setAssignError(err.message) }
    finally { setAssigning(false) }
  }

  return (
    <div>
      <h2 className="admin-section-title">Create Accommodation</h2>
      <form className="admin-form" onSubmit={handleCreate}>
        {error && <p className="admin-error">{error}</p>}
        <input placeholder="Name" value={form.name} onChange={e => setForm(f => ({...f, name: e.target.value}))} required />
        <input placeholder="Location" value={form.location} onChange={e => setForm(f => ({...f, location: e.target.value}))} required />
        <label>Capacity <input type="number" min="1" value={form.capacity} onChange={e => setForm(f => ({...f, capacity: parseInt(e.target.value)}))} required /></label>
        <button type="submit" className="admin-btn-primary" disabled={saving}>{saving ? 'Creating…' : 'Create'}</button>
      </form>

      <h2 className="admin-section-title" style={{marginTop:'32px'}}>Assign Athlete</h2>
      <form className="admin-form" onSubmit={handleAssign}>
        {assignError && <p className="admin-error">{assignError}</p>}
        <select value={assignForm.accommodation} onChange={e => setAssignForm(f => ({...f, accommodation: e.target.value}))} required>
          <option value="">Select accommodation</option>
          {accommodations.map(a => <option key={a.id} value={a.id}>{a.name} ({a.spots_remaining} spots left)</option>)}
        </select>
        <select value={assignForm.athlete} onChange={e => setAssignForm(f => ({...f, athlete: e.target.value}))} required>
          <option value="">Select athlete</option>
          {athletes.map(a => <option key={a.id} value={a.id}>{a.full_name || a.username}</option>)}
        </select>
        <button type="submit" className="admin-btn-primary" disabled={assigning}>{assigning ? 'Assigning…' : 'Assign'}</button>
      </form>

      <h2 className="admin-section-title" style={{marginTop:'32px'}}>All Accommodations</h2>
      <table className="data-table">
        <thead><tr><th>Name</th><th>Location</th><th>Capacity</th><th>Spots left</th><th>Assigned athletes</th></tr></thead>
        <tbody>
          {accommodations.map(acc => (
            <tr key={acc.id}>
              <td className="td-bold">{acc.name}</td>
              <td>{acc.location}</td>
              <td>{acc.capacity}</td>
              <td>{acc.spots_remaining}</td>
              <td>{acc.assigned_athletes?.map(a => a.username).join(', ') || '—'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
