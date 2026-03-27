<script setup>
import { ref } from 'vue'
import { queryAPI } from '../composables/api'

const props = defineProps({
  text: {
    type: String,
    default: ''
  }
})

const isPlaying = ref(false)
const isLoading = ref(false)
const selectedVoice = ref('aidar')
const audioPlayer = ref(null)

// Доступные голоса
const voices = ['aidar', 'baya', 'kseniya', 'xenia', 'eugene']

// Озвучка текста через серверный TTS
const speak = async () => {
  if (!props.text || isPlaying.value) return

  try {
    isLoading.value = true
    
    // Получаем аудио с сервера
    const audioBlob = await queryAPI.textToSpeech(props.text, selectedVoice.value)
    
    // Воспроизводим аудио
    const audioUrl = URL.createObjectURL(audioBlob)
    audioPlayer.value = new Audio(audioUrl)
    
    audioPlayer.value.onplay = () => {
      isPlaying.value = true
      isLoading.value = false
    }
    
    audioPlayer.value.onended = () => {
      isPlaying.value = false
      URL.revokeObjectURL(audioUrl)
    }
    
    audioPlayer.value.onerror = () => {
      isPlaying.value = false
      isLoading.value = false
    }
    
    await audioPlayer.value.play()
  } catch (err) {
    console.error('TTS error:', err)
    isLoading.value = false
    isPlaying.value = false
  }
}

const stop = () => {
  if (audioPlayer.value) {
    audioPlayer.value.pause()
    audioPlayer.value.currentTime = 0
  }
  isPlaying.value = false
}
</script>

<template>
  <div class="flex items-center gap-2">
    <!-- Выбор голоса -->
    <select
      v-model="selectedVoice"
      class="text-sm border border-gray-300 rounded px-2 py-1 bg-white max-w-[150px]"
      @click.stop
      :disabled="isPlaying"
    >
      <option v-for="voice in voices" :key="voice" :value="voice">
        {{ voice }}
      </option>
    </select>

    <!-- Кнопка озвучки -->
    <button
      @click="speak"
      :disabled="!text || isPlaying || isLoading"
      class="p-2 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      :class="[
        isPlaying
          ? 'bg-green-500 text-white'
          : 'bg-blue-500 hover:bg-blue-600 text-white'
      ]"
      :title="isPlaying ? 'Воспроизводится' : 'Озвучить ответ'"
    >
      <!-- Иконка загрузки -->
      <svg v-if="isLoading" class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
      </svg>
      <!-- Иконка динамика -->
      <svg v-else-if="!isPlaying" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z"/>
      </svg>
      <!-- Иконка воспроизведения -->
      <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z"/>
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2"/>
      </svg>
    </button>

    <!-- Кнопка остановки -->
    <button
      v-if="isPlaying"
      @click="stop"
      class="p-2 rounded-lg bg-red-500 hover:bg-red-600 text-white transition-colors"
      title="Остановить"
    >
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z"/>
      </svg>
    </button>
  </div>
</template>
