import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { api } from '../api/client'
import type { Job } from '../api/types'

export type LibraryJobState = 'idle' | 'queued' | 'running'

export const useJobsStore = defineStore('jobs', () => {
  const active = ref<Job | null>(null)
  const queue = ref<Job[]>([])
  const history = ref<Job[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const libraryJobMap = computed(() => {
    const map = new Map<number, LibraryJobState>()
    if (active.value) {
      map.set(active.value.library_id, 'running')
    }
    for (const j of queue.value) {
      if (!map.has(j.library_id)) {
        map.set(j.library_id, 'queued')
      }
    }
    return map
  })

  function libraryJobState(libraryId: number): LibraryJobState {
    return libraryJobMap.value.get(libraryId) ?? 'idle'
  }

  async function fetchDashboard() {
    loading.value = true
    error.value = null
    try {
      const data = await api.getJobsDashboard()
      active.value = data.active
      queue.value = data.queue
      history.value = data.history
    } catch (e) {
      error.value = e instanceof Error ? e.message : String(e)
    } finally {
      loading.value = false
    }
  }

  return {
    active,
    queue,
    history,
    loading,
    error,
    libraryJobState,
    fetchDashboard,
  }
})
