import { useState } from 'react'
import api from '../api/client'
import { useAuth } from '../context/useAuth'

function AthleteCard({ athlete, isFavourited = false, favouriteId = null, onFavouriteChange }) {
  const { user } = useAuth()
  const [fav, setFav] = useState(isFavourited)
  const [favId, setFavId] = useState(favouriteId)
  const [loading, setLoading] = useState(false)

  async function toggleFav() {
    if (!user || loading) return
    setLoading(true)
    try {
      if (fav && favId) {
        await api.delete(`/api/v1/favourites/${favId}/`)
        setFav(false)
        setFavId(null)
        onFavouriteChange?.({ removed: true, athleteId: athlete.id })
      } else {
        const data = await api.post('/api/v1/favourites/', { athlete: athlete.id })
        setFav(true)
        setFavId(data.id)
        onFavouriteChange?.({ removed: false, athleteId: athlete.id, favouriteId: data.id })
      }
    } catch {
      // silently ignore (e.g. not logged in)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="athlete-card">
      <div className="athlete-card-header">
        <span className="athlete-card-name">{athlete.full_name || athlete.username}</span>
        {user && (
          <span
            className="heart"
            onClick={toggleFav}
            title={fav ? 'Remove from favourites' : 'Add to favourites'}
            style={{ opacity: loading ? 0.5 : 1, cursor: 'pointer' }}
          >
            {fav ? '❤️' : '♡'}
          </span>
        )}
      </div>
      <p className="athlete-card-sport">{athlete.sport_name}</p>
      <p className="athlete-card-country">{athlete.country_name}</p>
      {athlete.bio && <p className="athlete-card-bio">{athlete.bio}</p>}
    </div>
  )
}

export default AthleteCard
