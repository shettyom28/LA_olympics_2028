import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../context/useAuth'

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/

const RULES = [
  { id: 'len',     label: 'At least 8 characters',        test: p => p.length >= 8 },
  { id: 'upper',   label: 'One uppercase letter (A–Z)',    test: p => /[A-Z]/.test(p) },
  { id: 'lower',   label: 'One lowercase letter (a–z)',    test: p => /[a-z]/.test(p) },
  { id: 'digit',   label: 'One number (0–9)',              test: p => /\d/.test(p) },
  { id: 'special', label: 'One special character (!@#…)',  test: p => /[^A-Za-z0-9]/.test(p) },
]

function strength(password) {
  return RULES.filter(r => r.test(password)).length
}

function RegisterPage() {
  const { register } = useAuth()
  const navigate = useNavigate()

  const [username, setUsername]               = useState('')
  const [email, setEmail]                     = useState('')
  const [password, setPassword]               = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showPw, setShowPw]                   = useState(false)
  const [touchedPw, setTouchedPw]             = useState(false)
  const [touchedEmail, setTouchedEmail]       = useState(false)
  const [error, setError]                     = useState('')
  const [submitting, setSubmitting]           = useState(false)

  const score        = strength(password)
  const allRulesMet  = score === RULES.length
  const emailValid   = EMAIL_RE.test(email)
  const pwMatch      = password === confirmPassword
  const canSubmit    = username && emailValid && allRulesMet && pwMatch && !submitting

  const strengthLabel = ['', 'Very weak', 'Weak', 'Fair', 'Strong', 'Very strong'][score]
  const strengthColor = ['', '#ef4444', '#f97316', '#eab308', '#22c55e', '#16a34a'][score]

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    if (!emailValid)   return setError('Please enter a valid email address.')
    if (!allRulesMet)  return setError('Your password does not meet all requirements.')
    if (!pwMatch)      return setError('Passwords do not match.')
    setSubmitting(true)
    try {
      await register(username, email, password)
      navigate('/')
    } catch (err) {
      setError(err.message || 'Registration failed. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <p className="auth-logo">Olympics <span>2028</span></p>
        <h2 className="auth-title">Create your account</h2>
        <p className="auth-subtitle">Join the Olympic Games community</p>

        {error && (
          <div className="auth-error">
            {error.split('\n').map((line, i) => <p key={i} style={{margin:'2px 0'}}>{line}</p>)}
          </div>
        )}

        <form onSubmit={handleSubmit} noValidate>
          {/* Username */}
          <div className="form-group">
            <label className="form-label" htmlFor="username">Username</label>
            <input
              id="username" type="text"
              className="form-input"
              value={username}
              onChange={e => setUsername(e.target.value)}
              placeholder="Choose a username"
              required
            />
          </div>

          {/* Email */}
          <div className="form-group">
            <label className="form-label" htmlFor="email">Email</label>
            <input
              id="email" type="email"
              className={`form-input ${touchedEmail && email ? (emailValid ? 'input-valid' : 'input-invalid') : ''}`}
              value={email}
              onChange={e => setEmail(e.target.value)}
              onBlur={() => setTouchedEmail(true)}
              placeholder="your@email.com"
              required
            />
            {touchedEmail && email && !emailValid && (
              <p className="field-hint field-hint--error">Please enter a valid email address.</p>
            )}
          </div>

          {/* Password */}
          <div className="form-group">
            <label className="form-label" htmlFor="password">Password</label>
            <div className="input-eye-wrap">
              <input
                id="password"
                type={showPw ? 'text' : 'password'}
                className="form-input"
                value={password}
                onChange={e => { setPassword(e.target.value); setTouchedPw(true) }}
                placeholder="Create a password"
                required
              />
              <button type="button" className="input-eye" onClick={() => setShowPw(v => !v)}>
                {showPw ? '🙈' : '👁'}
              </button>
            </div>

            {/* Strength bar */}
            {touchedPw && password && (
              <div className="pw-strength-wrap">
                <div className="pw-strength-bar">
                  {[1,2,3,4,5].map(i => (
                    <div
                      key={i}
                      className="pw-strength-seg"
                      style={{ background: i <= score ? strengthColor : '#e2e8f0' }}
                    />
                  ))}
                </div>
                <span className="pw-strength-label" style={{ color: strengthColor }}>
                  {strengthLabel}
                </span>
              </div>
            )}

            {/* Rules checklist */}
            {touchedPw && (
              <ul className="pw-rules">
                {RULES.map(r => (
                  <li key={r.id} className={`pw-rule ${r.test(password) ? 'pw-rule--ok' : 'pw-rule--no'}`}>
                    <span className="pw-rule-icon">{r.test(password) ? '✓' : '○'}</span>
                    {r.label}
                  </li>
                ))}
              </ul>
            )}
          </div>

          {/* Confirm password */}
          <div className="form-group">
            <label className="form-label" htmlFor="confirmPassword">Confirm Password</label>
            <input
              id="confirmPassword"
              type={showPw ? 'text' : 'password'}
              className={`form-input ${confirmPassword ? (pwMatch ? 'input-valid' : 'input-invalid') : ''}`}
              value={confirmPassword}
              onChange={e => setConfirmPassword(e.target.value)}
              placeholder="Repeat your password"
              required
            />
            {confirmPassword && !pwMatch && (
              <p className="field-hint field-hint--error">Passwords do not match.</p>
            )}
          </div>

          <button type="submit" className="form-btn" disabled={!canSubmit}>
            {submitting ? 'Creating account…' : 'Create Account'}
          </button>
        </form>

        <div className="auth-footer" style={{ marginTop: '20px' }}>
          Already have an account? <Link to="/login">Sign in</Link>
        </div>
      </div>
    </div>
  )
}

export default RegisterPage
