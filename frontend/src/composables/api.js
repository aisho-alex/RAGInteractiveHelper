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

  async getDocuments() {
    const response = await api.get('/documents/list')
    return response.data
  },

  async getSpeakers() {
    const response = await api.get('/audio/speakers')
    return response.data
  },

  async textToSpeech(text, speaker = 'aidar', sampleRate = 48000) {
    const response = await api.post(
      `/audio/tts?text=${encodeURIComponent(text)}&speaker=${speaker}&sample_rate=${sampleRate}`,
      null,
      { responseType: 'arraybuffer' }
    )
    return response.data
  },

  async speechToText(audioBlob) {
    const formData = new FormData()
    formData.append('file', audioBlob)

    const response = await api.post('/audio/stt', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },
}
