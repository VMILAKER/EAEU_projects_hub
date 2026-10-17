import { useState } from 'react'
import { useSettings } from '../context/SettingsContext.jsx'

export default function SettingsModal({ onClose }) {
  const { settings, setSettings } = useSettings()
  const [apiKey, setApiKey] = useState(settings.apiKey)
  const [demo, setDemo] = useState(settings.demo)

  const save = (e) => {
    e.preventDefault()
    setSettings({ ...settings, apiKey: apiKey.trim(), demo })
    onClose()
  }

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <form className="modal" onClick={(e) => e.stopPropagation()} onSubmit={save}>
        <h2>Настройки</h2>

        <label className="field">
          <span className="field__label">API-ключ</span>
          <input
            className="input"
            type="password"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            placeholder="INTERNAL_BACKEND_API_KEY"
            autoComplete="off"
          />
          <span className="field__hint">Передаётся в заголовке API_Key при каждом запросе.</span>
        </label>

        <label className="checkbox">
          <input type="checkbox" checked={demo} onChange={(e) => setDemo(e.target.checked)} />
          Демо-режим (тестовые данные без бэкенда)
        </label>

        <div className="modal__actions">
          <button type="button" className="btn btn--ghost" onClick={onClose}>
            Отмена
          </button>
          <button type="submit" className="btn btn--primary">
            Сохранить
          </button>
        </div>
      </form>
    </div>
  )
}
