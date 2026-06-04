<script setup lang="ts">
import type { Photo } from '../../api/types'
import { api } from '../../api/client'

defineProps<{
  photo: Photo | null
  rootPath?: string
}>()

const emit = defineEmits<{ close: [] }>()
</script>

<template>
  <div v-if="photo" class="overlay" @click.self="emit('close')">
    <button type="button" class="close" @click="emit('close')">×</button>
    <img :src="api.photoThumbUrl(photo.id)" :alt="photo.path" />
    <p class="path">{{ rootPath ? `${rootPath}\\${photo.path}` : photo.path }}</p>
  </div>
</template>

<style scoped>
.overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.85);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 100;
  padding: 2rem;
}
img {
  max-width: 90vw;
  max-height: 75vh;
  object-fit: contain;
}
.path {
  margin-top: 1rem;
  color: #ccc;
  font-size: 0.85rem;
  word-break: break-all;
  text-align: center;
}
.close {
  position: absolute;
  top: 1rem;
  right: 1rem;
  font-size: 2rem;
  background: none;
  border: none;
  color: #fff;
  cursor: pointer;
}
</style>
