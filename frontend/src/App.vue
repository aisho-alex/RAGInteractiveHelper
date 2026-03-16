<script setup>
import { ref } from 'vue'
import QueryForm from './components/QueryForm.vue'
import DocumentViewer from './components/DocumentViewer.vue'

const highlightedChunks = ref([])

function handleHighlightChunks(chunks) {
  highlightedChunks.value = chunks
}
</script>

<template>
  <main class="min-h-screen p-8">
    <div class="max-w-6xl mx-auto">
      <h1 class="text-3xl font-bold text-center mb-8 text-gray-800">
        RAG Система
      </h1>
      
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="space-y-6">
          <QueryForm @highlight-chunks="handleHighlightChunks" />
        </div>
        
        <div>
          <DocumentViewer :highlighted-chunks="highlightedChunks" />
        </div>
      </div>
    </div>
  </main>
</template>
