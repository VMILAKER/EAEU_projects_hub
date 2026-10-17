import { useState } from 'react'
import { useSettings } from '../context/SettingsContext.jsx'
import { Empty, ErrorBox, Loader } from '../components/Status.jsx'

const EXAMPLES = [
  'Запуск БелАЭС в 2026-м году',
  'Совместные проекты в области транспорта',
  'Какие проекты связаны с микроэлектроникой?',
]

export default function SearchPage() {
  const { api } = useSettings()
  const [query, setQuery] = useState('')
  const [topK, setTopK] = useState(5)
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const ask = async (q) => {
    const text = q.trim()
    if (!text) return
    setLoading(true)
    setError(null)
    try {
      const answer = await api.searchByQuery(text, topK)

      let paragraphs = []

      if (typeof answer === 'string') {
        paragraphs = answer
          .split(/\r?\n/)
          .map(line => line.trim())
          .filter(line => line.length > 0)
      }

      else if (Array.isArray(answer)) {
        paragraphs = answer
          .map((item) => {
            if (typeof item === 'object' && item !== null) {
              return item.content ?? item.text ?? String(item)
            }
            return typeof item === 'string' ? item : String(item)
          })
          .flatMap(str => str.split(/\r?\n/))
          .map(line => line.trim())
          .filter(line => line.length > 0)
      }
      setHistory((h) => [{ query: text, paragraphs }, ...h])
      setQuery('')
    } catch (e) {
      setError(e)
    } finally {
      setLoading(false)
    }
  }

  const onSubmit = (e) => {
    e.preventDefault()
    ask(query)
  }

  return (
    <section>
      <div className="page-head">
        <h1>Умный поиск</h1>
        <p className="muted">
          Задайте вопрос на естественном языке — система найдёт релевантные проекты (векторный поиск + BM25 +
          реранкинг) и сформирует ответ с помощью LLM.
        </p>
      </div>

      <form className="card search" onSubmit={onSubmit}>
        <textarea
          className="input search__input"
          rows={3}
          value={query}
          placeholder="Например: какие энергетические проекты реализуются совместно с Россией?"
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault()
              ask(query)
            }
          }}
        />
        <div className="search__row">
          <div className="chips">
            {EXAMPLES.map((ex) => (
              <button type="button" key={ex} className="chip" onClick={() => ask(ex)} disabled={loading}>
                {ex}
              </button>
            ))}
          </div>
          <label className="topk">
            Источников
            <input
              className="input input--small"
              type="number"
              min={1}
              max={20}
              value={topK}
              onChange={(e) => setTopK(Math.max(1, Math.min(20, Number(e.target.value) || 1)))}
            />
          </label>
          <button className="btn btn--primary" type="submit" disabled={loading || !query.trim()}>
            Спросить
          </button>
        </div>
      </form>

      <ErrorBox error={error} />
      {loading && <Loader text="Ищем проекты и готовим ответ… Это может занять до минуты." />}

      {history.length === 0 && !loading && <Empty>Здесь появятся ответы на ваши вопросы.</Empty>}

      <div className="answers">
        {history.map((item, i) => (
          <article key={history.length - i} className="card answer">
            <div className="answer__query">{item.query}</div>
            {item.paragraphs.length ? (
              item.paragraphs.map((p, j) => <p key={j}>{p}</p>)
            ) : (
              <p className="muted">Модель не вернула ответ. Проверьте, что Ollama запущена и модель загружена.</p>
            )}
          </article>
        ))}
      </div>
    </section>
  )
}
