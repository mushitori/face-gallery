<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import AppShell from '../components/layout/AppShell.vue'
import ActiveScanCard from '../components/scan/ActiveScanCard.vue'
import PendingScanList from '../components/scan/PendingScanList.vue'
import ScanHistoryTable from '../components/scan/ScanHistoryTable.vue'
import { useJobsStore } from '../stores/jobs'

const jobs = useJobsStore()
let timer: ReturnType<typeof setInterval> | null = null

onMounted(() => {
  void jobs.fetchDashboard()
  timer = setInterval(() => void jobs.fetchDashboard(), 2000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<template>
  <AppShell>
    <h1>Scan queue &amp; history</h1>
    <p v-if="jobs.error" class="error-text">{{ jobs.error }}</p>

    <section v-if="jobs.active" class="block">
      <h2 class="block-title">Active scan</h2>
      <ActiveScanCard :job="jobs.active" />
    </section>

    <div class="block">
      <PendingScanList :jobs="jobs.queue" />
    </div>

    <div class="block">
      <ScanHistoryTable :jobs="jobs.history" />
    </div>
  </AppShell>
</template>

<style scoped>
h1 {
  margin-bottom: 1.5rem;
}
.block {
  margin-bottom: 2rem;
}
.block-title {
  font-size: 1rem;
  margin: 0 0 0.75rem;
  color: var(--muted);
}
</style>
