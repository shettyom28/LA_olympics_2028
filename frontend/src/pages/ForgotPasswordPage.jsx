import { useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../api/client'

function ForgotPasswordPage() {
  const [email, setEmail] = useState('')
  const [error, setError] = useState('')
  const [submitted, setSubmitted] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setSubmitting(true)

    try {
      await api.post('/api/v1/auth/password/reset/', { email })
      setSubmitted(true)
    } catch (err) {
      setError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  if (submitted) {
    return (
      <div>
        <h2>Check Your Email</h2>
        <p>If an account exists with that email address, we have sent password reset instructions.</p>
        <p><Link to="/login">Back to Login</Link></p>
      </div>
    )
  }

  return (
    <div>
      <h2>Forgot Password</h2>
      <p>Enter your email address and we will send you instructions to reset your password.</p>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="email">Email</label><br />
          <input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        </div>
        <button type="submit" disabled={submitting}>
          {submitting ? 'Sending...' : 'Send Reset Link'}
        </button>
      </form>
      <p><Link to="/login">Back to Login</Link></p>
    </div>
  )
}

export default ForgotPasswordPage
