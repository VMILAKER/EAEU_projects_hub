import { createContext, useContext, useMemo, useState } from 'react'
import { createApi } from '../api.js'

const SettingsContext = createContext(null)

const STORAGE_KEY = 'eaeu-hub-settings'

function loadSettings() {
  const defaults = { apiKey: import.meta.env.VITE_API_KEY || '', demo: false }
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY))
    return { ...defaults, ...saved }
  } catch {
    return defaults
  }
}

export function SettingsProvider({ children }) {
  const [settings, setSettingsState] = useState(loadSettings)

  const setSettings = (next) => {
    setSettingsState(next)
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(next))
    } catch {
      // хранилище недоступно — настройки живут до перезагрузки
    }
  }

  const api = useMemo(() => createApi(settings), [settings])

  return (
    <SettingsContext.Provider value={{ settings, setSettings, api }}>
      {children}
    </SettingsContext.Provider>
  )
}

export function useSettings() {
  return useContext(SettingsContext)
}
