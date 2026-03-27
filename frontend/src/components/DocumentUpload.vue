<script setup>
import { ref } from 'vue'
import { queryAPI } from '../composables/api'

const emit = defineEmits(['document-loaded'])

const isUploading = ref(false)
const uploadError = ref(null)
const uploadSuccess = ref(null)
const dragOver = ref(false)

const fileInput = ref(null)

function handleFileSelect(event) {
  const file = event.target.files[0]
  if (file) {
    uploadFile(file)
  }
}

function handleDragOver(event) {
  event.preventDefault()
  dragOver.value = true
}

function handleDragLeave(event) {
  event.preventDefault()
  dragOver.value = false
}

function handleDrop(event) {
  event.preventDefault()
  dragOver.value = false
  const file = event.dataTransfer.files[0]
  if (file) {
    uploadFile(file)
  }
}

async function uploadFile(file) {
  const allowedTypes = ['application/pdf', 'text/plain', 'text/markdown', 'text/x-markdown']
  const allowedExtensions = ['.pdf', '.txt', '.md']
  
  const fileExtension = '.' + file.name.split('.').pop().toLowerCase()
  
  if (!allowedExtensions.includes(fileExtension)) {
    uploadError.value = 'Неподдерживаемый формат файла. Используйте PDF, TXT или MD'
    return
  }

  isUploading.value = true
  uploadError.value = null
  uploadSuccess.value = null

  try {
    const result = await queryAPI.uploadDocument(file)
    uploadSuccess.value = `Документ "${file.name}" успешно загружен!`
    emit('document-loaded')
    // Очистка input для повторной загрузки того же файла
    if (fileInput.value) {
      fileInput.value.value = ''
    }
  } catch (err) {
    uploadError.value = 'Ошибка при загрузке документа. Проверьте подключение к серверу.'
    console.error(err)
  } finally {
    isUploading.value = false
  }
}

function triggerFileInput() {
  fileInput.value?.click()
}
</script>

<template>
  <div class="bg-white rounded-lg shadow-md p-6 mb-6">
    <h2 class="text-xl font-semibold mb-4 text-gray-700">Загрузка документа</h2>

    <div
      class="border-2 border-dashed rounded-lg p-8 text-center transition-colors"
      :class="dragOver ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'"
      @dragover="handleDragOver"
      @dragleave="handleDragLeave"
      @drop="handleDrop"
      @click="triggerFileInput"
    >
      <input
        ref="fileInput"
        type="file"
        accept=".pdf,.txt,.md"
        class="hidden"
        @change="handleFileSelect"
      />

      <div class="space-y-4">
        <svg
          class="mx-auto h-12 w-12 text-gray-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
          />
        </svg>

        <div class="text-sm text-gray-600">
          <p class="font-medium text-gray-900">
            Перетащите файл сюда или кликните для выбора
          </p>
          <p class="mt-1">Поддерживаются форматы: PDF, TXT, MD</p>
        </div>

        <button
          type="button"
          class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          :disabled="isUploading"
        >
          {{ isUploading ? 'Загрузка...' : 'Выбрать файл' }}
        </button>
      </div>
    </div>

    <div v-if="uploadSuccess" class="mt-4 bg-green-50 border border-green-200 text-green-700 p-4 rounded-lg">
      {{ uploadSuccess }}
    </div>

    <div v-if="uploadError" class="mt-4 bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg">
      {{ uploadError }}
    </div>
  </div>
</template>
