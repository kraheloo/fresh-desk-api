import MetricCard from './MetricCard'
import ResolutionChart from './ResolutionChart'
import StatusBreakdown from './StatusBreakdown'
import TicketTable from './TicketTable'
import './Dashboard.css'

function Dashboard({ data, selectedUser, days }) {
  const { incidentCounts, serviceCounts } = data

  // Helper function to render metrics section
  const renderMetricsSection = (metricsData, title, sectionKey) => {
    const {
      totalOpen,
      totalPending,
      totalResolved,
      totalClosed,
      totalOpenAndPending,
      resolutionRate,
      accessibleDepartments,
      oldestOpenTickets
    } = metricsData

    const totalTickets = totalOpen + totalPending + totalResolved + totalClosed
    const openRate = totalTickets > 0 ? ((totalOpenAndPending / totalTickets) * 100).toFixed(1) : 0

    return (
      <div className="dashboard" key={sectionKey}>
        <div className="dashboard-header">
          <h2>{title}</h2>
          <p className="metrics-info">
            Showing data for <strong>{selectedUser}</strong> over the last <strong>{days} days</strong>
          </p>
          {sectionKey === 'incidents' && (
            <p className="department-count">
              Accessible Departments: <strong>{accessibleDepartments?.length || 0}</strong>
            </p>
          )}
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
            subtitle={`New ${sectionKey}`}
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
            subtitle="Fixed"
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

        <TicketTable 
          tickets={oldestOpenTickets} 
          type={sectionKey === 'incidents' ? 'Incidents' : 'Service Requests'} 
        />

        {sectionKey === 'service-requests' && accessibleDepartments && accessibleDepartments.length > 0 && (
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

  return (
    <div className="dashboard-container">
      {renderMetricsSection(incidentCounts, 'Incident Metrics', 'incidents')}
      <div className="section-divider"></div>
      {renderMetricsSection(serviceCounts, 'Service Request Metrics', 'service-requests')}
    </div>
  )
}

export default Dashboard
