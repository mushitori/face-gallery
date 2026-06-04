<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppShell from '../components/layout/AppShell.vue'
import AddLibraryCard from '../components/library/AddLibraryCard.vue'
import LibraryActionBar from '../components/library/LibraryActionBar.vue'
import LibraryGrid from '../components/library/LibraryGrid.vue'
import ScanProgressPanel from '../components/scan/ScanProgressPanel.vue'
import { useApiHealth } from '../composables/useApi'
import { useScanProgress } from '../composables/useScanProgress'
import { ApiError } from '../api/client'
import { useJobsStore } from '../stores/jobs'
import { useLibraryStore } from '../stores/library'
import { useScanStore } from '../stores/scan'

const library = useLibraryStore()
const scan = useScanStore()
const jobs = useJobsStore()
const router = useRouter()
const { online } = useApiHealth()
const { isActive } = useScanProgress()

const selectedLib = computed(() => library.selected())
const actionsDisabled = computed(
  () => !online.value || selectedLib.value == null,
)
const scanBusy = computed(() => {
  const id = library.selectedId
  if (id == null) return false
  const st = jobs.libraryJobState(id)
  return st === 'queued' || st === 'running' || isActive.value
})

onMounted(async () => {
  await Promise.all([library.fetchLibraries(), jobs.fetchDashboard()])
})

async function onAdd(path: string) {
  const lib = await library.addLibrary(path)
  try {
    await scan.startScan(lib.id, false)
  } catch (e) {
    if (!(e instanceof ApiError)) throw e
  }
}

async function scanSelected(force = false) {
  const lib = library.selected()
  if (!lib) return
  try {
    await scan.startScan(lib.id, force)
  } catch {
    /* lastError set in store */
  }
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
    <div class="home-layout">
      <aside class="col-left">
        <AddLibraryCard @add="onAdd" />
        <ScanProgressPanel />
        <p v-if="scan.lastError" class="error-text">{{ scan.lastError }}</p>
        <p v-if="library.error" class="error-text">{{ library.error }}</p>
      </aside>

      <section v-if="library.libraries.length" class="col-right glass-panel-strong">
        <div class="libraries-head">
          <h2 class="section-title">Your Libraries</h2>
        </div>
        <div class="libraries-body">
          <LibraryGrid
            :libraries="library.libraries"
            :selected-id="library.selectedId"
            @select="library.selectedId = $event"
          />
        </div>
        <LibraryActionBar
          :disabled="actionsDisabled"
          :scan-busy="scanBusy"
          @scan-new="scanSelected(false)"
          @rescan-all="scanSelected(true)"
          @browse-people="openPersons"
        />
      </section>

      <section v-else class="col-right empty-panel glass-panel-strong">
        <p class="empty-libs">Add a photo library to get started.</p>
      </section>
    </div>
  </AppShell>
</template>

<style scoped>
.home-layout {
  display: grid;
  grid-template-columns: minmax(300px, 380px) 1fr;
  gap: 1.5rem;
  align-items: stretch;
}
.col-left {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.col-right {
  display: flex;
  flex-direction: column;
  min-height: 420px;
  overflow: hidden;
}
.libraries-head {
  padding: 1.35rem 1.5rem 0;
}
.section-title {
  margin: 0;
  font-size: 1.15rem;
  font-weight: 600;
}
.libraries-body {
  flex: 1;
  padding: 1rem 1.5rem 1.25rem;
  overflow-y: auto;
}
.empty-panel {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 320px;
}
.empty-libs {
  color: var(--muted);
  font-size: 0.95rem;
  margin: 0;
}
.col-left .error-text {
  padding: 0 0.25rem;
}
@media (max-width: 960px) {
  .home-layout {
    grid-template-columns: 1fr;
  }
  .col-right {
    min-height: auto;
  }
}
</style>
