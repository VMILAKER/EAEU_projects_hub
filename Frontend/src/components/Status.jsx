export function Loader({ text = 'Загрузка…' }) {
  return (
    <div className="status">
      <span className="spinner" />
      {text}
    </div>
  )
}

export function ErrorBox({ error }) {
  if (!error) return null
  return <div className="alert alert--error">{error.message || String(error)}</div>
}

export function Empty({ children }) {
  return <div className="status status--empty">{children}</div>
}
