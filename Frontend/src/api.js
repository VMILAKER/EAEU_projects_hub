import { mockProjects, mockSearchAnswer, mockStatistics } from './mockData.js'

const BASE = '/eaeu_hub'

export class ApiError extends Error {
  constructor(message, status) {
    super(message)
    this.status = status
  }
}

function formatDetail(detail) {
  if (!detail) return null
  if (typeof detail === 'string') return detail
  return JSON.stringify(detail)
}

async function request(path, { apiKey, params, ...options } = {}) {
  const query = params
    ? '?' +
      new URLSearchParams(
        Object.entries(params).filter(([, v]) => v !== undefined && v !== null && v !== ''),
      ).toString()
    : ''

  let response
  try {
    response = await fetch(`${BASE}${path}${query}`, {
      ...options,
      headers: { API_Key: apiKey ?? '', ...(options.headers || {}) },
    })
  } catch {
    throw new ApiError('Не удалось связаться с сервером. Проверьте, что бэкенд запущен.', 0)
  }

  const text = await response.text()
  let data = text
  try {
    data = text ? JSON.parse(text) : null
  } catch {
    // ответ не JSON — оставляем строку
  }

  if (!response.ok) {
    const messages = {
      400: 'Не указан API-ключ',
      401: 'Неверный API-ключ',
    }
    const detail = formatDetail(data?.detail)
    // пустой ответ 5xx — так dev-прокси сообщает, что бэкенд недоступен
    const fallback =
      response.status >= 500 && !text
        ? 'Бэкенд недоступен. Запустите сервер или включите демо-режим в настройках.'
        : `Ошибка ${response.status}`
    throw new ApiError(detail || messages[response.status] || fallback, response.status)
  }
  return data
}

const delay = (ms) => new Promise((r) => setTimeout(r, ms))

function filterMock({ project_name, scope, stage, participants }) {
  const split = (s) => (s ? s.split(',').map((x) => x.trim().toLowerCase()).filter(Boolean) : [])
  const match = (value, terms) => !terms.length || terms.some((t) => value.toLowerCase().includes(t))
  const res = mockProjects.filter(
    (p) =>
      match(p.project_name, split(project_name)) &&
      match(p.scope, split(scope)) &&
      match(p.stage, split(stage)) &&
      (!split(participants).length ||
        p.participants.some((obj) => match(Object.values(obj)[0], split(participants)))),
  )
  return res.length ? res : 'No matches'
}

export function createApi({ apiKey, demo }) {
  return {
    async getProjects(filters) {
      if (demo) {
        await delay(300)
        return filterMock(filters)
      }
      return request('/projects', { apiKey, params: filters })
    },

    async searchByQuery(query, topK) {
      if (demo) {
        await delay(900)
        return mockSearchAnswer(query)
      }
      return request('/projects_by_query', { apiKey, params: { query, top_K: topK } })
    },

    async getStatistics() {
      if (demo) {
        await delay(300)
        return mockStatistics
      }
      return request('/statistics', { apiKey })
    },

    async uploadProjects(file) {
      if (demo) {
        await delay(700)
        return `Data from ${file.name} is uploaded, Duplicates: []\n`
      }
      const body = new FormData()
      body.append('file', file)
      return request('/projects', { apiKey, method: 'POST', body })
    },
  }
}
