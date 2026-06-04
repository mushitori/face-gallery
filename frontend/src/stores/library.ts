import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '../api/client'
import type { Library } from '../api/types'

export const useLibraryStore = defineStore('library', () => {
  const libraries = ref<Library[]>([])
  const selectedId = ref<number | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchLibraries() {
    loading.value = true
    error.value = null
    try {
      libraries.value = await api.listLibraries()
      if (selectedId.value == null && libraries.value.length) {
        selectedId.value = libraries.value[0].id
      }
    } catch (e) {
      error.value = e instanceof Error ? e.message : String(e)
    } finally {
      loading.value = false
    }
  }

  async function addLibrary(rootPath: string) {
    const lib = await api.createLibrary(rootPath)
    console.log('[FaceGallery] addLibrary', { rootPath, lib })
    await fetchLibraries()
    selectedId.value = lib.id
    return lib
  }

  const selected = () =>
    libraries.value.find((l) => l.id === selectedId.value) ?? null

  return {
    libraries,
    selectedId,
    loading,
    error,
    fetchLibraries,
    addLibrary,
    selected,
  }
})
