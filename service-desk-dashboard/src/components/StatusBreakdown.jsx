import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts'

function StatusBreakdown({ open, pending, resolved, closed }) {
  const data = [
    { name: 'Open', value: open, color: '#4287f5' },
    { name: 'Pending', value: pending, color: '#ffa500' },
    { name: 'Resolved', value: resolved, color: '#28a745' },
    { name: 'Closed', value: closed, color: '#6c757d' },
  ]

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#444" />
        <XAxis dataKey="name" stroke="#888" />
        <YAxis stroke="#888" />
        <Tooltip
          contentStyle={{
            backgroundColor: '#1a1a1a',
            border: '1px solid #646cff',
            borderRadius: '8px'
          }}
        />
        <Legend />
        <Bar dataKey="value" name="Count" radius={[8, 8, 0, 0]}>
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={entry.color} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}

export default StatusBreakdown
