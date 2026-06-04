<script setup lang="ts">
import { onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import AppShell from '../components/layout/AppShell.vue'
import PersonThumbGrid from '../components/persons/PersonThumbGrid.vue'
import { usePersonsStore } from '../stores/persons'

const props = defineProps<{ libraryId: string }>()
const persons = usePersonsStore()
const route = useRoute()

function load() {
  const id = Number(props.libraryId)
  if (!Number.isNaN(id)) {
    void persons.fetchPersons(id)
  }
}

onMounted(load)
watch(() => route.params.libraryId, load)
</script>

<template>
  <AppShell>
    <h1>People</h1>
    <p class="hint">Library #{{ libraryId }} — select a person to view their photos.</p>
    <PersonThumbGrid :persons="persons.items" :loading="persons.loading" />
    <p v-if="persons.error" class="error">{{ persons.error }}</p>
  </AppShell>
</template>

<style scoped>
.hint {
  color: var(--muted);
  margin-bottom: 1rem;
}
.error {
  color: #f07178;
}
</style>
