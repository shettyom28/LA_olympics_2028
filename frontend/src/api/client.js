// API client — Axios instance with JWT bearer tokens
// For production packages, use 

import axios from 'axios'
import { traceparent } from './traceparent'


// JWT sessionStorage functions

const JWT_TOKEN_KEY = 'auth_tokens'

function getJwtTokens() {
  return JSON.parse(sessionStorage.getItem(JWT_TOKEN_KEY))
}

export function saveJwtTokens(access, refresh) {
  sessionStorage.setItem(JWT_TOKEN_KEY, JSON.stringify({ access, refresh }))
}

export function clearJwtTokens() {
  sessionStorage.removeItem(JWT_TOKEN_KEY)
}

export function hasJwtTokens() {
  return sessionStorage.getItem(JWT_TOKEN_KEY) !== null
}


// Axios API client instance with JWT bearer tokens

const api = axios.create()

api.interceptors.request.use((config) => {
  const tokens = getJwtTokens()
  if (tokens?.access) {
    config.headers.Authorization = `Bearer ${tokens.access}`
  }
  config.headers.traceparent = traceparent()
  return config
})

api.interceptors.response.use(
  (response) => {
    // Auto-unwrap paginated responses: { count, results, next, previous } → results array
    const d = response.data
    if (d && typeof d === 'object' && 'results' in d && 'count' in d && Array.isArray(d.results)) {
      return d.results
    }
    return d
  },
  async (error) => {
    const original = error.config

    // On 401, attempt one JWT token refresh then retry
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true
      const tokens = getJwtTokens()
      if (tokens?.refresh) {
        try {
          const { data } = await axios.post('/api/v1/auth/token/refresh/', {
            refresh: tokens.refresh,
          })
          saveJwtTokens(data.access, data.refresh || tokens.refresh)
          return api(original)
        } catch {
          clearJwtTokens()
        }
      }
    }

    // Build a human-readable message from DRF error responses
    const data  = error.response?.data
    const status = error.response?.status
    let message

    if (data) {
      if (typeof data === 'string') {
        message = data
      } else if (data.detail) {
        message = data.detail
      } else if (data.non_field_errors) {
        message = data.non_field_errors.join(' ')
      } else if (typeof data === 'object') {
        // Field-level errors: { username: ["Already taken."], password: ["Too short."] }
        const lines = Object.entries(data)
          .map(([field, errs]) => {
            const label = field.charAt(0).toUpperCase() + field.slice(1).replace(/_/g, ' ')
            const msg = Array.isArray(errs) ? errs.join(' ') : String(errs)
            return `${label}: ${msg}`
          })
        message = lines.join('\n')
      }
    }

    if (!message) {
      const FALLBACKS = {
        400: 'The request could not be processed. Please check your input.',
        401: 'Invalid credentials. Please try again.',
        403: 'You do not have permission to perform this action.',
        404: 'The requested resource was not found.',
        500: 'A server error occurred. Please try again later.',
      }
      message = FALLBACKS[status] || error.message
    }

    const err = new Error(message)
    err.status = status
    err.data = data
    throw err
  }
)

export default api
