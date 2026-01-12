function UserSelector({ users, selectedUser, onUserChange }) {
  return (
    <div className="user-selector">
      <label htmlFor="user-select">Select User:</label>
      <div className="user-selector-container">
        <select
          id="user-select"
          value={selectedUser}
          onChange={(e) => {
            onUserChange(e.target.value)
          }}
        >
          <option value="">-- Select a user --</option>
          {users.map((user) => (
            <option key={user.username} value={user.username}>
              {user.username}
            </option>
          ))}
        </select>
        {selectedUser && (
          <span className="selected-user-indicator">✓</span>
        )}
      </div>
    </div>
  )
}

export default UserSelector
