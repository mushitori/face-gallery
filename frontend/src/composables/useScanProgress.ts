import { computed } from 'vue'
import { useScanStore } from '../stores/scan'

export function useScanProgress() {
  const scan = useScanStore()
  const progressPercent = computed(() =>
    Math.round((scan.job?.progress ?? 0) * 100),
  )
  const isActive = computed(
    () =>
      scan.polling ||
      (scan.job != null &&
        scan.job.status !== 'done' &&
        scan.job.status !== 'failed'),
  )
  return { scan, progressPercent, isActive }
}
