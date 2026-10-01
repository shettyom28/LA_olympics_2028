import { useQuery } from '@tanstack/react-query'
import api from '../api/client'

function LeaderboardTable() {
  const { data: rows = [], isLoading } = useQuery({
    queryKey: ['leaderboard'],
    queryFn: () => api.get('/api/v1/leaderboard/'),
  })

  if (isLoading) return <p className="lb-sub">Loading medal table…</p>
  if (rows.length === 0) return <p className="lb-sub">No medal data yet.</p>

  return (
    <div className="table-container">
      <div className="table-header">
        <span>RANK</span>
        <span>COUNTRY</span>
        <span>GOLD</span>
        <span>SILVER</span>
        <span>BRONZE</span>
        <span>TOTAL</span>
      </div>
      {rows.map((row, i) => (
        <div key={row.country_code} className={`table-row ${i === 0 ? 'top' : ''}`}>
          <span>{i + 1}</span>
          <span>{row.country_code} <small>{row.country_name}</small></span>
          <span className="gold">{row.gold}</span>
          <span>{row.silver}</span>
          <span className="bronze">{row.bronze}</span>
          <span>{row.total}</span>
        </div>
      ))}
    </div>
  )
}

export default LeaderboardTable
