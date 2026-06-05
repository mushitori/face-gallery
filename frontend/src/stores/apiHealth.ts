import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { pingHealth } from '../api/client'

const POLL_OFFLINE_MS = 1000
const POLL_ONLINE_MS = 5000
const RELOAD_DELAY_MS = 1500

export type ApiOverlayPhase = 'connecting' | 'offline' | 'recovered'

export const useApiHealthStore = defineStore('apiHealth', () => {
  const online = ref(false)
  const checking = ref(true)
  const overlayPhase = ref<ApiOverlayPhase>('connecting')
  const initialized = ref(false)

  let pollTimer: ReturnType<typeof setInterval> | null = null
  let reloadTimer: ReturnType<typeof setTimeout> | null = null

  const showOverlay = computed(
    () => !online.value || overlayPhase.value === 'recovered',
  )

  const overlayTitle = computed(() => {
    if (overlayPhase.value === 'recovered') {
      return 'Back online'
    }
    if (overlayPhase.value === 'connecting') {
      return 'Connecting…'
    }
    return 'API unavailable'
  })

  const overlayMessage = computed(() => {
    if (overlayPhase.value === 'recovered') {
      return 'The app is connected again. Refreshing your libraries and scans…'
    }
    if (overlayPhase.value === 'connecting') {
      return 'Starting Face Gallery and checking the local API.'
    }
    return "We can't reach the photo API right now. We'll keep checking every second until it's ready."
  })

  const overlayHint = computed(() => {
    if (overlayPhase.value === 'recovered') {
      return ''
    }
    return 'On first launch this can take a minute while face-recognition models download. If this screen stays open, try closing and reopening the app.'
  })

  function clearPollTimer() {
    if (pollTimer) {
      clearInterval(pollTimer)
      pollTimer = null
    }
  }

  function clearReloadTimer() {
    if (reloadTimer) {
      clearTimeout(reloadTimer)
      reloadTimer = null
    }
  }

  function schedulePoll(intervalMs: number) {
    clearPollTimer()
    pollTimer = setInterval(() => {
      void check()
    }, intervalMs)
  }

  function handleRecovered() {
    online.value = true
    overlayPhase.value = 'recovered'
    clearPollTimer()
    clearReloadTimer()
    reloadTimer = setTimeout(() => {
      window.location.reload()
    }, RELOAD_DELAY_MS)
  }

  async function check() {
    checking.value = true
    const ok = await pingHealth()

    if (ok) {
      if (!online.value && overlayPhase.value === 'offline') {
        handleRecovered()
      } else {
        online.value = true
        overlayPhase.value = 'connecting'
        clearPollTimer()
        schedulePoll(POLL_ONLINE_MS)
      }
    } else {
      online.value = false
      overlayPhase.value = 'offline'
      clearReloadTimer()
      schedulePoll(POLL_OFFLINE_MS)
    }

    checking.value = false
  }

  function init() {
    if (initialized.value) return
    initialized.value = true
    void check()
  }

  function stop() {
    clearPollTimer()
    clearReloadTimer()
  }

  return {
    online,
    checking,
    showOverlay,
    overlayPhase,
    overlayTitle,
    overlayMessage,
    overlayHint,
    initialized,
    init,
    stop,
    check,
  }
})
