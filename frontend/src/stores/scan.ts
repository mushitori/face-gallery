import { defineStore } from 'pinia'
import { ref } from 'vue'
import { ApiError, api } from '../api/client'
import { useJobsStore } from './jobs'
import { useLibraryStore } from './library'
import type { Job } from '../api/types'

function isValidJobId(jobId: number): boolean {
  return Number.isFinite(jobId) && jobId > 0
}

const TERMINAL = new Set(['done', 'failed'])

export const useScanStore = defineStore('scan', () => {
  const activeJobId = ref<number | null>(null)
  const job = ref<Job | null>(null)
  const polling = ref(false)
  const lastError = ref<string | null>(null)
  let timer: ReturnType<typeof setInterval> | null = null

  function stopPolling() {
    if (timer) {
      clearInterval(timer)
      timer = null
    }
    polling.value = false
  }

  async function pollOnce() {
    const id = activeJobId.value
    if (id == null || !isValidJobId(id)) return
    try {
      job.value = await api.getJob(id)
      if (job.value && TERMINAL.has(job.value.status)) {
        stopPolling()
        const library = useLibraryStore()
        const jobs = useJobsStore()
        await library.fetchLibraries()
        await jobs.fetchDashboard()
      }
    } catch (e) {
      console.warn('[FaceGallery] pollOnce failed', { jobId: id, error: e })
      stopPolling()
    }
  }

  function startPolling(jobId: number) {
    if (!isValidJobId(jobId)) {
      stopPolling()
      activeJobId.value = null
      job.value = null
      return
    }
    activeJobId.value = jobId
    stopPolling()
    polling.value = true
    void pollOnce()
    timer = setInterval(() => void pollOnce(), 1000)
  }

  async function startScan(libraryId: number, force = false) {
    lastError.value = null
    try {
      const { job_id } = await api.startScan(libraryId, force)
      const jobs = useJobsStore()
      await jobs.fetchDashboard()
      startPolling(job_id)
      return job_id
    } catch (e) {
      if (e instanceof ApiError && e.status === 409) {
        lastError.value = e.message
      } else {
        lastError.value = e instanceof Error ? e.message : String(e)
      }
      throw e
    }
  }

  return {
    activeJobId,
    job,
    polling,
    lastError,
    startScan,
    stopPolling,
    pollOnce,
  }
})
