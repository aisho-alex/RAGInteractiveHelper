<script setup>
import { ref } from 'vue'
import QueryForm from './components/QueryForm.vue'
import DocumentViewer from './components/DocumentViewer.vue'
import DocumentUpload from './components/DocumentUpload.vue'

const highlightedChunks = ref([])
const documentKey = ref(0)

function handleHighlightChunks(chunks) {
  highlightedChunks.value = chunks
}

function handleDocumentLoaded() {
  // Перезагрузка документа для обновления viewer
  documentKey.value++
}
</script>

<template>
  <main class="min-h-screen p-8">
    <div class="max-w-6xl mx-auto">
      <h1 class="text-3xl font-bold text-center mb-8 text-gray-800">
        RAG Interactive Helper
      </h1>
      <p class="text-center text-gray-600 mb-8">
        Универсальная система для работы с документами (PDF, TXT, MD)
      </p>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="space-y-6">
          <DocumentUpload @document-loaded="handleDocumentLoaded" />
          <QueryForm @highlight-chunks="handleHighlightChunks" />
        </div>

        <div>
          <DocumentViewer :key="documentKey" :highlighted-chunks="highlightedChunks" />
        </div>
      </div>
    </div>
  </main>
</template>
