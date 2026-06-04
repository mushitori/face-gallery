<script setup lang="ts">
import { RouterLink } from 'vue-router'
import type { Person } from '../../api/types'
import { api } from '../../api/client'

defineProps<{
  person: Person
}>()
</script>

<template>
  <RouterLink
    :to="{ name: 'person-photos', params: { personId: person.id } }"
    class="card"
  >
    <img
      :src="api.personThumbUrl(person.id)"
      :alt="person.display_name ?? `Person ${person.id}`"
      loading="lazy"
    />
    <div class="info">
      <span class="name">{{ person.display_name ?? `Person ${person.id}` }}</span>
      <span class="count">{{ person.photo_count }} photos</span>
    </div>
  </RouterLink>
</template>

<style scoped>
.card {
  display: flex;
  flex-direction: column;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  overflow: hidden;
  text-decoration: none;
  color: inherit;
  transition: border-color 0.15s;
}
.card:hover {
  border-color: var(--accent);
}
img {
  width: 100%;
  aspect-ratio: 1;
  object-fit: cover;
  background: var(--bg);
}
.info {
  padding: 0.5rem 0.65rem;
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}
.name {
  font-size: 0.9rem;
  font-weight: 600;
}
.count {
  font-size: 0.8rem;
  color: var(--muted);
}
</style>
