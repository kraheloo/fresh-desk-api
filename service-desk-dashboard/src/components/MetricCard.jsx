import './MetricCard.css'

function MetricCard({ title, value, icon, color, subtitle, highlight }) {
  return (
    <div className={`metric-card ${highlight ? 'highlight' : ''}`} style={{ '--card-color': color }}>
      <div className="metric-icon">{icon}</div>
      <div className="metric-content">
        <h3 className="metric-title">{title}</h3>
        <p className="metric-value">{value}</p>
        {subtitle && <p className="metric-subtitle">{subtitle}</p>}
      </div>
    </div>
  )
}

export default MetricCard
