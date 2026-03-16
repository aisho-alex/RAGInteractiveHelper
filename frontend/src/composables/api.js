import axios from 'axios'

const API_BASE = '/api'

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const queryAPI = {
  async sendQuery(query, topK = 3) {
    const response = await api.post('/query', { query, top_k: topK })
    return response.data
  },
}
