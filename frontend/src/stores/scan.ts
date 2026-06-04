import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '../api/client'
import type { Job } from '../api/types'

export const useScanStore = defineStore('scan', () => {
  const activeJobId = ref<number | null>(null)
  const job = ref<Job | null>(null)
  const polling = ref(false)
  let timer: ReturnType<typeof setInterval> | null = null

  function stopPolling() {
    if (timer) {
      clearInterval(timer)
      timer = null
    }
    polling.value = false
  }

  async function pollOnce() {
    if (activeJobId.value == null) return
    job.value = await api.getJob(activeJobId.value)
    if (job.value.status === 'done' || job.value.status === 'failed') {
      stopPolling()
    }
  }

  function startPolling(jobId: number) {
    activeJobId.value = jobId
    stopPolling()
    polling.value = true
    void pollOnce()
    timer = setInterval(() => void pollOnce(), 1000)
  }

  async function startScan(libraryId: number, force = false) {
    const { job_id } = await api.startScan(libraryId, force)
    startPolling(job_id)
    return job_id
  }

  return {
    activeJobId,
    job,
    polling,
    startScan,
    stopPolling,
    pollOnce,
  }
})
