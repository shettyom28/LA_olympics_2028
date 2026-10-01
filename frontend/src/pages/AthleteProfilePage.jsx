import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import client from '../api/client'


const dummyAthletes = [
  { id: 1, full_name: 'Noah Lyles', country_name: 'United States', sport_name: 'Athletics', bio: 'World 100m champion and multiple world record holder.' },
  { id: 2, full_name: 'Mondo Duplantis', country_name: 'Sweden', sport_name: 'Athletics', bio: 'World record holder in the pole vault.' },
  { id: 3, full_name: 'Leon Marchand', country_name: 'France', sport_name: 'Swimming', bio: 'Four-time Olympic champion in Paris 2024.' },
  { id: 4, full_name: 'Sydney McLaughlin-Levrone', country_name: 'United States', sport_name: 'Athletics', bio: 'World record holder in the 400m hurdles.' },
  { id: 5, full_name: 'Carlos Yulo', country_name: 'Philippines', sport_name: 'Gymnastics', bio: 'Double Olympic champion in gymnastics at Paris 2024.' },
]
 
// fetch function
 
async function fetchAthlete(id) {
  try {
    const athletes = await client.get('/api/v1/athletes/')
    for (let i = 0; i < athletes.length; i++) {
      if (athletes[i].id === Number(id)) {
        return athletes[i]
      }
    }
    return null
  } catch (err) {
    console.warn('Athletes API not available, using dummy data')
    for (let i = 0; i < dummyAthletes.length; i++) {
      if (dummyAthletes[i].id === Number(id)) {
        return dummyAthletes[i]
      }
    }
    return dummyAthletes[0]
  }
}
 
 
export default function AthleteProfilePage() {
  const { id } = useParams()
 
  const { data: athlete, isLoading } = useQuery({
    queryKey: ['athlete', id],
    queryFn: function () {
      return fetchAthlete(id)
    },
  })
 
  // loading state
  if (isLoading || !athlete) {
    return <p className="page-status">Loading athlete…</p>
  }
 
  const displayName = athlete.full_name || athlete.username
 
  return (
    <div className="page-container">
 
      <Link to="/schedule" className="back-link">Back</Link>
 
      <h1 className="page-title">{displayName}</h1>
      <p className="page-subtitle">{athlete.sport_name} — {athlete.country_name}</p>
 
      <p style={{ color: '#615f5f', fontSize: '14px', marginBottom: '32px' }}>{athlete.bio}</p>
 
      {/* results will be added here once event results are linked to athlete profiles in the API */}
 
    </div>
  )
}
 