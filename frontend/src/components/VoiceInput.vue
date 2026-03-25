<script setup>
import { ref, onMounted } from 'vue'
import { queryAPI } from '../composables/api'

const emit = defineEmits(['input', 'start-record', 'stop-record'])

const props = defineProps({
  isRecording: {
    type: Boolean,
    default: false
  }
})

const isListening = ref(false)
const mediaRecorder = ref(null)
const audioChunks = ref([])

// Инициализация распознавания речи через Web Audio API
const startListening = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    mediaRecorder.value = new MediaRecorder(stream)
    audioChunks.value = []

    mediaRecorder.value.ondataavailable = (event) => {
      audioChunks.value.push(event.data)
    }

    mediaRecorder.value.onstop = async () => {
      const audioBlob = new Blob(audioChunks.value, { type: 'audio/wav' })
      console.log('Audio recorded:', audioBlob.size, 'bytes')

      // Отправляем на сервер для распознавания
      try {
        const result = await queryAPI.speechToText(audioBlob)
        console.log('STT result:', result)
        if (result.text) {
          emit('input', result.text)
        }
      } catch (err) {
        console.error('STT error:', err)
        alert('Ошибка распознавания речи: ' + (err.message || err))
      }

      // Останавливаем поток
      stream.getTracks().forEach(track => track.stop())
    }

    mediaRecorder.value.start()
    isListening.value = true
    emit('start-record')
  } catch (err) {
    console.error('Microphone access error:', err)
    alert('Не удалось получить доступ к микрофону')
  }
}

const stopListening = () => {
  if (mediaRecorder.value && isListening.value) {
    mediaRecorder.value.stop()
    isListening.value = false
    emit('stop-record')
  }
}

const toggleListening = () => {
  if (isListening.value) {
    stopListening()
  } else {
    startListening()
  }
}

onMounted(() => {
  // Проверка поддержки MediaRecorder
  if (!navigator.mediaDevices || !MediaRecorder) {
    console.warn('MediaRecorder не поддерживается')
  }
})
</script>

<template>
  <button
    @click="toggleListening"
    :class="[
      'p-2 rounded-lg transition-colors',
      isListening
        ? 'bg-red-500 hover:bg-red-600 text-white animate-pulse'
        : 'bg-gray-200 hover:bg-gray-300 text-gray-700'
    ]"
    :title="isListening ? 'Остановить запись' : 'Голосовой ввод'"
  >
    <!-- Иконка микрофона -->
    <svg v-if="!isListening" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"/>
    </svg>
    <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z"/>
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2"/>
    </svg>
  </button>
</template>

<style scoped>
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
.animate-pulse {
  animation: pulse 1s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>
