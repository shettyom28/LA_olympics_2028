import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import api from '../api/client'

function ResetPasswordPage() {
  const { uid, token } = useParams()
  const [newPassword1, setNewPassword1] = useState('')
  const [newPassword2, setNewPassword2] = useState('')
  const [error, setError] = useState('')
  const [submitted, setSubmitted] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')

    if (newPassword1 !== newPassword2) {
      setError('Passwords do not match.')
      return
    }

    setSubmitting(true)

    try {
      await api.post('/api/v1/auth/password/reset/confirm/', {
        uid,
        token,
        new_password1: newPassword1,
        new_password2: newPassword2,
      })
      setSubmitted(true)
    } catch (err) {
      if (err.data) {
        const msgs = []
        for (const [key, val] of Object.entries(err.data)) {
          const values = Array.isArray(val) ? val : [val]
          if (key === 'token' || key === 'uid') {
            msgs.push('This password reset link is invalid or has expired.')
          } else {
            msgs.push(...values)
          }
        }
        if (msgs.length) setError(msgs.join(' '))
      } else {
        setError(err.message)
      }
    } finally {
      setSubmitting(false)
    }
  }

  if (submitted) {
    return (
      <div>
        <h2>Password Reset Complete</h2>
        <p>Your password has been set. You can now log in with your new password.</p>
        <p><Link to="/login">Go to Login</Link></p>
      </div>
    )
  }

  return (
    <div>
      <h2>Set New Password</h2>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="newPassword1">New Password</label><br />
          <input id="newPassword1" type="password" value={newPassword1} onChange={(e) => setNewPassword1(e.target.value)} required />
        </div>
        <div>
          <label htmlFor="newPassword2">Confirm New Password</label><br />
          <input id="newPassword2" type="password" value={newPassword2} onChange={(e) => setNewPassword2(e.target.value)} required />
        </div>
        <button type="submit" disabled={submitting}>
          {submitting ? 'Resetting...' : 'Reset Password'}
        </button>
      </form>
    </div>
  )
}

export default ResetPasswordPage
