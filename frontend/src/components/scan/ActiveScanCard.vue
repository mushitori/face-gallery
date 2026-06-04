<script setup lang="ts">
import { computed } from 'vue'
import type { Job } from '../../api/types'
import {
  formatDurationMs,
  jobElapsedMs,
  libraryDisplayName,
  parseCurrentFile,
} from '../../utils/format'

const props = defineProps<{
  job: Job
}>()

const percent = computed(() => Math.round(props.job.progress * 100))
const elapsed = computed(() => formatDurationMs(jobElapsedMs(props.job)))
const libraryName = computed(() =>
  libraryDisplayName(props.job.library_root_path ?? ''),
)
const currentFile = computed(() => parseCurrentFile(props.job.message))
</script>

<template>
  <article class="card glass-panel">
    <h3>Library: {{ libraryName }}</h3>
    <div class="row">
      <div class="ring" :style="{ '--p': percent }">
        <div class="ring-inner">
          <span class="ring-label">{{ percent }}%</span>
        </div>
      </div>
      <div class="details">
        <p class="status">{{ job.status }}</p>
        <p class="elapsed">Elapsed: {{ elapsed }}</p>
        <p v-if="currentFile" class="file">Processing: {{ currentFile }}</p>
        <p v-else-if="job.message" class="file">{{ job.message }}</p>
      </div>
    </div>
    <div class="linear">
      <div class="linear-fill" :style="{ width: `${percent}%` }" />
    </div>
  </article>
</template>

<style scoped>
.card {
  padding: 1.25rem;
}
h3 {
  margin: 0 0 1rem;
  font-size: 1rem;
}
.row {
  display: flex;
  gap: 1.25rem;
  align-items: center;
}
.ring {
  --p: 0;
  width: 88px;
  height: 88px;
  border-radius: 50%;
  background: conic-gradient(
    var(--accent-teal) calc(var(--p) * 1%),
    rgba(255, 255, 255, 0.08) 0
  );
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.ring-inner {
  width: 68px;
  height: 68px;
  border-radius: 50%;
  background: rgba(13, 14, 20, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
}
.ring-label {
  font-weight: 700;
  font-size: 0.95rem;
}
.details {
  flex: 1;
  min-width: 0;
}
.status {
  text-transform: capitalize;
  margin: 0;
  font-weight: 600;
}
.elapsed,
.file {
  margin: 0.35rem 0 0;
  font-size: 0.85rem;
  color: var(--muted);
}
.file {
  color: var(--text);
  word-break: break-all;
}
.linear {
  height: 6px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 3px;
  margin-top: 1rem;
  overflow: hidden;
}
.linear-fill {
  height: 100%;
  background: var(--gradient-primary);
  transition: width 0.3s ease;
}
</style>
