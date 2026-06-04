<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import AppShell from '../components/layout/AppShell.vue'
import PhotoVirtualGrid from '../components/photos/PhotoVirtualGrid.vue'
import { api } from '../api/client'
import type { Person } from '../api/types'

const props = defineProps<{ personId: string }>()
const person = ref<Person | null>(null)
const rootPath = ref<string | undefined>()

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
    <RouterLink to="/" class="back">← Back</RouterLink>
    <h1>{{ person?.display_name ?? `Person ${personId}` }}</h1>
    <PhotoVirtualGrid
      v-if="!Number.isNaN(Number(personId))"
      :person-id="Number(personId)"
      :root-path="rootPath"
    />
  </AppShell>
</template>

<style scoped>
.back {
  color: var(--accent);
  text-decoration: none;
  font-size: 0.9rem;
}
h1 {
  margin: 0.5rem 0 1rem;
}
</style>
