<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import type { Photo } from '../../api/types'
import { api } from '../../api/client'
import PhotoLightbox from './PhotoLightbox.vue'

const props = defineProps<{
  personId: number
  rootPath?: string
}>()

const emit = defineEmits<{
  totalChange: [n: number]
}>()

const photos = ref<Photo[]>([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)
const pageSize = 60
const selectedIndex = ref<number | null>(null)

const selectedPhoto = computed(() =>
  selectedIndex.value != null ? (photos.value[selectedIndex.value] ?? null) : null,
)

function wrapIndex(index: number, count: number): number {
  return ((index % count) + count) % count
}

async function loadPage(p: number) {
  loading.value = true
  try {
    const res = await api.personPhotos(props.personId, p, pageSize)
    if (p === 1) {
      photos.value = res.items
      selectedIndex.value = null
    } else {
      photos.value = [...photos.value, ...res.items]
    }
    total.value = res.total
    page.value = p
    emit('totalChange', res.total)
  } finally {
    loading.value = false
  }
}

async function loadMore() {
  if (photos.value.length >= total.value || loading.value) return
  await loadPage(page.value + 1)
}

async function ensurePhotoLoaded(targetIndex: number): Promise<void> {
  while (photos.value.length <= targetIndex && photos.value.length < total.value) {
    await loadPage(page.value + 1)
  }
}

async function goToIndex(targetIndex: number): Promise<void> {
  if (total.value === 0) return
  const wrapped = wrapIndex(targetIndex, total.value)
  await ensurePhotoLoaded(wrapped)
  selectedIndex.value = wrapped
}

async function goPrev() {
  if (selectedIndex.value == null) return
  await goToIndex(selectedIndex.value - 1)
}

async function goNext() {
  if (selectedIndex.value == null) return
  await goToIndex(selectedIndex.value + 1)
}

function openAt(index: number) {
  selectedIndex.value = index
}

onMounted(() => void loadPage(1))
watch(
  () => props.personId,
  () => void loadPage(1),
)
</script>

<template>
  <div class="wrap">
    <div v-if="loading && !photos.length" class="loading">Loading photos…</div>
    <div v-else class="grid">
      <button
        v-for="(photo, index) in photos"
        :key="photo.id"
        type="button"
        class="cell"
        @click="openAt(index)"
      >
        <img :src="api.photoThumbUrl(photo.id)" :alt="photo.path" loading="lazy" />
      </button>
    </div>
    <button
      v-if="photos.length < total"
      type="button"
      class="btn"
      :disabled="loading"
      @click="loadMore"
    >
      {{ loading ? 'Loading…' : 'Load more' }}
    </button>
    <PhotoLightbox
      v-if="selectedIndex != null && selectedPhoto"
      :photo="selectedPhoto"
      :index="selectedIndex"
      :total="total"
      :root-path="rootPath"
      @close="selectedIndex = null"
      @prev="goPrev"
      @next="goNext"
    />
  </div>
</template>

<style scoped>
.wrap {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 0.65rem;
}
.cell {
  border: none;
  padding: 0;
  cursor: pointer;
  border-radius: 12px;
  overflow: hidden;
  background: var(--bg);
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.cell:hover {
  transform: scale(1.02);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.35);
}
.cell img {
  width: 100%;
  aspect-ratio: 1;
  object-fit: cover;
  display: block;
}
.loading {
  color: var(--muted);
  padding: 2rem;
}
</style>
