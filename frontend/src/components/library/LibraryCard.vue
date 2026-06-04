<script setup lang="ts">
import { computed } from 'vue'
import { api } from '../../api/client'
import type { Library } from '../../api/types'
import { formatLastScan } from '../../utils/format'

const props = defineProps<{
  library: Library
  selected: boolean
}>()

const emit = defineEmits<{
  select: []
}>()

const thumbUrl = computed(() =>
  props.library.cover_person_id != null
    ? api.personThumbUrl(props.library.cover_person_id)
    : null,
)
</script>

<template>
  <button
    type="button"
    class="card"
    :class="{ selected }"
    :title="library.root_path"
    @click="emit('select')"
  >
    <div
      v-if="thumbUrl"
      class="bg-thumb"
      :style="{ backgroundImage: `url(${thumbUrl})` }"
    />
    <div class="card-inner">
      <div class="card-main">
        <span class="folder-icon" aria-hidden="true">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
            <path
              d="M3 7a2 2 0 012-2h4l2 2h8a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2V7z"
              stroke="currentColor"
              stroke-width="1.5"
              stroke-linejoin="round"
            />
          </svg>
        </span>
        <div class="info">
          <p class="path">{{ library.root_path }}</p>
          <dl class="stats">
            <div class="stat">
              <dt>Total Photos</dt>
              <dd>{{ library.photo_count }}</dd>
            </div>
            <div class="stat">
              <dt>Person Count</dt>
              <dd>{{ library.person_count }}</dd>
            </div>
            <div class="stat">
              <dt>Last Scan</dt>
              <dd>{{ formatLastScan(library.last_scan_at) }}</dd>
            </div>
          </dl>
        </div>
      </div>
    </div>
  </button>
</template>

<style scoped>
.card {
  position: relative;
  overflow: hidden;
  text-align: left;
  width: 100%;
  padding: 0;
  cursor: pointer;
  border-radius: 16px;
  border: 1px solid var(--glass-border);
  background: var(--glass-bg);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  box-shadow: inset 0 1px 0 var(--glass-highlight);
  transition:
    border-color 0.2s,
    box-shadow 0.2s;
}
.card:hover {
  border-color: rgba(45, 212, 191, 0.25);
}
.card.selected {
  border-color: var(--accent-teal);
  box-shadow:
    0 0 0 1px var(--accent-teal),
    0 4px 24px rgba(45, 212, 191, 0.15);
}
.bg-thumb {
  position: absolute;
  inset: 0;
  background-size: cover;
  background-position: center right;
  opacity: 0.35;
  filter: blur(12px);
  transform: scale(1.15);
  mask-image: linear-gradient(90deg, transparent 30%, black 85%);
  -webkit-mask-image: linear-gradient(90deg, transparent 30%, black 85%);
}
.card-inner {
  position: relative;
  padding: 1.1rem 1.25rem;
  min-height: 118px;
}
.card-main {
  display: flex;
  gap: 0.85rem;
  align-items: flex-start;
}
.folder-icon {
  flex-shrink: 0;
  color: var(--accent-teal);
  margin-top: 0.15rem;
}
.info {
  flex: 1;
  min-width: 0;
}
.path {
  margin: 0 0 0.65rem;
  font-weight: 600;
  font-size: 0.88rem;
  line-height: 1.35;
  color: var(--text);
  word-break: break-all;
}
.stats {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem 1.5rem;
  margin: 0;
}
.stat {
  display: flex;
  align-items: baseline;
  gap: 0.4rem;
}
.stat dt {
  margin: 0;
  font-size: 0.78rem;
  font-weight: 500;
  color: var(--muted);
}
.stat dd {
  margin: 0;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-soft);
}
</style>
