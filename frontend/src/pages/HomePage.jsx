import { useState, useEffect, useRef } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import api from '../api/client'
import { useAuth } from '../context/useAuth'
import ExampleMessageCard from '../components/ExampleMessageCard'

function HomePage() {
  const { user } = useAuth()
  const queryClient = useQueryClient()
  const [content, setContent] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [flash, setFlash] = useState('')
  const flashTimer = useRef(null)

  const { data: messages, error: loadError, isLoading } = useQuery({
    queryKey: ['messages'],
    queryFn: () => api.get('/api/v1/example-messages/'),
  })

  useEffect(() => {
    const scheme = window.location.protocol === 'https:' ? 'wss' : 'ws'
    const ws = new WebSocket(`${scheme}://${window.location.host}/ws/notifications/`)

    console.log('WebSocket connected to /ws/notifications/')

    ws.onmessage = (e) => {
      const data = JSON.parse(e.data)
      if (data.type === 'notify') {
        console.log('WebSocket notification:', data.message)
        setFlash(`Websocket: ${data.message}`)
        clearTimeout(flashTimer.current)
        flashTimer.current = setTimeout(() => setFlash(''), 5000)
        queryClient.invalidateQueries({ queryKey: ['messages'] })
      }
    }

    return () => ws.close()
  }, [queryClient])

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setSubmitting(true)
    try {
      console.log('Posting message:', content)
      await api.post('/api/v1/example-messages/', { content })
      setContent('')
      queryClient.invalidateQueries({ queryKey: ['messages'] })
    } catch (err) {
      setError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  if (isLoading) return <p>Loading messages...</p>
  if (loadError) return <p>Error: {loadError.message}</p>

  return (
    <div>
      <h1>Message Board</h1>

      {flash && <p><strong>{flash}</strong></p>}

      {user ? (
        <form onSubmit={handleSubmit}>
          {error && <p style={{ color: 'red' }}>{error}</p>}
          <div>
            <label htmlFor="content">Message:</label><br />
            <textarea id="content" value={content} onChange={(e) => setContent(e.target.value)} required />
          </div>
          <button type="submit" disabled={submitting}>
            {submitting ? 'Posting...' : 'Post'}
          </button>
        </form>
      ) : (
        <p><Link to="/login">Login</Link> to post a message.</p>
      )}

      <h2>Messages</h2>
      {messages.length === 0 ? (
        <p>No messages yet.</p>
      ) : (
        messages.map((msg) => (
          <ExampleMessageCard key={msg.id} message={msg} />
        ))
      )}
    </div>
  )
}

export default HomePage
