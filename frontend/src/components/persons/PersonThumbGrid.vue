<script setup lang="ts">
import type { Person } from '../../api/types'
import PersonThumbCard from './PersonThumbCard.vue'

defineProps<{
  persons: Person[]
  loading?: boolean
}>()
</script>

<template>
  <div v-if="loading" class="loading">Loading people…</div>
  <div v-else-if="!persons.length" class="empty">No persons yet. Run a scan first.</div>
  <div v-else class="grid">
    <PersonThumbCard v-for="p in persons" :key="p.id" :person="p" />
  </div>
</template>

<style scoped>
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 1rem;
}
.loading,
.empty {
  color: var(--muted);
  padding: 2rem;
}
</style>
