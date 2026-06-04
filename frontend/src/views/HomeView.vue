<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppShell from '../components/layout/AppShell.vue'
import AddLibraryCard from '../components/library/AddLibraryCard.vue'
import ScanProgressPanel from '../components/scan/ScanProgressPanel.vue'
import { useLibraryStore } from '../stores/library'
import { useScanStore } from '../stores/scan'

const library = useLibraryStore()
const scan = useScanStore()
const router = useRouter()

onMounted(() => void library.fetchLibraries())

async function onAdd(path: string) {
  const lib = await library.addLibrary(path)
  await scan.startScan(lib.id)
}

async function scanSelected() {
  const lib = library.selected()
  if (!lib) return
  await scan.startScan(lib.id)
}

function openPersons() {
  const id = library.selectedId
  if (id != null) {
    router.push({ name: 'persons', params: { libraryId: id } })
  }
}
</script>

<template>
  <AppShell>
    <h1>Photo libraries</h1>
    <AddLibraryCard @add="onAdd" />
    <ScanProgressPanel />

    <section v-if="library.libraries.length" class="libs">
      <h2>Your libraries</h2>
      <ul>
        <li v-for="lib in library.libraries" :key="lib.id">
          <label>
            <input v-model="library.selectedId" type="radio" :value="lib.id" />
            {{ lib.root_path }}
          </label>
        </li>
      </ul>
      <div class="actions">
        <button type="button" class="btn primary" @click="scanSelected">Scan selected</button>
        <button type="button" class="btn" @click="openPersons">Browse people</button>
      </div>
    </section>
    <p v-if="library.error" class="error">{{ library.error }}</p>
  </AppShell>
</template>

<style scoped>
h1 {
  margin-bottom: 1rem;
}
.libs {
  margin-top: 2rem;
}
.libs ul {
  list-style: none;
  padding: 0;
}
.libs li {
  padding: 0.35rem 0;
}
.actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 1rem;
}
.error {
  color: #f07178;
}
</style>
