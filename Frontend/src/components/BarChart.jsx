export default function BarChart({ data, limit = 10 }) {
  const entries = Object.entries(data || {}).sort((a, b) => b[1] - a[1])
  const shown = entries.slice(0, limit)
  const max = Math.max(...shown.map(([, v]) => v), 1)
  const total = entries.reduce((sum, [, v]) => sum + v, 0)

  return (
    <div className="bars">
      {shown.map(([label, value]) => (
        <div key={label} className="bars__row" title={`${label}: ${value}`}>
          <div className="bars__label">{label}</div>
          <div className="bars__track">
            <div className="bars__fill" style={{ width: `${(value / max) * 100}%` }} />
          </div>
          <div className="bars__value">
            {value}
            <span className="bars__percent">{Math.round((value / total) * 100)}%</span>
          </div>
        </div>
      ))}
      {entries.length > limit && <div className="bars__more">и ещё {entries.length - limit}</div>}
    </div>
  )
}
