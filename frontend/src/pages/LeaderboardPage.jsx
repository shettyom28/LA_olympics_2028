import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import client from '../api/client'

// static data if backend fails or isnt set up yet

const dummyMedals = [
  { country_name: 'United States', country_code: 'USA', gold: 2, silver: 0, bronze: 0, total: 2 },
  { country_name: 'Sweden', country_code: 'SWE', gold: 1, silver: 0, bronze: 0, total: 1 },
  { country_name: 'France', country_code: 'FRA', gold: 1, silver: 0, bronze: 0, total: 1 },
  { country_name: 'Philippines', country_code: 'PHI', gold: 1, silver: 0, bronze: 0, total: 1 },
  { country_name: 'Australia', country_code: 'AUS', gold: 0, silver: 0, bronze: 0, total: 0 },
  { country_name: 'Great Britain', country_code: 'GBR', gold: 0, silver: 0, bronze: 0, total: 0 },
  { country_name: 'China', country_code: 'CHN', gold: 0, silver: 0, bronze: 0, total: 0 },
  { country_name: 'Kenya', country_code: 'KEN', gold: 0, silver: 0, bronze: 0, total: 0 },
  { country_name: 'Ireland', country_code: 'IRL', gold: 0, silver: 0, bronze: 0, total: 0 },
  { country_name: 'Jamaica', country_code: 'JAM', gold: 0, silver: 0, bronze: 0, total: 0 },
]

// fetch function

async function fetchLeaderboard() {
  try {
    return await client.get('/api/v1/leaderboard/')
  } catch (err) {
    console.warn('Leaderboard API not available, using dummy data')
    return dummyMedals
  }
}

// helpers

function flagUrl(code) {
  if (!code) return ''
  return 'https://flagcdn.com/24x18/' + code.toLowerCase().slice(0, 2) + '.png'
}


export default function LeaderboardPage() {
  const [sortBy, setSortBy] = useState('gold')
  const [sortDir, setSortDir] = useState('desc')

  const { data: medals = [], isLoading } = useQuery({
    queryKey: ['leaderboard'],
    queryFn: fetchLeaderboard,
  })

  // loading state
  if (isLoading) {
    return <p className="page-status">Loading leaderboard…</p>
  }

  // sort
  function handleSort(column) {
    if (sortBy === column) {
      if (sortDir === 'desc') {
        setSortDir('asc')
      } else {
        setSortDir('desc')
      }
    } else {
      setSortBy(column)
      setSortDir('desc')
    }
  }

  // do the actual sorting
  const sorted = medals.slice().sort(function (a, b) {
    if (sortDir === 'desc') {
      return b[sortBy] - a[sortBy]
    } else {
      return a[sortBy] - b[sortBy]
    }
  })

  // show arrow next to active sort column
  function arrow(column) {
    if (sortBy !== column) return ''
    if (sortDir === 'desc') return ' ▼'
    return ' ▲'
  }

  return (
    <div className="page-container">

      <h1 className="page-title">Medal Table</h1>
      <p className="page-subtitle">Click a column to sort</p>

      <table className="data-table">
        <thead>
          <tr>
            <th style={{ width: 40 }}>#</th>
            <th>Country</th>
            <th onClick={function () { handleSort('gold') }} style={{ width: 70, cursor: 'pointer' }}>
              Gold{arrow('gold')}
            </th>
            <th onClick={function () { handleSort('silver') }} style={{ width: 70, cursor: 'pointer' }}>
              Silver{arrow('silver')}
            </th>
            <th onClick={function () { handleSort('bronze') }} style={{ width: 70, cursor: 'pointer' }}>
              Bronze{arrow('bronze')}
            </th>
            <th onClick={function () { handleSort('total') }} style={{ width: 70, cursor: 'pointer' }}>
              Total{arrow('total')}
            </th>
          </tr>
        </thead>
        <tbody>
          {sorted.map(function (m, index) {
            return (
              <tr key={m.country_code}>
                <td className="td-mono td-dim">{index + 1}</td>
                <td className="td-bold">
                  <img src={flagUrl(m.country_code)} alt="" style={{ marginRight: 8, verticalAlign: 'middle' }} />
                  {m.country_name}
                </td>
                <td className="td-bold">{m.gold}</td>
                <td>{m.silver}</td>
                <td>{m.bronze}</td>
                <td className="td-bold">{m.total}</td>
              </tr>
            )
          })}
        </tbody>
      </table>

    </div>
  )
}