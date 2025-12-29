import { useState, useEffect } from 'react'
import './App.css'
import UserSelector from './components/UserSelector'
import Dashboard from './components/Dashboard'
import { serviceDeskApi } from './services/api'

function App() {
  const [users, setUsers] = useState([])
  const [selectedUser, setSelectedUser] = useState('')
  const [metricsData, setMetricsData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [days, setDays] = useState(30)

  // Load users on mount
  useEffect(() => {
    const loadUsers = async () => {
      try {
        const data = await serviceDeskApi.getUsers()
        setUsers(data)
      } catch (err) {
        setError('Failed to load users: ' + err.message)
      }
    }
    loadUsers()
  }, [])

  // Load metrics data when user or days changes
  useEffect(() => {
    if (!selectedUser) {
      setMetricsData(null)
      return
    }

    const loadMetricsData = async () => {
      setLoading(true)
      setError(null)
      try {
        const data = await serviceDeskApi.getMetrics(selectedUser, days)
        setMetricsData(data)
      } catch (err) {
        setError('Failed to load metrics data: ' + err.message)
        setMetricsData(null)
      } finally {
        setLoading(false)
      }
    }

    loadMetricsData()
  }, [selectedUser, days])

  return (
    <div className="app">
      <header className="app-header">
        <h1>Service Desk Dashboard</h1>
        <p className="subtitle">Monitor and analyze service desk incidents</p>
      </header>

      <div className="controls">
        <UserSelector
          users={users}
          selectedUser={selectedUser}
          onUserChange={setSelectedUser}
        />

        <div className="days-selector">
          <label htmlFor="days">Time Range:</label>
          <select
            id="days"
            value={days}
            onChange={(e) => setDays(Number(e.target.value))}
          >
            <option value="7">Last 7 days</option>
            <option value="14">Last 14 days</option>
            <option value="30">Last 30 days</option>
            <option value="60">Last 60 days</option>
            <option value="90">Last 90 days</option>
          </select>
        </div>
      </div>

      {error && (
        <div className="error-message">
          <p>{error}</p>
        </div>
      )}

      {loading && (
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading metrics data...</p>
        </div>
      )}

      {!loading && !error && metricsData && (
        <Dashboard data={metricsData} selectedUser={selectedUser} days={days} />
      )}

      {!loading && !error && !metricsData && selectedUser && (
        <div className="no-data">
          <p>No data available for the selected user and time range.</p>
        </div>
      )}

      {!selectedUser && (
        <div className="welcome">
          <h2>Welcome to the Service Desk Dashboard</h2>
          <p>Select a user from the dropdown above to view their incident and service request metrics.</p>
        </div>
      )}
    </div>
  )
}

export default App
