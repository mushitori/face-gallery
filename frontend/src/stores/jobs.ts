import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { ApiError, api } from '../api/client'
import type { Job } from '../api/types'

export type LibraryJobState = 'idle' | 'queued' | 'paused' | 'running'

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
        map.set(j.library_id, j.status === 'paused' ? 'paused' : 'queued')
      }
    }
    return map
  })

  function libraryJobState(libraryId: number): LibraryJobState {
    return libraryJobMap.value.get(libraryId) ?? 'idle'
  }

  function libraryHasInFlightJob(libraryId: number): boolean {
    const st = libraryJobState(libraryId)
    return st === 'running' || st === 'queued' || st === 'paused'
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

  async function runJobAction(action: (jobId: number) => Promise<void>, jobId: number) {
    error.value = null
    try {
      await action(jobId)
      await fetchDashboard()
    } catch (e) {
      error.value = e instanceof ApiError ? e.message : e instanceof Error ? e.message : String(e)
      throw e
    }
  }

  function pauseJob(jobId: number) {
    return runJobAction(api.pauseJob, jobId)
  }

  function cancelJob(jobId: number) {
    return runJobAction(api.cancelJob, jobId)
  }

  function resumeJob(jobId: number) {
    return runJobAction(api.resumeJob, jobId)
  }

  function retryJob(jobId: number) {
    return runJobAction(api.retryJob, jobId)
  }

  return {
    active,
    queue,
    history,
    loading,
    error,
    libraryJobState,
    libraryHasInFlightJob,
    fetchDashboard,
    pauseJob,
    cancelJob,
    resumeJob,
    retryJob,
  }
})
