<script setup lang="ts">
import { ref } from 'vue'

const emit = defineEmits<{
  add: [path: string]
}>()

const manualPath = ref('')
const busy = ref(false)
const error = ref<string | null>(null)

function clearSelection() {
  manualPath.value = ''
}

async function pickFolder() {
  error.value = null
  try {
    const { open } = await import('@tauri-apps/plugin-dialog')
    const selected = await open({ directory: true, multiple: false })
    if (selected && typeof selected === 'string') {
      manualPath.value = selected
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
    await emit('add', p)
    clearSelection()
  } catch (e) {
    error.value = e instanceof Error ? e.message : String(e)
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <section class="card glass-panel-strong">
    <h2>Add photo library</h2>
    <p class="hint">Choose a folder on disk. All scanning runs locally in Python.</p>
    <button type="button" class="btn-gradient block" :disabled="busy" @click="pickFolder">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true">
        <path
          d="M3 7a2 2 0 012-2h4l2 2h8a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2V7z"
          stroke="currentColor"
          stroke-width="1.75"
          stroke-linejoin="round"
        />
      </svg>
      Choose folder…
    </button>
    <label class="field">
      <span>Or enter path</span>
      <input v-model="manualPath" type="text" placeholder="D:\Photos" />
    </label>
    <button
      type="button"
      class="btn-add"
      :disabled="busy || !manualPath.trim()"
      @click="submit"
    >
      Add library
    </button>
    <p v-if="error" class="error-text">{{ error }}</p>
  </section>
</template>

<style scoped>
.card {
  padding: 1.5rem 1.5rem 1.35rem;
  height: 100%;
  min-height: 320px;
  max-height: 350px;
  display: flex;
  flex-direction: column;
}
h2 {
  margin-bottom: 0.5rem;
}
.hint {
  color: var(--muted);
  font-size: 0.9rem;
  margin: 0 0 1.25rem;
  line-height: 1.45;
}
.field {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  margin: 1.1rem 0 0.85rem;
  font-size: 0.85rem;
  color: var(--muted);
}
.field input {
  padding: 0.65rem 0.85rem;
  border-radius: 12px;
  border: 1px solid var(--glass-border);
  background: rgba(8, 10, 18, 0.55);
  color: var(--text);
  font-size: 0.9rem;
}
.field input::placeholder {
  color: var(--muted);
  opacity: 0.7;
}
.field input:focus {
  outline: none;
  border-color: rgba(45, 212, 191, 0.45);
}
.btn-add {
  width: 100%;
  padding: 0.65rem 1rem;
  border-radius: 12px;
  border: 1px solid var(--glass-border);
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-soft);
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition:
    background 0.15s,
    border-color 0.15s;
}
.btn-add:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.15);
  color: var(--text);
}
.btn-add:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}
.error-text {
  margin-top: 0.75rem;
}
</style>
