import { useState } from 'react'
import './UserSelector.css'

function UserSelector({ users, selectedUser, onUserChange }) {
  const [searchTerm, setSearchTerm] = useState('')

  const filteredUsers = users.filter(user =>
    user.username.toLowerCase().includes(searchTerm.toLowerCase())
  )

  return (
    <div className="user-selector">
      <label htmlFor="user-select">Select User:</label>
      <div className="select-wrapper">
        <input
          type="text"
          placeholder="Search users..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="user-search"
        />
        <select
          id="user-select"
          value={selectedUser}
          onChange={(e) => {
            onUserChange(e.target.value)
            setSearchTerm('')
          }}
          size="1"
        >
          <option value="">-- Select a user --</option>
          {filteredUsers.map((user) => (
            <option key={user.username} value={user.username}>
              {user.username} ({user.accessLevel})
            </option>
          ))}
        </select>
      </div>
      {selectedUser && (
        <p className="selected-user-info">
          Viewing data for: <strong>{selectedUser}</strong>
        </p>
      )}
    </div>
  )
}

export default UserSelector
