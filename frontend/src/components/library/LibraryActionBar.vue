<script setup lang="ts">
defineProps<{
  disabled: boolean
  scanBusy: boolean
}>()

const emit = defineEmits<{
  scanNew: []
  rescanAll: []
  browsePeople: []
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
      Scan new/changed
    </button>
    <button type="button" class="btn" :disabled="disabled || scanBusy" @click="emit('rescanAll')">
      Rescan all
    </button>
    <button type="button" class="btn" :disabled="disabled" @click="emit('browsePeople')">
      Browse people
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
