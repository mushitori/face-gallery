import { defineStore } from 'pinia'
import { ref } from 'vue'
import { ApiError, api } from '../api/client'
import { useJobsStore } from './jobs'

export const useScanStore = defineStore('scan', () => {
  const lastError = ref<string | null>(null)

  async function startScan(libraryId: number, force = false) {
    lastError.value = null
    try {
      const { job_id } = await api.startScan(libraryId, force)
      const jobs = useJobsStore()
      await jobs.fetchDashboard()
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
    lastError,
    startScan,
  }
})
