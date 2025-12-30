import './TicketTable.css'

function TicketTable({ tickets, type }) {
  if (!tickets || tickets.length === 0) {
    return (
      <div className="ticket-table-empty">
        <p>No open tickets found 🎉</p>
      </div>
    )
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A'
    const date = new Date(dateString)
    const now = new Date()
    const diffTime = Math.abs(now - date)
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))
    
    if (diffDays === 0) return 'Today'
    if (diffDays === 1) return '1 day ago'
    if (diffDays < 7) return `${diffDays} days ago`
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`
    if (diffDays < 365) return `${Math.floor(diffDays / 30)} months ago`
    return `${Math.floor(diffDays / 365)} years ago`
  }

  return (
    <div className="ticket-table-container">
      <h3>Oldest Open {type}</h3>
      <table className="ticket-table">
        <thead>
          <tr>
            <th>Ticket ID</th>
            <th>Subject</th>
            <th>Status</th>
            <th>Created</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {tickets.map((ticket) => (
            <tr key={ticket.id}>
              <td className="ticket-id">#{ticket.id}</td>
              <td className="ticket-subject" title={ticket.subject}>
                {ticket.subject || 'No subject'}
              </td>
              <td>
                <span className={`status-badge status-${ticket.statusName.toLowerCase()}`}>
                  {ticket.statusName}
                </span>
              </td>
              <td className="ticket-date">{formatDate(ticket.createdAt)}</td>
              <td>
                <a 
                  href={ticket.url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="ticket-link"
                >
                  View Ticket →
                </a>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default TicketTable
