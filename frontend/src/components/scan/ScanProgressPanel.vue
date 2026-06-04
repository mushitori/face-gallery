<script setup lang="ts">
import { useScanProgress } from '../../composables/useScanProgress'

const { scan, progressPercent, isActive } = useScanProgress()
</script>

<template>
  <section v-if="scan.job || isActive" class="panel">
    <h3>Scan progress</h3>
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
  margin-top: 1rem;
  padding: 1rem;
  border-radius: 12px;
  border: 1px solid var(--border);
  background: var(--surface);
  max-width: 520px;
}
.bar {
  height: 8px;
  background: var(--bg);
  border-radius: 4px;
  overflow: hidden;
  margin: 0.5rem 0;
}
.fill {
  height: 100%;
  background: var(--accent);
  transition: width 0.3s ease;
}
.meta {
  font-size: 0.9rem;
  color: var(--muted);
}
.message {
  font-size: 0.85rem;
  color: var(--text);
  word-break: break-word;
}
</style>
