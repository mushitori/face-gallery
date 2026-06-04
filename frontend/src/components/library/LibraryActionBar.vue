<script setup lang="ts">
defineProps<{
  disabled: boolean
  scanBusy: boolean
  showViewScans: boolean
}>()

const emit = defineEmits<{
  scanNew: []
  browsePeople: []
  viewScans: []
}>()
</script>

<template>
  <div class="bar">
    <button
      type="button"
      class="btn-outline-gradient"
      :disabled="disabled || scanBusy"
      @click="emit('scanNew')"
    >
      Rescan Selected
    </button>
    <button type="button" class="btn" :disabled="disabled" @click="emit('browsePeople')">
      Browse people
    </button>
    <button
      v-if="showViewScans"
      type="button"
      class="btn"
      @click="emit('viewScans')"
    >
      View In Scan History
    </button>
  </div>
</template>

<style scoped>
.bar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.85rem;
  padding: 1.15rem 1.35rem;
  margin-top: 0;
  border-top: 1px solid var(--glass-border);
  background: rgba(0, 0, 0, 0.15);
  border-radius: 0 0 18px 18px;
}
</style>
