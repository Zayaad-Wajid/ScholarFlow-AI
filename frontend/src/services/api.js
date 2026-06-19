import axios from 'axios'

export const TOKEN_STORAGE_KEY = 'scholarflow_token'
export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1'

export function getStoredToken() {
  return window.localStorage.getItem(TOKEN_STORAGE_KEY)
}

export function setStoredToken(token) {
  if (token) {
    window.localStorage.setItem(TOKEN_STORAGE_KEY, token)
    return
  }

  window.localStorage.removeItem(TOKEN_STORAGE_KEY)
}

const api = axios.create({
  baseURL: API_BASE_URL,
})

api.interceptors.request.use((config) => {
  const token = getStoredToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && !error.config?.skipAuthRedirect) {
      window.dispatchEvent(new CustomEvent('scholarflow:unauthorized'))
    }
    return Promise.reject(error)
  },
)

export function getApiError(error, fallbackMessage) {
  return error?.response?.data?.detail || fallbackMessage
}

export const authApi = {
  register(payload) {
    return api.post('/auth/register', payload, { skipAuthRedirect: true })
  },
  login(payload) {
    return api.post('/auth/login', payload, { skipAuthRedirect: true })
  },
  me() {
    return api.get('/auth/me')
  },
}

export const projectApi = {
  list() {
    return api.get('/research/projects')
  },
  create(payload) {
    return api.post('/research/projects', payload)
  },
  get(projectId) {
    return api.get(`/research/projects/${projectId}`)
  },
  delete(projectId) {
    return api.delete(`/research/projects/${projectId}`)
  },
}

export const documentApi = {
  list(projectId) {
    return api.get(`/documents/project/${projectId}`)
  },
  upload(projectId, file) {
    const formData = new FormData()
    formData.append('project_id', String(projectId))
    formData.append('file', file)
    return api.post('/documents/upload', formData)
  },
  process(documentId) {
    return api.post(`/documents/${documentId}/process`)
  },
  index(documentId) {
    return api.post(`/documents/${documentId}/index`)
  },
  remove(documentId) {
    return api.delete(`/documents/${documentId}`)
  },
}

export const chatApi = {
  ask(payload) {
    return api.post('/chat/ask', payload)
  },
}

export const reportApi = {
  generate(payload) {
    return api.post('/reports/generate', payload)
  },
  list(projectId) {
    return api.get(`/reports/project/${projectId}`)
  },
  get(reportId) {
    return api.get(`/reports/${reportId}`)
  },
  remove(reportId) {
    return api.delete(`/reports/${reportId}`)
  },
}

export default api
