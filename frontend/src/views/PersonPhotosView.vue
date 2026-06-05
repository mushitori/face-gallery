<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import AppShell from '../components/layout/AppShell.vue'
import PhotoVirtualGrid from '../components/photos/PhotoVirtualGrid.vue'
import { api } from '../api/client'
import type { Person } from '../api/types'

const props = defineProps<{ personId: string }>()
const person = ref<Person | null>(null)
const rootPath = ref<string | undefined>()
const photoTotal = ref(0)

const peopleLink = computed(() =>
  person.value
    ? { name: 'persons' as const, params: { libraryId: String(person.value.library_id) } }
    : null,
)

const title = computed(
  () => person.value?.display_name ?? `Person ${props.personId}`,
)

onMounted(async () => {
  const id = Number(props.personId)
  const res = await api.listPersons()
  person.value = res.items.find((p) => p.id === id) ?? null
  if (person.value) {
    const libs = await api.listLibraries()
    rootPath.value = libs.find((l) => l.id === person.value!.library_id)?.root_path
  }
})
</script>

<template>
  <AppShell>
    <RouterLink v-if="peopleLink" :to="peopleLink" class="back">
      ← Back to People
    </RouterLink>
    <span v-else class="back muted">← Back to People</span>

    <header class="page-header">
      <h1>{{ title }}</h1>
      <p v-if="photoTotal > 0" class="subtitle">{{ photoTotal }} photos</p>
    </header>

    <PhotoVirtualGrid
      v-if="!Number.isNaN(Number(personId))"
      :person-id="Number(personId)"
      :root-path="rootPath"
      @total-change="photoTotal = $event"
    />
  </AppShell>
</template>

<style scoped>
.back {
  display: inline-block;
  color: var(--accent-teal);
  text-decoration: none;
  font-size: 0.9rem;
  margin-bottom: 1rem;
}
.back:hover {
  color: var(--accent-cyan);
}
.back.muted {
  color: var(--muted);
  pointer-events: none;
}
.page-header {
  margin-bottom: 1.25rem;
}
.page-header h1 {
  margin: 0;
  font-size: 1.75rem;
  font-weight: 700;
  letter-spacing: -0.02em;
}
.subtitle {
  margin: 0.35rem 0 0;
  color: var(--muted);
  font-size: 0.95rem;
}
</style>
