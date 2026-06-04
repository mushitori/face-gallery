<script setup lang="ts">
import { computed } from 'vue'
import type { Job } from '../../api/types'
import {
  formatDurationMs,
  jobElapsedMs,
  libraryScanLabel,
  parseCurrentFile,
} from '../../utils/format'

const props = defineProps<{
  job: Job
  variant?: 'ring' | 'bar'
}>()

const percent = computed(() => Math.round(props.job.progress * 100))
const elapsed = computed(() => formatDurationMs(jobElapsedMs(props.job)))
const libraryName = computed(() =>
  libraryScanLabel(props.job.library_root_path, props.job.library_id),
)
const currentFile = computed(() => parseCurrentFile(props.job.message))
const useRing = computed(() => (props.variant ?? 'ring') === 'ring')
</script>

<template>
  <article class="card glass-panel">
    <div class="card-top">
      <h3>Library: {{ libraryName }}</h3>
      <span class="run-icon" aria-hidden="true" title="Scan running">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
          <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="1.5" />
          <path
            d="M12 7v5l3 2"
            stroke="currentColor"
            stroke-width="1.5"
            stroke-linecap="round"
          />
        </svg>
      </span>
    </div>

    <div v-if="useRing" class="layout-ring">
      <div class="ring-wrap">
        <div class="ring" :style="{ '--p': percent }">
          <div class="ring-inner">
            <span class="pct">{{ percent }}%</span>
          </div>
        </div>
        <span class="complete-label">Complete</span>
      </div>
      <div class="details">
        <p class="line">
          <span class="label">Time Elapsed:</span>
          {{ elapsed }}
        </p>
        <p v-if="currentFile" class="line file">
          <span class="label">Processing:</span>
          {{ currentFile }}
        </p>
        <p v-else-if="job.message" class="line file muted">{{ job.message }}</p>
      </div>
    </div>

    <div v-else class="layout-bar">
      <div class="bar-head">
        <span class="pct-inline">{{ percent }}% Complete</span>
      </div>
      <div class="linear">
        <div class="linear-fill" :style="{ width: `${percent}%` }" />
      </div>
      <div class="details compact">
        <p class="line">
          <span class="label">Time Elapsed:</span>
          {{ elapsed }}
        </p>
        <p v-if="currentFile" class="line file">
          <span class="label">Processing:</span>
          {{ currentFile }}
        </p>
      </div>
    </div>
  </article>
</template>

<style scoped>
.card {
  padding: 1.35rem 1.5rem;
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}
.card-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 1.15rem;
}
h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--text);
}
.run-icon {
  color: var(--accent-cyan);
  opacity: 0.85;
  flex-shrink: 0;
}
.layout-ring {
  display: flex;
  gap: 1.5rem;
  align-items: center;
}
.ring-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.35rem;
  flex-shrink: 0;
}
.ring {
  --p: 0;
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: conic-gradient(
    var(--accent-teal) calc(var(--p) * 1%),
    rgba(255, 255, 255, 0.06) 0
  );
  display: flex;
  align-items: center;
  justify-content: center;
}
.ring-inner {
  width: 76px;
  height: 76px;
  border-radius: 50%;
  background: rgba(10, 12, 20, 0.92);
  display: flex;
  align-items: center;
  justify-content: center;
}
.pct {
  font-weight: 700;
  font-size: 1.05rem;
  color: var(--text);
}
.complete-label {
  font-size: 0.75rem;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.details {
  flex: 1;
  min-width: 0;
}
.line {
  margin: 0 0 0.5rem;
  font-size: 0.9rem;
  color: var(--text-soft);
}
.line .label {
  color: var(--muted);
  margin-right: 0.35rem;
}
.line.file {
  color: var(--text);
  word-break: break-all;
}
.line.muted {
  font-size: 0.82rem;
  color: var(--muted);
}
.layout-bar .bar-head {
  margin-bottom: 0.5rem;
}
.pct-inline {
  font-weight: 600;
  font-size: 0.95rem;
}
.linear {
  height: 8px;
  background: rgba(0, 0, 0, 0.35);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 0.85rem;
}
.linear-fill {
  height: 100%;
  background: var(--gradient-primary);
  transition: width 0.3s ease;
  border-radius: 4px;
}
.details.compact {
  margin-top: 0;
}
</style>
