<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { queryAPI } from '../composables/api'

const props = defineProps({
  highlightedChunks: {
    type: Array,
    default: () => []
  }
})

const chunks = ref([])
const loading = ref(true)
const error = ref(null)
const containerRef = ref(null)

// Загрузка чанков при монтировании
onMounted(async () => {
  try {
    chunks.value = await queryAPI.getDocuments()
  } catch (err) {
    error.value = 'Не удалось загрузить документ'
    console.error(err)
  } finally {
    loading.value = false
  }
})

// Группировка чанков по заголовкам для красивого отображения
const groupedContent = computed(() => {
  const groups = []
  let currentGroup = null
  let charPosition = 0
  
  chunks.value.forEach((chunk, index) => {
    const text = chunk.text.trim()
    const isHeader = text.startsWith('#')
    
    if (isHeader) {
      // Сохраняем предыдущую группу
      if (currentGroup) {
        groups.push(currentGroup)
      }
      
      // Создаём новую группу с заголовком
      currentGroup = {
        type: 'section',
        header: {
          text: text.replace(/^#+\s*/, ''),
          level: text.match(/^#+/)[0].length,
          chunk: chunk.chunk
        },
        paragraphs: [],
        startChunk: chunk.chunk
      }
    } else if (text && currentGroup) {
      // Добавляем параграф в текущую группу
      currentGroup.paragraphs.push({
        text: text,
        chunk: chunk.chunk,
        position: charPosition
      })
    }
    
    charPosition += text.length
  })
  
  if (currentGroup) {
    groups.push(currentGroup)
  }
  
  return groups
})

// Проверка, является ли чанк подсвеченным
const isHighlighted = (chunkNum) => {
  return props.highlightedChunks.some(h => h.chunk === chunkNum)
}

// Автопрокрутка к подсвеченным чанкам
watch(() => props.highlightedChunks, async (newVal) => {
  if (!newVal || newVal.length === 0) return
  
  await nextTick()
  
  // Находим первый подсвеченный чанк и скроллим к нему
  const firstHighlighted = newVal[0]?.chunk
  if (firstHighlighted !== undefined) {
    const element = document.getElementById(`chunk-${firstHighlighted}`)
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
  }
}, { immediate: true })
</script>

<template>
  <div class="bg-white rounded-lg shadow-md p-6">
    <h2 class="text-xl font-semibold mb-4 text-gray-700">Текст инструкции</h2>
    
    <div v-if="loading" class="text-center py-8 text-gray-500">
      Загрузка документа...
    </div>
    
    <div v-else-if="error" class="text-center py-8 text-red-500">
      {{ error }}
    </div>
    
    <div v-else ref="containerRef" class="max-h-[600px] overflow-y-auto space-y-4 pr-2">
      <div v-for="(group, groupIndex) in groupedContent" :key="groupIndex" class="mb-6">
        <!-- Заголовок раздела -->
        <component
          v-if="group.header"
          :is="`h${Math.min(group.header.level + 1, 6)}`"
          class="text-gray-800 font-bold mt-4 mb-3 sticky top-0 bg-white py-2"
          :class="{
            'text-xl': group.header.level === 1,
            'text-lg': group.header.level === 2,
            'text-base': group.header.level >= 3
          }"
        >
          {{ group.header.text }}
          <span v-if="isHighlighted(group.header.chunk)" class="ml-2 text-xs px-2 py-1 bg-yellow-400 text-yellow-900 rounded">
            #{{ group.header.chunk }}
          </span>
        </component>
        
        <!-- Параграфы раздела -->
        <div class="space-y-2">
          <p
            v-for="(para, paraIndex) in group.paragraphs"
            :key="`${groupIndex}-${paraIndex}`"
            :id="`chunk-${para.chunk}`"
            class="text-gray-700 leading-relaxed transition-all duration-300"
            :class="[
              isHighlighted(para.chunk)
                ? 'bg-yellow-200 border-l-4 border-yellow-500 pl-3 py-1 rounded'
                : 'hover:bg-gray-50'
            ]"
          >
            {{ para.text }}
            <span v-if="isHighlighted(para.chunk)" class="ml-2 text-xs text-yellow-700 font-medium">
              [#{{ para.chunk }}]
            </span>
          </p>
        </div>
      </div>
      
      <!-- Легенда -->
      <div v-if="highlightedChunks.length > 0" class="mt-6 p-4 bg-yellow-50 rounded-lg border border-yellow-200">
        <p class="text-sm text-yellow-800">
          📍 Найдено совпадений: {{ highlightedChunks.length }}
        </p>
        <p class="text-xs text-yellow-700 mt-1">
          Чанки: {{ highlightedChunks.map(h => `#${h.chunk}`).join(', ') }}
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Кастомный скроллбар */
.max-h-\[600px\]::-webkit-scrollbar {
  width: 8px;
}

.max-h-\[600px\]::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.max-h-\[600px\]::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.max-h-\[600px\]::-webkit-scrollbar-thumb:hover {
  background: #a1a1a1;
}

/* Липкие заголовки */
.sticky {
  position: sticky;
  z-index: 10;
  backdrop-filter: blur(4px);
  background-color: rgba(255, 255, 255, 0.9);
}
</style>
