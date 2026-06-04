<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { RouterLink } from 'vue-router'
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
    <nav class="breadcrumb" aria-label="Breadcrumb">
      <RouterLink to="/">Home</RouterLink>
      <span class="sep" aria-hidden="true">&gt;</span>
      <span class="current">Scan queue &amp; history</span>
    </nav>

    <header class="page-header">
      <h1>Scan queue &amp; history</h1>
    </header>

    <p v-if="jobs.error" class="error-text">{{ jobs.error }}</p>

    <div class="queue-row">
      <div class="queue-col">
        <h2 class="section-label">Active scans</h2>
        <div class="panel-slot">
          <ActiveScanCard v-if="jobs.active" :job="jobs.active" variant="ring" />
          <div v-else class="empty-active glass-panel">
            <p>No scan running right now.</p>
          </div>
        </div>
      </div>

      <div class="queue-col pending-col">
        <h2 class="section-label">Pending scans</h2>
        <div class="panel-slot">
          <PendingScanList :jobs="jobs.queue" />
        </div>
      </div>
    </div>

    <ScanHistoryTable :jobs="jobs.history" />
  </AppShell>
</template>

<style scoped>
.breadcrumb {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  margin-bottom: 1rem;
  color: var(--muted);
}
.breadcrumb a {
  color: var(--muted);
  text-decoration: none;
}
.breadcrumb a:hover {
  color: var(--accent-teal);
}
.breadcrumb .sep {
  opacity: 0.5;
}
.breadcrumb .current {
  color: var(--text-soft);
}
.page-header {
  margin-bottom: 1.75rem;
}
.page-header h1 {
  margin: 0;
  font-size: 1.75rem;
  font-weight: 700;
  letter-spacing: -0.02em;
}
.queue-row {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 1.25rem;
  align-items: stretch;
  margin-bottom: 2rem;
}
.queue-col {
  display: flex;
  flex-direction: column;
  min-height: 220px;
  min-width: 0;
}
.pending-col {
  width: 100%;
  max-width: 380px;
}
.section-label {
  margin: 0 0 0.85rem;
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--text);
  flex-shrink: 0;
  line-height: 1.3;
}
.panel-slot {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}
.panel-slot :deep(.card),
.empty-active {
  flex: 1;
  min-height: 0;
}
.empty-active {
  padding: 2.5rem 1.5rem;
  text-align: center;
  color: var(--muted);
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  justify-content: center;
}
.empty-active p {
  margin: 0;
}
.pending-col .panel-slot {
  max-width: 380px;
  width: 100%;
}
.pending-col .panel-slot :deep(.panel) {
  max-width: 100%;
}
@media (max-width: 960px) {
  .queue-row {
    grid-template-columns: 1fr;
  }
  .pending-col {
    max-width: none;
  }
  .pending-col :deep(.panel) {
    max-width: none;
  }
}
</style>
