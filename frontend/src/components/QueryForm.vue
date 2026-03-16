<script setup>
import { ref } from 'vue'
import { queryAPI } from '../composables/api'

const query = ref('')
const response = ref(null)
const loading = ref(false)
const error = ref(null)

async function handleSubmit() {
  if (!query.value.trim()) return
  
  loading.value = true
  error.value = null
  response.value = null

  try {
    const result = await queryAPI.sendQuery(query.value, 3)
    response.value = result
  } catch (err) {
    error.value = 'Ошибка при выполнении запроса. Проверьте подключение к серверу.'
    console.error(err)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="bg-white rounded-lg shadow-md p-6 mb-6">
    <h2 class="text-xl font-semibold mb-4 text-gray-700">Запрос к документам</h2>
    
    <form @submit.prevent="handleSubmit" class="space-y-4">
      <textarea
        v-model="query"
        placeholder="Введите ваш вопрос по документам..."
        class="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        rows="4"
        required
      />
      
      <button
        type="submit"
        :disabled="loading || !query.trim()"
        class="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
      >
        {{ loading ? 'Обработка...' : 'Отправить запрос' }}
      </button>
    </form>

    <div v-if="error" class="mt-4 bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg">
      {{ error }}
    </div>

    <div v-if="response" class="mt-6">
      <h3 class="text-lg font-medium mb-3 text-gray-700">Ответ</h3>
      <div class="prose max-w-none mb-6">
        <p class="text-gray-800 whitespace-pre-wrap">{{ response.answer }}</p>
      </div>

      <div v-if="response.sources?.length > 0">
        <h4 class="text-md font-medium mb-3 text-gray-700">Источники:</h4>
        <div class="space-y-3">
          <div
            v-for="(source, index) in response.sources"
            :key="index"
            class="bg-gray-50 p-4 rounded-lg border border-gray-200"
          >
            <p class="text-sm text-gray-600 mb-2">
              <strong>Фрагмент {{ index + 1 }}</strong>
              <span v-if="source.metadata?.type" class="ml-2 px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                {{ source.metadata.type }}
              </span>
            </p>
            <p class="text-gray-700 text-sm">{{ source.content }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
