import { useRef, useState } from 'react'
import { useSettings } from '../context/SettingsContext.jsx'
import { ErrorBox, Loader } from '../components/Status.jsx'

const ACCEPT = '.csv,.xlsx,.xls,.json'
const COLUMNS = [
  '№',
  'Проект',
  'Направление',
  'Стадия',
  'Российские участники',
  'Белорусские участники',
  'Ключевые факты',
  'Источник',
  'Краткое описание',
]

// Ответ бэкенда: "Data from <file> is uploaded, Duplicates: ['A', 'B']"
function parseDuplicates(message) {
  const match = /Duplicates:\s*\[(.*)\]/s.exec(message || '')
  if (!match || !match[1].trim()) return []
  return match[1].split(/',\s*'/).map((s) => s.replace(/^['"]|['"]$/g, '').trim())
}

export default function UploadPage() {
  const { api } = useSettings()
  const inputRef = useRef(null)
  const [file, setFile] = useState(null)
  const [dragging, setDragging] = useState(false)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const pick = (f) => {
    if (!f) return
    setFile(f)
    setResult(null)
    setError(null)
  }

  const upload = async () => {
    if (!file) return
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const message = await api.uploadProjects(file)
      setResult({ message, duplicates: parseDuplicates(message) })
      setFile(null)
      if (inputRef.current) inputRef.current.value = ''
    } catch (e) {
      setError(e)
    } finally {
      setLoading(false)
    }
  }

  return (
    <section>
      <div className="page-head">
        <h1>Загрузка проектов</h1>
        <p className="muted">Импорт таблицы проектов в базу. Поддерживаются форматы CSV, XLSX, XLS и JSON.</p>
      </div>

      <div
        className={'card dropzone' + (dragging ? ' dropzone--active' : '')}
        onClick={() => inputRef.current?.click()}
        onDragOver={(e) => {
          e.preventDefault()
          setDragging(true)
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault()
          setDragging(false)
          pick(e.dataTransfer.files[0])
        }}
      >
        <input
          ref={inputRef}
          type="file"
          accept={ACCEPT}
          hidden
          onChange={(e) => pick(e.target.files[0])}
        />
        <div className="dropzone__icon">⇪</div>
        {file ? (
          <div>
            <strong>{file.name}</strong>
            <div className="muted">{(file.size / 1024).toFixed(1)} КБ</div>
          </div>
        ) : (
          <div>
            Перетащите файл сюда или <span className="link">выберите на компьютере</span>
          </div>
        )}
      </div>

      <div className="upload-actions">
        <button className="btn btn--primary" onClick={upload} disabled={!file || loading}>
          Загрузить
        </button>
      </div>

      {loading && <Loader text="Обработка файла и расчёт эмбеддингов…" />}
      <ErrorBox error={error} />

      {result && (
        <div className="alert alert--success">
          <div>Файл успешно загружен.</div>
          {result.duplicates.length > 0 && (
            <div className="duplicates">
              Пропущены уже существующие проекты ({result.duplicates.length}):
              <ul>
                {result.duplicates.map((d) => (
                  <li key={d}>{d}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      <div className="card">
        <h3 className="card__title">Ожидаемые столбцы</h3>
        <div className="chips">
          {COLUMNS.map((c) => (
            <span key={c} className="tag">
              {c}
            </span>
          ))}
        </div>
        <p className="muted small">
          Участники перечисляются с нумерацией («1. …  2. …»), ключевые факты и описание — пунктами через «•»,
          источники — ссылками. Проекты с уже существующим названием пропускаются.
        </p>
      </div>
    </section>
  )
}
