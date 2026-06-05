<script setup lang="ts">
import type { Job } from '../../api/types'
import {
  formatDurationMs,
  formatApiDateTime,
  jobElapsedMs,
  libraryScanLabel,
  parseJobStats,
} from '../../utils/format'

defineProps<{
  jobs: Job[]
  disabled?: boolean
}>()

const emit = defineEmits<{
  retry: [jobId: number]
}>()
</script>

<template>
  <section class="section">
    <h2>Scan history</h2>
    <p v-if="!jobs.length" class="empty glass-panel">No completed scans yet.</p>
    <div v-else class="table-wrap glass-panel-strong">
      <table>
        <thead>
          <tr>
            <th>Date &amp; time</th>
            <th>Library</th>
            <th>Status</th>
            <th>Total faces found</th>
            <th>New persons created</th>
            <th>Duration</th>
            <th />
          </tr>
        </thead>
        <tbody>
          <tr v-for="job in jobs" :key="job.id">
            <td class="date">{{ formatApiDateTime(job.created_at) }}</td>
            <td>{{ libraryScanLabel(job.library_root_path, job.library_id) }}</td>
            <td>
              <span v-if="job.status === 'done'" class="status done">
                <span class="status-dot" aria-hidden="true" />
                Completed
              </span>
              <span v-else-if="job.status === 'cancelled'" class="status cancelled">
                <span class="status-dot cancelled-dot" aria-hidden="true" />
                Cancelled
              </span>
              <span v-else class="status failed">
                <span class="status-dot failed-dot" aria-hidden="true" />
                Failed
              </span>
            </td>
            <td class="num">
              {{
                parseJobStats(job.message).faces != null
                  ? `${parseJobStats(job.message).faces} faces`
                  : '—'
              }}
            </td>
            <td class="num">
              {{
                parseJobStats(job.message).persons != null
                  ? `${parseJobStats(job.message).persons} new`
                  : '—'
              }}
            </td>
            <td class="duration">{{ formatDurationMs(jobElapsedMs(job)) }}</td>
            <td class="actions">
              <button
                v-if="job.status === 'cancelled' || job.status === 'failed'"
                type="button"
                class="btn btn-sm"
                :disabled="disabled"
                @click="emit('retry', job.id)"
              >
                Start scan again
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<style scoped>
.section h2 {
  margin: 0 0 1rem;
  font-size: 1.15rem;
  font-weight: 600;
}
.empty {
  padding: 2rem;
  text-align: center;
  color: var(--muted);
  font-size: 0.9rem;
  border-radius: 16px;
}
.table-wrap {
  overflow-x: auto;
  border-radius: 18px;
}
table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.88rem;
}
thead {
  background: rgba(0, 0, 0, 0.2);
}
th {
  padding: 0.85rem 1.15rem;
  text-align: left;
  font-weight: 500;
  color: var(--muted);
  font-size: 0.8rem;
  text-transform: capitalize;
  border-bottom: 1px solid var(--glass-border);
}
td {
  padding: 0.9rem 1.15rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  color: var(--text-soft);
  vertical-align: middle;
}
tbody tr:last-child td {
  border-bottom: none;
}
tbody tr:hover {
  background: rgba(255, 255, 255, 0.02);
}
.date,
.duration {
  white-space: nowrap;
}
.actions {
  white-space: nowrap;
}
.btn-sm {
  padding: 0.35rem 0.75rem;
  font-size: 0.78rem;
}
.num {
  color: var(--text);
  font-weight: 500;
}
.status {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500;
}
.status.done {
  color: var(--status-online);
}
.status.failed {
  color: var(--danger);
}
.status.cancelled {
  color: #fb923c;
}
.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--status-online);
  box-shadow: 0 0 8px rgba(74, 222, 128, 0.5);
  flex-shrink: 0;
}
.status-dot.failed-dot {
  background: var(--danger);
  box-shadow: none;
}
.status-dot.cancelled-dot {
  background: #fb923c;
  box-shadow: none;
}
</style>
