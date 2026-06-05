<script setup lang="ts">
import { onUnmounted } from 'vue'
import { RouterView } from 'vue-router'
import ApiOfflineOverlay from './components/layout/ApiOfflineOverlay.vue'
import { useApiHealthStore } from './stores/apiHealth'

const apiHealth = useApiHealthStore()
apiHealth.init()

onUnmounted(() => {
  apiHealth.stop()
})
</script>

<template>
  <ApiOfflineOverlay />
  <RouterView />
</template>
