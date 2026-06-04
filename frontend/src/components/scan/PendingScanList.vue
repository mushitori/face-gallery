<script setup lang="ts">
import type { Job } from '../../api/types'
import { libraryDisplayName } from '../../utils/format'

defineProps<{
  jobs: Job[]
}>()
</script>

<template>
  <section class="section">
    <h2>Pending scans</h2>
    <p v-if="!jobs.length" class="empty">No scans waiting in queue.</p>
    <ul v-else class="list">
      <li v-for="job in jobs" :key="job.id" class="item glass-panel">
        <span class="badge" aria-hidden="true">⏳</span>
        <div class="info">
          <span class="name">
            Library: {{ libraryDisplayName(job.library_root_path ?? '') }}
          </span>
          <span v-if="job.queue_position" class="pos">Position {{ job.queue_position }}</span>
        </div>
      </li>
    </ul>
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
  gap: 0.75rem;
  padding: 0.85rem 1rem;
}
.badge {
  font-size: 1.1rem;
}
.info {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}
.name {
  font-weight: 500;
  font-size: 0.9rem;
}
.pos {
  font-size: 0.8rem;
  color: var(--muted);
}
</style>
