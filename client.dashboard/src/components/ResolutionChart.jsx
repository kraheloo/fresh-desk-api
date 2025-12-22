import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts'

function ResolutionChart({ resolutionRate, openRate }) {
  const data = [
    { name: 'Resolved', value: parseFloat(resolutionRate) || 0, color: '#28a745' },
    { name: 'Open/Pending', value: parseFloat(openRate) || 0, color: '#dc3545' },
  ]

  const COLORS = data.map(d => d.color)

  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          labelLine={false}
          label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(1)}%`}
          outerRadius={100}
          fill="#8884d8"
          dataKey="value"
        >
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index]} />
          ))}
        </Pie>
        <Tooltip formatter={(value) => `${value.toFixed(1)}%`} />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  )
}

export default ResolutionChart
