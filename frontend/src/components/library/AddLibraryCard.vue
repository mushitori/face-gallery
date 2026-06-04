<script setup lang="ts">
import { ref } from 'vue'

const emit = defineEmits<{
  add: [path: string]
}>()

const manualPath = ref('')
const busy = ref(false)
const error = ref<string | null>(null)

async function pickFolder() {
  error.value = null
  try {
    const { open } = await import('@tauri-apps/plugin-dialog')
    const selected = await open({ directory: true, multiple: false })
    if (selected && typeof selected === 'string') {
      manualPath.value = selected
      await submit()
    }
  } catch {
    error.value =
      'Folder dialog unavailable. Enter a path below (browser dev mode).'
  }
}

async function submit() {
  const p = manualPath.value.trim()
  if (!p) return
  busy.value = true
  error.value = null
  try {
    emit('add', p)
  } catch (e) {
    error.value = e instanceof Error ? e.message : String(e)
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <section class="card">
    <h2>Add photo library</h2>
    <p class="hint">Choose a folder on disk. All scanning runs locally in Python.</p>
    <div class="actions">
      <button type="button" class="btn primary" :disabled="busy" @click="pickFolder">
        Choose folder…
      </button>
    </div>
    <label class="field">
      <span>Or enter path</span>
      <input v-model="manualPath" type="text" placeholder="D:\Photos" />
    </label>
    <button type="button" class="btn" :disabled="busy || !manualPath.trim()" @click="submit">
      Add library
    </button>
    <p v-if="error" class="error">{{ error }}</p>
  </section>
</template>

<style scoped>
.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1.25rem;
  max-width: 520px;
}
.hint {
  color: var(--muted);
  font-size: 0.9rem;
}
.actions {
  margin: 1rem 0;
}
.field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  margin-bottom: 0.75rem;
}
.field input {
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: var(--bg);
  color: var(--text);
}
.error {
  color: #f07178;
  font-size: 0.9rem;
}
</style>
