import { storeToRefs } from 'pinia'
import { useApiHealthStore } from '../stores/apiHealth'

/** Shared API health state (Pinia). Call init() once from App.vue. */
export function useApiHealth() {
  const store = useApiHealthStore()
  const { online, checking } = storeToRefs(store)
  return { online, checking, check: store.check }
}
