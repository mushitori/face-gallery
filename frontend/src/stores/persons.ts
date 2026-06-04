import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '../api/client'
import type { Person } from '../api/types'

export const usePersonsStore = defineStore('persons', () => {
  const items = ref<Person[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchPersons(libraryId?: number) {
    loading.value = true
    error.value = null
    try {
      const res = await api.listPersons(libraryId)
      items.value = res.items
    } catch (e) {
      error.value = e instanceof Error ? e.message : String(e)
    } finally {
      loading.value = false
    }
  }

  return { items, loading, error, fetchPersons }
})
