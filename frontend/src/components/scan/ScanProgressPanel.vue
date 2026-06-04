<script setup lang="ts">
import { computed } from 'vue'
import { useScanProgress } from '../../composables/useScanProgress'

const { scan, progressPercent, isActive } = useScanProgress()

const queueHint = computed(() => {
  const j = scan.job
  if (!j || j.status !== 'queued') return null
  if (j.queue_position != null) {
    return `Queued — position ${j.queue_position} in line`
  }
  return 'Queued — waiting for worker'
})
</script>

<template>
  <section v-if="scan.job || isActive" class="panel glass-panel">
    <h3>Scan progress</h3>
    <p v-if="queueHint" class="queue-hint">{{ queueHint }}</p>
    <div class="bar">
      <div class="fill" :style="{ width: `${progressPercent}%` }" />
    </div>
    <p class="meta">
      <strong>{{ scan.job?.status ?? '…' }}</strong>
      — {{ progressPercent }}%
    </p>
    <p v-if="scan.job?.message" class="message">{{ scan.job.message }}</p>
  </section>
</template>

<style scoped>
.panel {
  padding: 1rem 1.15rem;
}
h3 {
  margin: 0 0 0.65rem;
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-soft);
}
.queue-hint {
  font-size: 0.85rem;
  color: var(--accent-teal);
  margin: 0 0 0.5rem;
}
.bar {
  height: 8px;
  background: rgba(0, 0, 0, 0.35);
  border-radius: 4px;
  overflow: hidden;
  margin: 0.5rem 0;
}
.fill {
  height: 100%;
  background: var(--gradient-primary);
  transition: width 0.3s ease;
  border-radius: 4px;
}
.meta {
  font-size: 0.88rem;
  color: var(--muted);
  margin: 0;
}
.message {
  font-size: 0.82rem;
  color: var(--text-soft);
  word-break: break-word;
  margin: 0.35rem 0 0;
}
</style>
