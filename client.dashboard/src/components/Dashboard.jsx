import MetricCard from './MetricCard'
import ResolutionChart from './ResolutionChart'
import StatusBreakdown from './StatusBreakdown'
import './Dashboard.css'

function Dashboard({ data, selectedUser, days }) {
  const {
    totalOpen,
    totalPending,
    totalResolved,
    totalClosed,
    totalOpenAndPending,
    resolutionRate,
    accessibleDepartments
  } = data

  const totalTickets = totalOpen + totalPending + totalResolved + totalClosed
  const openRate = totalTickets > 0 ? ((totalOpenAndPending / totalTickets) * 100).toFixed(1) : 0

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h2>Incident Metrics</h2>
        <p className="metrics-info">
          Showing data for <strong>{selectedUser}</strong> over the last <strong>{days} days</strong>
        </p>
        <p className="department-count">
          Accessible Departments: <strong>{accessibleDepartments?.length || 0}</strong>
        </p>
      </div>

      <div className="metrics-grid">
        <MetricCard
          title="Total Tickets"
          value={totalTickets}
          icon="📊"
          color="#646cff"
        />
        <MetricCard
          title="Open"
          value={totalOpen}
          icon="🔵"
          color="#4287f5"
          subtitle="New incidents"
        />
        <MetricCard
          title="Pending"
          value={totalPending}
          icon="🟡"
          color="#ffa500"
          subtitle="Awaiting action"
        />
        <MetricCard
          title="Resolved"
          value={totalResolved}
          icon="✅"
          color="#28a745"
          subtitle="Fixed incidents"
        />
        <MetricCard
          title="Closed"
          value={totalClosed}
          icon="🔒"
          color="#6c757d"
          subtitle="Completed"
        />
        <MetricCard
          title="Open + Pending"
          value={totalOpenAndPending}
          icon="⚠️"
          color="#dc3545"
          subtitle="Requires attention"
          highlight={totalOpenAndPending > 0}
        />
      </div>

      <div className="charts-section">
        <div className="chart-container">
          <h3>Resolution Rate</h3>
          <ResolutionChart
            resolutionRate={resolutionRate}
            openRate={openRate}
          />
          <div className="rate-labels">
            <div className="rate-label">
              <span className="rate-color resolved"></span>
              <span>Resolved: {resolutionRate}%</span>
            </div>
            <div className="rate-label">
              <span className="rate-color open"></span>
              <span>Open/Pending: {openRate}%</span>
            </div>
          </div>
        </div>

        <div className="chart-container">
          <h3>Status Breakdown</h3>
          <StatusBreakdown
            open={totalOpen}
            pending={totalPending}
            resolved={totalResolved}
            closed={totalClosed}
          />
        </div>
      </div>

      {accessibleDepartments && accessibleDepartments.length > 0 && (
        <div className="departments-section">
          <h3>Accessible Departments ({accessibleDepartments.length})</h3>
          <div className="departments-list">
            {accessibleDepartments.map((dept) => (
              <div key={dept.departmentId} className="department-tag">
                {dept.departmentName}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default Dashboard
