import { onMounted, ref } from 'vue'
import { api } from '../api/client'

export function useApiHealth() {
  const online = ref(false)
  const checking = ref(true)

  async function check() {
    checking.value = true
    try {
      await api.health()
      online.value = true
    } catch {
      online.value = false
    } finally {
      checking.value = false
    }
  }

  onMounted(() => void check())

  return { online, checking, check }
}
