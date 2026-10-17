import { useEffect, useState } from 'react'
import { useSettings } from '../context/SettingsContext.jsx'
import BarChart from '../components/BarChart.jsx'
import { Empty, ErrorBox, Loader } from '../components/Status.jsx'

// Бэкенд формирует ключи вида «Распределение по <поле>»
const TITLES = {
  'Распределение по scope': 'По направлениям',
  'Распределение по stage': 'По стадиям',
  'Распределение по странам': 'Участников по странам',
  'Распределение по компаниям': 'По компаниям-участникам',
  'Распределение по links': 'По источникам',
}

export default function StatisticsPage() {
  const { api } = useSettings()
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)
    api
      .getStatistics()
      .then((data) => !cancelled && setStats(data && typeof data === 'object' ? data : {}))
      .catch((e) => !cancelled && setError(e))
      .finally(() => !cancelled && setLoading(false))
    return () => {
      cancelled = true
    }
  }, [api])

  const sections = stats ? Object.entries(stats) : []
  const totalByStage = stats?.['Распределение по stage']
  const projectCount = totalByStage ? Object.values(totalByStage).reduce((a, b) => a + b, 0) : null

  return (
    <section>
      <div className="page-head">
        <h1>Статистика</h1>
        <p className="muted">Распределение проектов в базе данных.</p>
      </div>

      <ErrorBox error={error} />
      {loading && <Loader />}

      {!loading && stats && sections.length === 0 && <Empty>В базе пока нет данных.</Empty>}

      {!loading && sections.length > 0 && (
        <>
          <div className="kpis">
            {projectCount !== null && <Kpi label="Проектов" value={projectCount} />}
            {sections.map(([key, values]) => (
              <Kpi key={key} label={TITLES[key] || key} value={Object.keys(values).length} hint="уникальных" />
            ))}
          </div>
          <div className="grid grid--stats">
            {sections.map(([key, values]) => (
              <div key={key} className="card">
                <h3 className="card__title">{TITLES[key] || key}</h3>
                <BarChart data={values} />
              </div>
            ))}
          </div>
        </>
      )}
    </section>
  )
}

function Kpi({ label, value, hint }) {
  return (
    <div className="card kpi">
      <div className="kpi__value">{value}</div>
      <div className="kpi__label">
        {label}
        {hint && <span className="muted"> · {hint}</span>}
      </div>
    </div>
  )
}
