import { useState, useRef, useEffect } from 'react'
import { useAuth } from '../context/useAuth'
import api from '../api/client'

function renderMarkdown(text) {
  const lines = text.split('\n')
  const elements = []
  let key = 0

  function parseInline(str) {
    const parts = []
    const re = /(\*\*(.+?)\*\*|\*(.+?)\*|`(.+?)`)/g
    let last = 0, m
    while ((m = re.exec(str)) !== null) {
      if (m.index > last) parts.push(str.slice(last, m.index))
      if (m[2]) parts.push(<strong key={key++}>{m[2]}</strong>)
      else if (m[3]) parts.push(<em key={key++}>{m[3]}</em>)
      else if (m[4]) parts.push(<code key={key++} className="cw-code">{m[4]}</code>)
      last = m.index + m[0].length
    }
    if (last < str.length) parts.push(str.slice(last))
    return parts
  }

  let i = 0
  while (i < lines.length) {
    const line = lines[i]
    const bullet = line.match(/^(\s*[\*\-]\s+)(.*)/)
    if (bullet) {
      const items = []
      while (i < lines.length && lines[i].match(/^\s*[\*\-]\s+/)) {
        items.push(<li key={key++}>{parseInline(lines[i].replace(/^\s*[\*\-]\s+/, ''))}</li>)
        i++
      }
      elements.push(<ul key={key++} className="cw-list">{items}</ul>)
      continue
    }
    if (line.trim() === '') {
      elements.push(<br key={key++} />)
    } else {
      elements.push(<p key={key++} className="cw-p">{parseInline(line)}</p>)
    }
    i++
  }
  return elements
}

export default function ChatWidget() {
  const { user } = useAuth()
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)
  const pollRef = useRef(null)
  const textareaRef = useRef(null)

  useEffect(() => {
    if (open && user) loadHistory()
    return () => clearTimeout(pollRef.current)
  }, [open, user])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  async function loadHistory() {
    try {
      const data = await api.get('/api/v1/example-messages/')
      setMessages(data.flatMap(m => [
        { id: m.id, role: 'user', text: m.content, time: m.created_at },
        ...(m.bot_response ? [{ id: `${m.id}-bot`, role: 'bot', text: m.bot_response, time: m.created_at }] : []),
      ]))
    } catch { /* silent */ }
  }

  async function sendMessage() {
    if (!input.trim() || loading) return
    const text = input.trim()
    setInput('')
    setLoading(true)
    if (textareaRef.current) textareaRef.current.style.height = 'auto'

    const now = new Date().toISOString()
    const tempId = `tmp-${Date.now()}`
    setMessages(prev => [
      ...prev,
      { id: tempId, role: 'user', text, time: now },
      { id: `${tempId}-bot`, role: 'bot', text: null, time: now },
    ])

    try {
      const msg = await api.post('/api/v1/example-messages/', { content: text })
      setMessages(prev => prev.map(m =>
        m.id === tempId ? { ...m, id: msg.id } :
        m.id === `${tempId}-bot` ? { ...m, id: `${msg.id}-bot` } : m
      ))
      pollForReply(msg.id)
    } catch {
      setMessages(prev => prev.map(m =>
        m.id === `${tempId}-bot` ? { ...m, text: 'Error sending message.' } : m
      ))
      setLoading(false)
    }
  }

  function pollForReply(messageId, attempts = 0) {
    if (attempts > 30) {
      setMessages(prev => prev.map(m =>
        m.id === `${messageId}-bot` ? { ...m, text: 'No response received.' } : m
      ))
      setLoading(false)
      return
    }
    pollRef.current = setTimeout(async () => {
      try {
        const data = await api.get('/api/v1/example-messages/')
        const found = data.find(m => m.id === messageId)
        if (found?.bot_response) {
          setMessages(prev => prev.map(m =>
            m.id === `${messageId}-bot` ? { ...m, text: found.bot_response } : m
          ))
          setLoading(false)
        } else {
          pollForReply(messageId, attempts + 1)
        }
      } catch {
        pollForReply(messageId, attempts + 1)
      }
    }, 2000)
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  function handleInput(e) {
    setInput(e.target.value)
    e.target.style.height = 'auto'
    e.target.style.height = Math.min(e.target.scrollHeight, 100) + 'px'
  }

  function formatTime(iso) {
    if (!iso) return ''
    return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  return (
    <div className="cw-root">
      {open && (
        <div className="cw-window">
          {/* Header */}
          <div className="cw-header">
            <div className="cw-header-left">
              <div className="cw-avatar-bot">🏅</div>
              <div>
                <div className="cw-header-name">Olympics AI</div>
                <div className="cw-header-status">
                  <span className="cw-dot" />
                  {loading ? 'Typing…' : 'Online'}
                </div>
              </div>
            </div>
            <button className="cw-close" onClick={() => setOpen(false)}>✕</button>
          </div>

          {/* Messages */}
          <div className="cw-messages">
            {!user ? (
              <div className="cw-gate">
                <div className="cw-gate-icon">🔒</div>
                <p>Please <a href="/login">log in</a> to chat with the AI assistant.</p>
              </div>
            ) : (
              <>
                {messages.length === 0 && (
                  <div className="cw-welcome">
                    <div className="cw-welcome-icon">🏅</div>
                    <p>Hi! I'm your Olympics 2028 AI assistant.</p>
                    <p>Ask me about events, athletes, schedules or anything Olympics!</p>
                  </div>
                )}
                {messages.map(m => (
                  <div key={m.id} className={`cw-row cw-row--${m.role}`}>
                    {m.role === 'bot' && <div className="cw-avatar-sm">🏅</div>}
                    <div className={`cw-bubble cw-bubble--${m.role}`}>
                      {m.text === null ? (
                        <span className="cw-typing">
                          <span /><span /><span />
                        </span>
                      ) : (
                        <>
                          <div className="cw-text">{renderMarkdown(m.text)}</div>
                          <span className="cw-time">{formatTime(m.time)}</span>
                        </>
                      )}
                    </div>
                  </div>
                ))}
              </>
            )}
            <div ref={bottomRef} />
          </div>

          {/* Input */}
          {user && (
            <div className="cw-input-row">
              <textarea
                ref={textareaRef}
                className="cw-input"
                value={input}
                onChange={handleInput}
                onKeyDown={handleKeyDown}
                placeholder="Message Olympics AI…"
                rows={1}
                disabled={loading}
              />
              <button
                className="cw-send"
                onClick={sendMessage}
                disabled={loading || !input.trim()}
                title="Send"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="22" y1="2" x2="11" y2="13" />
                  <polygon points="22 2 15 22 11 13 2 9 22 2" />
                </svg>
              </button>
            </div>
          )}
        </div>
      )}

      {/* Bubble button */}
      <button className="cw-toggle" onClick={() => setOpen(o => !o)} title="Chat with AI">
        {open ? (
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
            <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        ) : (
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M20 2H4a2 2 0 00-2 2v18l4-4h14a2 2 0 002-2V4a2 2 0 00-2-2z"/>
          </svg>
        )}
        {!open && loading && <span className="cw-badge" />}
      </button>
    </div>
  )
}
