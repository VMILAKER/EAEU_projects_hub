import { useEffect, useState } from 'react'
import { useSettings } from '../context/SettingsContext.jsx'
import ProjectCard from '../components/ProjectCard.jsx'
import { Empty, ErrorBox, Loader } from '../components/Status.jsx'

const EMPTY_FILTERS = { project_name: '', scope: '', stage: '', participants: '' }

const FIELDS = [
  { name: 'project_name', label: 'Название проекта'},
  { name: 'scope', label: 'Направление', placeholder: 'Цифровизация' },
  { name: 'stage', label: 'Стадия', placeholder: 'Соглашение' },
  { name: 'participants', label: 'Участники'},
]

export default function ProjectsPage() {
  const { api } = useSettings()
  const [filters, setFilters] = useState(EMPTY_FILTERS)
  const [projects, setProjects] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const load = async (f) => {
    setLoading(true)
    setError(null)
    try {
      const data = await api.getProjects(f)
      setProjects(Array.isArray(data) ? data : [])
    } catch (e) {
      setError(e)
      setProjects(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load(filters)
    // перезагружаем при смене ключа / режима
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [api])

  const onSubmit = (e) => {
    e.preventDefault()
    load(filters)
  }

  const reset = () => {
    setFilters(EMPTY_FILTERS)
    load(EMPTY_FILTERS)
  }

  return (
    <section>
      <div className="page-head">
        <h1>Проекты</h1>
        <p className="muted">Каталог совместных проектов государств ЕАЭС. Несколько значений в поле — через запятую.</p>
      </div>

      <form className="card filters" onSubmit={onSubmit}>
        {FIELDS.map((f) => (
          <label key={f.name} className="field">
            <span className="field__label">{f.label}</span>
            <input
              className="input"
              value={filters[f.name]}
              placeholder={f.placeholder}
              onChange={(e) => setFilters({ ...filters, [f.name]: e.target.value })}
            />
          </label>
        ))}
        <div className="filters__actions">
          <button type="button" className="btn btn--ghost" onClick={reset}>
            Сбросить
          </button>
          <button type="submit" className="btn btn--primary" disabled={loading}>
            Найти
          </button>
        </div>
      </form>

      <ErrorBox error={error} />
      {loading && <Loader />}

      {!loading && projects && (
        <>
          <div className="muted result-count">Найдено проектов: {projects.length}</div>
          {projects.length === 0 ? (
            <Empty>Ничего не найдено. Попробуйте изменить фильтры.</Empty>
          ) : (
            <div className="grid">
              {projects.map((p) => (
                <ProjectCard key={p.project_name} project={p} />
              ))}
            </div>
          )}
        </>
      )}
    </section>
  )
}
