<script setup lang="ts">
import type { Library } from '../../api/types'
import LibraryCard from './LibraryCard.vue'

defineProps<{
  libraries: Library[]
  selectedId: number | null
}>()

const emit = defineEmits<{
  select: [id: number]
}>()
</script>

<template>
  <div class="grid">
    <LibraryCard
      v-for="lib in libraries"
      :key="lib.id"
      :library="lib"
      :selected="lib.id === selectedId"
      @select="emit('select', lib.id)"
    />
  </div>
</template>

<style scoped>
.grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}
/* Mock: last card spans full width when odd count */
.grid > :last-child:nth-child(odd):not(:only-child) {
  grid-column: 1 / -1;
}
@media (max-width: 900px) {
  .grid {
    grid-template-columns: 1fr;
  }
  .grid > :last-child:nth-child(odd):not(:only-child) {
    grid-column: auto;
  }
}
</style>
