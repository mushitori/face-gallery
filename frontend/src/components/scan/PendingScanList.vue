<script setup lang="ts">
import type { Job } from '../../api/types'
import { libraryScanLabel, pendingScanDetail } from '../../utils/format'

defineProps<{
  jobs: Job[]
  disabled?: boolean
}>()

const emit = defineEmits<{
  cancel: [jobId: number]
  resume: [jobId: number]
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
          <div class="content">
            <span class="name">
              Library: {{ libraryScanLabel(job.library_root_path, job.library_id) }}
              <span v-if="pendingScanDetail(job)" class="detail">
                {{ pendingScanDetail(job) }}
              </span>
            </span>
            <div class="actions">
              <button
                v-if="job.status === 'paused'"
                type="button"
                class="btn btn-sm"
                :disabled="disabled"
                @click="emit('resume', job.id)"
              >
                Resume
              </button>
              <button
                type="button"
                class="btn btn-sm btn-danger"
                :disabled="disabled"
                @click="emit('cancel', job.id)"
              >
                Cancel
              </button>
            </div>
          </div>
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
  align-items: flex-start;
  gap: 0.85rem;
  padding: 0.9rem 1.1rem;
  border-radius: 16px;
  background: rgba(0, 0, 0, 0.25);
  border: 1px solid var(--glass-border);
  flex-shrink: 0;
}
.warn-icon {
  flex-shrink: 0;
  display: flex;
  margin-top: 0.1rem;
}
.content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}
.name {
  font-weight: 500;
  font-size: 0.88rem;
  color: var(--text-soft);
  line-height: 1.35;
  word-break: break-word;
}
.detail {
  display: block;
  margin-top: 0.2rem;
  color: var(--accent-teal);
  font-weight: 600;
}
.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}
.btn-sm {
  padding: 0.35rem 0.75rem;
  font-size: 0.78rem;
}
.btn-danger {
  border-color: rgba(248, 113, 113, 0.35);
  color: var(--danger);
}
.btn-danger:hover:not(:disabled) {
  background: rgba(248, 113, 113, 0.12);
}
</style>
