# EAEU Projects Hub — фронтенд

React-интерфейс (Vite + JSX) для бэкенда `EAEU_projects_hub`.

## Страницы

| Страница | Эндпоинт бэкенда |
|---|---|
| **Проекты** — каталог с фильтрами по названию, направлению, стадии, участникам | `GET /eaeu_hub/get_projects` |
| **Умный поиск** — вопрос на естественном языке, ответ от LLM (RAG) | `GET /eaeu_hub/get_projects_by_query` |
| **Статистика** — распределения по направлениям, стадиям, странам, компаниям | `GET /eaeu_hub/statistics` |
| **Загрузка** — импорт CSV / XLSX / JSON | `POST /eaeu_hub/upload_projects` |

API-ключ (заголовок `API_Key`) задаётся в окне «Настройки» или через `VITE_API_KEY`.
Там же включается **демо-режим** — интерфейс работает на тестовых данных без бэкенда.

## Запуск

Нужен Node.js 18+ (https://nodejs.org).

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

Откройте http://localhost:5173.

В режиме разработки Vite проксирует запросы `/eaeu_hub/*` на `VITE_BACKEND_URL`
(по умолчанию `http://localhost:8002` — порт из `docker-compose.yaml`), поэтому CORS на бэкенде не нужен.

## Сборка для продакшена

```bash
npm run build
```

Готовые файлы — в `dist/`. Раздавайте их любым веб-сервером (например, nginx) и проксируйте
`/eaeu_hub` на бэкенд. Учтите: nginx по умолчанию отбрасывает заголовки с подчёркиванием,
поэтому для `API_Key` нужна директива `underscores_in_headers on;`. Если фронтенд и бэкенд будут на разных доменах — включите `CORSMiddleware`
в `main.py` (там он уже заготовлен в комментариях).

## Структура

```
src/
  main.jsx                   точка входа
  App.jsx                    маршруты
  api.js                     запросы к бэкенду (+ демо-режим)
  mockData.js                тестовые данные
  context/SettingsContext.jsx  API-ключ и режим, общий клиент API
  components/                Layout, ProjectCard, BarChart, SettingsModal, Status
  pages/                     ProjectsPage, SearchPage, StatisticsPage, UploadPage
  styles.css                 стили (светлая и тёмная тема)
```
