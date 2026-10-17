import { useState } from 'react'
import { NavLink, Outlet } from 'react-router-dom'
import { useSettings } from '../context/SettingsContext.jsx'
import SettingsModal from './SettingsModal.jsx'

const NAV = [
  { to: '/', label: 'Проекты', end: true },
  { to: '/search', label: 'Умный поиск' },
  { to: '/statistics', label: 'Статистика' },
  { to: '/upload', label: 'Загрузка' },
]

export default function Layout() {
  const { settings } = useSettings()
  const [settingsOpen, setSettingsOpen] = useState(false)

  return (
    <div className="app">
      <header className="header">
        <div className="header__inner">
          <div className="brand">
            <span className="brand__logo">ЕАЭС</span>
            <span className="brand__title">Хаб совместных проектов</span>
          </div>
          <nav className="nav">
            {NAV.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.end}
                className={({ isActive }) => 'nav__link' + (isActive ? ' nav__link--active' : '')}
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
          <button className="btn btn--ghost" onClick={() => setSettingsOpen(true)}>
            {settings.demo && <span className="badge badge--warn">демо</span>}
            Настройки
          </button>
        </div>
      </header>

      <main className="main">
        <Outlet />
      </main>

      {settingsOpen && <SettingsModal onClose={() => setSettingsOpen(false)} />}
    </div>
  )
}
