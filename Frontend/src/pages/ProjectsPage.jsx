import { useEffect, useState } from 'react'
import { useSettings } from '../context/SettingsContext.jsx'
import ProjectCard from '../components/ProjectCard.jsx'
import { Empty, ErrorBox, Loader } from '../components/Status.jsx'

const EMPTY_FILTERS = { project_name: '', scope: '', stage: '', participants: '' }

const FIELDS = [
  { name: 'project_name', label: 'Название проекта' },
  { name: 'scope', label: 'Направление' },
  { name: 'stage', label: 'Стадия'},
  { name: 'participants', label: 'Участники' },
]

// --- ComboSelect: теперь только input + dropdown. Теги вынесены наружу ---
function ComboSelect({ options, value, onChange, placeholder, label }) {
  const [input, setInput] = useState('')
  const [isOpen, setIsOpen] = useState(false)

  const filtered = options.filter((o) =>
    (o.label ?? '').toLowerCase().includes(input.toLowerCase())
  )

  const handleSelect = (opt) => {
    if (!value.includes(opt.value)) {
      onChange([...value, opt.value])
      // Текст остаётся в input — не очищаем
    }
    setIsOpen(false)
  }

  const handleBlur = () => {
    setTimeout(() => setIsOpen(false), 200)
  }

  return (
    <div style={{ position: 'relative', width: '100%' }}>
      <label className="field">
        <span className="field__label">{label}</span>
        <div style={{ position: 'relative' }}>
          <input
            className="input"
            value={input}
            placeholder={value.length === 0 ? placeholder : ''}
            onChange={(e) => {
              setInput(e.target.value)
              setIsOpen(true)
            }}
            onFocus={() => setIsOpen(true)}
            onBlur={handleBlur}
            style={{
              width: '100%',
              padding: '8px 12px',
              boxSizing: 'border-box',
              border: '1px solid var(--color-border, #ccc)',
              borderRadius: '6px',
              backgroundColor: 'var(--color-bg, #fff)',
              color: 'var(--color-text, #000)',
              outline: 'none',
              whiteSpace: 'nowrap',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
            }}
          />

          {isOpen && (
            <ul
              style={{
                position: 'absolute',
                top: '100%',
                left: 0,
                right: 0,
                maxHeight: '200px',
                overflowY: 'auto',
                border: '1px solid var(--color-border, #ccc)',
                background: 'var(--color-dropdown-bg, #fff)',
                margin: 0,
                padding: 0,
                zIndex: 10,
                listStyle: 'none',
                boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
                borderRadius: '6px',
              }}
            >
              {filtered.length === 0 ? (
                <li
                  style={{
                    padding: '12px',
                    color: 'var(--color-muted, #888)',
                    fontStyle: 'italic',
                  }}
                >
                  Не найдено
                </li>
              ) : (
                filtered.map((opt) => (
                  <li
                    key={opt.value}
                    onClick={() => handleSelect(opt)}
                    onMouseEnter={(e) => (e.currentTarget.style.background = 'var(--color-hover-bg, #f5f5f5)')}
                    onMouseLeave={(e) => (e.currentTarget.style.background = 'var(--color-dropdown-bg, #fff)')}
                    style={{
                      padding: '10px 12px',
                      cursor: 'pointer',
                      color: 'var(--color-text, #000)',
                      transition: 'background 0.2s ease',
                    }}
                  >
                    {opt.label}
                  </li>
                ))
              )}
            </ul>
          )}
        </div>
      </label>
    </div>
  )
}

// --- Компонент тегов: выносим отдельно, чтобы не ломать высоту полей ---
function TagsList({ options, value, onRemove }) {
  return (
    <div style={{ marginTop: '6px', display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
      {value.map((v) => {
        const opt = options.find((o) => o.value === v)
        return (
          <span
            key={v}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '8px',
              padding: '6px 10px',
              borderRadius: '4px', // прямоугольные с лёгким скруглением
              fontSize: '13px',
              fontWeight: 500,
              backgroundColor: 'var(--color-tag-bg, #eef2ff)',
              color: 'var(--color-tag-text, #2563eb)',
              boxShadow: '0 1px 2px rgba(0,0,0,0.05)',
            }}
          >
            {opt?.label || v}
            <span
              onClick={() => onRemove(v)}
              style={{ cursor: 'pointer', color: 'var(--color-tag-remove, #ef4444)', fontWeight: 'bold' }}
            >
              ×
            </span>
          </span>
        )
      })}
    </div>
  )
}

export default function ProjectsPage() {
  const { api } = useSettings()
  const [filters, setFilters] = useState(EMPTY_FILTERS)
  const [projects, setProjects] = useState([])
  const [preloadedData, setPreloadedData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const load = async (f) => {
    setLoading(true)
    setError(null)
    try {
      const data = await api.getProjects(f)
      const preloaded_data = await api.getPreloadedData(f)

      setProjects(Array.isArray(data) ? data : [])
      setPreloadedData(Array.isArray(preloaded_data) ? preloaded_data : [])
    } catch (e) {
      setError(e)
      setProjects([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load(filters)
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
        <p className="muted">
          Каталог совместных проектов государств ЕАЭС. Поля фильтров выровнены по верхнему краю, теги отображаются под ними.
        </p>
      </div>

      <form className="card filters" onSubmit={onSubmit}>
        {/* Сетка: все поля на одном уровне */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
            gap: '16px',
            alignItems: 'flex-start', // ключевой момент: все начинаются с одной линии
          }}
        >
          {FIELDS.map((f, fieldIndex) => {
            const options = preloadedData?.[fieldIndex] || []
            const currentValue = Array.isArray(filters[f.name]) ? filters[f.name] : []

            return (
              <div key={f.name} style={{ display: 'contents' }}>
                {/* Поле ввода */}
                <ComboSelect
                  options={options}
                  value={currentValue}
                  onChange={(newValues) =>
                    setFilters((prev) => ({ ...prev, [f.name]: newValues }))
                  }
                  placeholder={f.placeholder}
                  label={f.label}
                />

                {/* Теги под полем — не влияют на высоту соседей */}
                <TagsList
                  options={options}
                  value={currentValue}
                  onRemove={(val) =>
                    setFilters((prev) => ({
                      ...prev,
                      [f.name]: prev[f.name].filter((v) => v !== val),
                    }))
                  }
                />
              </div>
            )
          })}
        </div>

        <div className="filters__actions" style={{ marginTop: '24px' }}>
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

      {!loading && (
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
