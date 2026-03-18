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
    const data = await queryAPI.getDocuments()
    chunks.value = Array.isArray(data) ? data : []
  } catch (err) {
    error.value = 'Не удалось загрузить документ'
    console.error(err)
    chunks.value = []
  } finally {
    loading.value = false
  }
})

// Собираем полный текст с маппингом позиций на чанки
const documentData = computed(() => {
  if (!chunks.value || chunks.value.length === 0) return { text: '', chunkMap: {} }

  const sorted = [...chunks.value].sort((a, b) => (a.chunk || 0) - (b.chunk || 0))
  const chunkMap = {} // позиция -> номер чанка
  let fullText = ''

  for (let i = 0; i < sorted.length; i++) {
    const chunk = sorted[i]
    const chunkText = chunk?.text || ''
    const chunkNum = chunk?.chunk || i
    
    if (!chunkText) continue

    let textToAdd = chunkText
    let startOffset = fullText.length

    if (i > 0) {
      const prevText = sorted[i - 1]?.text || ''
      const overlapSize = Math.min(200, Math.floor(prevText.length / 3))
      
      if (overlapSize > 0) {
        const overlap = prevText.slice(-overlapSize)
        const overlapPos = chunkText.indexOf(overlap)
        
        if (overlapPos >= 0) {
          textToAdd = chunkText.slice(overlapPos + overlap.length)
          startOffset = fullText.length
        }
      }
    }

    // Маппим каждую позицию текста на номер чанка
    for (let j = 0; j < textToAdd.length; j++) {
      chunkMap[startOffset + j] = chunkNum
    }

    fullText += textToAdd
  }

  console.log('documentData:', { 
    textLength: fullText.length, 
    chunkMapSize: Object.keys(chunkMap).length,
    sampleChunks: Object.values(chunkMap).slice(0, 20)
  })

  return { text: fullText, chunkMap }
})

// Получаем Set номеров подсвеченных чанков
const highlightedChunkSet = computed(() => {
  if (!props.highlightedChunks || props.highlightedChunks.length === 0) return new Set()
  return new Set(props.highlightedChunks.map(h => h.chunk))
})

// Разбиваем текст на строки с информацией о чанках
const linesWithChunks = computed(() => {
  const { text, chunkMap } = documentData.value
  if (!text) return []

  return text.split('\n').map((lineText, lineIndex) => {
    // Находим позицию начала строки
    let startPos = 0
    for (let i = 0; i < lineIndex; i++) {
      startPos += text.split('\n')[i].length + 1
    }

    // Проверяем, попадает ли строка в подсвеченный чанк
    const chunkNum = chunkMap[startPos] || null
    const isHighlighted = chunkNum !== null && highlightedChunkSet.value.has(chunkNum)

    return {
      text: lineText,
      chunk: chunkNum,
      isHighlighted
    }
  })
})

// Группируем строки в секции
const sections = computed(() => {
  const lines = linesWithChunks.value
  if (!lines || lines.length === 0) return []

  const result = []
  let currentParagraph = []

  lines.forEach((line) => {
    const trimmed = line.text.trim()

    if (!trimmed) {
      if (currentParagraph.length > 0) {
        result.push({
          type: 'paragraph',
          content: currentParagraph.map(l => l.text).join('\n'),
          isHighlighted: currentParagraph.some(l => l.isHighlighted)
        })
        currentParagraph = []
      }
      return
    }

    if (trimmed.startsWith('#')) {
      if (currentParagraph.length > 0) {
        result.push({
          type: 'paragraph',
          content: currentParagraph.map(l => l.text).join('\n'),
          isHighlighted: currentParagraph.some(l => l.isHighlighted)
        })
        currentParagraph = []
      }

      const match = trimmed.match(/^#+/)
      const level = match ? match[0].length : 1
      const headerText = trimmed.replace(/^#+\s*/, '')
      
      result.push({
        type: 'header',
        level,
        content: headerText,
        isHighlighted: line.isHighlighted
      })
    } else {
      currentParagraph.push(line)
    }
  })

  if (currentParagraph.length > 0) {
    result.push({
      type: 'paragraph',
      content: currentParagraph.map(l => l.text).join('\n'),
      isHighlighted: currentParagraph.some(l => l.isHighlighted)
    })
  }

  return result
})

// Автопрокрутка
watch(() => props.highlightedChunks, async (newVal) => {
  if (!newVal || newVal.length === 0) return
  await nextTick()
  if (containerRef.value) {
    containerRef.value.scrollTop = 0
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
      <div v-for="(section, index) in sections" :key="index">
        <component
          v-if="section.type === 'header'"
          :is="`h${Math.min(section.level + 1, 6)}`"
          class="text-gray-800 font-bold mt-4 mb-2"
          :class="{
            'text-xl': section.level === 1,
            'text-lg': section.level === 2,
            'text-base': section.level >= 3
          }"
          :style="section.isHighlighted ? 'background-color: #fef3c7; border-left: 4px solid #eab308; padding-left: 8px;' : ''"
        >
          {{ section.content }}
        </component>
        
        <p
          v-else-if="section.type === 'paragraph'"
          class="leading-relaxed whitespace-pre-wrap transition-all duration-300"
          :class="[
            section.isHighlighted
              ? 'bg-yellow-100 border-l-4 border-yellow-500 pl-3 py-2 rounded text-gray-800'
              : 'text-gray-700'
          ]"
        >
          {{ section.content }}
        </p>
      </div>
      
      <div v-if="highlightedChunks.length > 0" class="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
        <p class="text-sm text-blue-800 font-medium">
          ✅ Найдено чанков: {{ highlightedChunks.length }} 
          <span class="font-mono text-xs">({{ highlightedChunks.map(h => '#' + h.chunk).join(', ') }})</span>
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.max-h-\[600px\]::-webkit-scrollbar { width: 8px; }
.max-h-\[600px\]::-webkit-scrollbar-track { background: #f1f1f1; border-radius: 4px; }
.max-h-\[600px\]::-webkit-scrollbar-thumb { background: #c1c1c1; border-radius: 4px; }
.max-h-\[600px\]::-webkit-scrollbar-thumb:hover { background: #a1a1a1; }
</style>
