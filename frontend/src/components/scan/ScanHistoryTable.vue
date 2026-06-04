<script setup lang="ts">
import type { Job } from '../../api/types'
import {
  formatDurationMs,
  jobElapsedMs,
  libraryDisplayName,
  parseJobSummary,
} from '../../utils/format'

defineProps<{
  jobs: Job[]
}>()

function formatDate(iso: string | null): string {
  if (!iso) return '—'
  const normalized = iso.includes('T') ? iso : iso.replace(' ', 'T')
  const d = new Date(normalized.endsWith('Z') ? normalized : `${normalized}Z`)
  if (Number.isNaN(d.getTime())) return iso
  return d.toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}
</script>

<template>
  <section class="section">
    <h2>Scan history</h2>
    <p v-if="!jobs.length" class="empty">No completed scans yet.</p>
    <div v-else class="table-wrap glass-panel">
      <table>
        <thead>
          <tr>
            <th>Date & time</th>
            <th>Library</th>
            <th>Status</th>
            <th>Duration</th>
            <th>Summary</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="job in jobs" :key="job.id">
            <td>{{ formatDate(job.created_at) }}</td>
            <td>{{ libraryDisplayName(job.library_root_path ?? '') }}</td>
            <td>
              <span class="status" :class="job.status">
                {{ job.status === 'done' ? '✓ Completed' : '✗ Failed' }}
              </span>
            </td>
            <td>{{ formatDurationMs(jobElapsedMs(job)) }}</td>
            <td class="summary">{{ parseJobSummary(job.message) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<style scoped>
.section h2 {
  margin-bottom: 0.75rem;
}
.empty {
  color: var(--muted);
  font-size: 0.9rem;
}
.table-wrap {
  overflow-x: auto;
  padding: 0;
}
table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
}
th,
td {
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid var(--glass-border);
}
th {
  color: var(--muted);
  font-weight: 500;
}
.status.done {
  color: var(--status-online);
}
.status.failed {
  color: var(--danger);
}
.summary {
  max-width: 280px;
  word-break: break-word;
  color: var(--muted);
}
</style>
