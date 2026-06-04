<script setup lang="ts">
import type { Job } from '../../api/types'
import { libraryScanLabel } from '../../utils/format'

defineProps<{
  jobs: Job[]
}>()
</script>

<template>
  <div class="panel glass-panel-strong">
    <div class="panel-body">
      <p v-if="!jobs.length" class="empty">No scans waiting in queue.</p>
      <ul v-else class="list">
        <li v-for="job in jobs" :key="job.id" class="item">
          <span class="warn-icon" aria-hidden="true">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
              <circle
                cx="12"
                cy="12"
                r="10"
                fill="rgba(251, 146, 60, 0.2)"
                stroke="#fb923c"
                stroke-width="1.5"
              />
              <path
                d="M12 8v5M12 16h.01"
                stroke="#fb923c"
                stroke-width="2"
                stroke-linecap="round"
              />
            </svg>
          </span>
          <span class="name">
            Library: {{ libraryScanLabel(job.library_root_path, job.library_id) }}
            <template v-if="job.queue_position">
              (position {{ job.queue_position }})
            </template>
          </span>
        </li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.panel {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  width: 100%;
  overflow: hidden;
}
.panel-body {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 1.25rem 1.35rem;
  scrollbar-gutter: stable;
}
.panel-body::-webkit-scrollbar {
  width: 6px;
}
.panel-body::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.15);
  border-radius: 3px;
}
.empty {
  color: var(--muted);
  font-size: 0.9rem;
  margin: 0;
}
.list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}
.item {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  padding: 0.9rem 1.1rem;
  border-radius: 999px;
  background: rgba(0, 0, 0, 0.25);
  border: 1px solid var(--glass-border);
  flex-shrink: 0;
}
.warn-icon {
  flex-shrink: 0;
  display: flex;
}
.name {
  font-weight: 500;
  font-size: 0.88rem;
  color: var(--text-soft);
  line-height: 1.35;
  min-width: 0;
  word-break: break-word;
}
</style>
