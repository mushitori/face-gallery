<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import type { Photo } from '../../api/types'
import { api } from '../../api/client'
import PhotoLightbox from './PhotoLightbox.vue'

const props = defineProps<{
  personId: number
  rootPath?: string
}>()

const photos = ref<Photo[]>([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)
const pageSize = 60
const selected = ref<Photo | null>(null)

async function loadPage(p: number) {
  loading.value = true
  try {
    const res = await api.personPhotos(props.personId, p, pageSize)
    if (p === 1) {
      photos.value = res.items
    } else {
      photos.value = [...photos.value, ...res.items]
    }
    total.value = res.total
    page.value = p
  } finally {
    loading.value = false
  }
}

async function loadMore() {
  if (photos.value.length >= total.value || loading.value) return
  await loadPage(page.value + 1)
}

onMounted(() => void loadPage(1))
watch(
  () => props.personId,
  () => void loadPage(1),
)
</script>

<template>
  <div class="wrap">
    <p class="meta">{{ total }} photos</p>
    <div v-if="loading && !photos.length" class="loading">Loading photos…</div>
    <div v-else class="grid">
      <button
        v-for="photo in photos"
        :key="photo.id"
        type="button"
        class="cell"
        @click="selected = photo"
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
    <PhotoLightbox :photo="selected" :root-path="rootPath" @close="selected = null" />
  </div>
</template>

<style scoped>
.wrap {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.meta {
  color: var(--muted);
  font-size: 0.9rem;
}
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 0.5rem;
}
.cell {
  border: none;
  padding: 0;
  cursor: pointer;
  border-radius: 8px;
  overflow: hidden;
  background: var(--bg);
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
