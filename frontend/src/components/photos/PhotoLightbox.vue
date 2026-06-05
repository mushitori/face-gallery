<script setup lang="ts">
import { computed, onMounted, onUnmounted } from 'vue'
import type { Photo } from '../../api/types'
import { api } from '../../api/client'

const props = defineProps<{
  photo: Photo
  index: number
  total: number
  rootPath?: string
}>()

const emit = defineEmits<{
  close: []
  prev: []
  next: []
}>()

const displayPath = computed(() =>
  props.rootPath ? `${props.rootPath}\\${props.photo.path}` : props.photo.path,
)

const counterLabel = computed(
  () => `Photo ${props.index + 1} of ${props.total}`,
)

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape') {
    e.preventDefault()
    emit('close')
  } else if (e.key === 'ArrowLeft') {
    e.preventDefault()
    emit('prev')
  } else if (e.key === 'ArrowRight') {
    e.preventDefault()
    emit('next')
  }
}

onMounted(() => {
  window.addEventListener('keydown', onKeydown)
  document.body.style.overflow = 'hidden'
})

onUnmounted(() => {
  window.removeEventListener('keydown', onKeydown)
  document.body.style.overflow = ''
})
</script>

<template>
  <Teleport to="body">
    <div class="overlay" role="dialog" aria-modal="true" :aria-label="counterLabel">
      <button
        type="button"
        class="chrome-btn close"
        aria-label="Close"
        @click="emit('close')"
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <path
            d="M6 6l12 12M18 6L6 18"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
          />
        </svg>
      </button>

      <button
        type="button"
        class="chrome-btn nav prev"
        aria-label="Previous photo"
        @click="emit('prev')"
      >
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <path
            d="M14 6l-6 6 6 6"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
        </svg>
      </button>

      <button
        type="button"
        class="chrome-btn nav next"
        aria-label="Next photo"
        @click="emit('next')"
      >
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <path
            d="M10 6l6 6-6 6"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
        </svg>
      </button>

      <div class="stage">
        <img
          :key="photo.id"
          :src="api.photoOriginalUrl(photo.id)"
          :alt="photo.path"
          class="photo"
        />
      </div>

      <div class="footer">
        <p class="path" :title="displayPath">{{ displayPath }}</p>
        <p class="counter" aria-live="polite">{{ counterLabel }}</p>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.overlay {
  position: fixed;
  inset: 0;
  z-index: 200;
  background: var(--glass-bg-strong-heavy);
  backdrop-filter: blur(24px) saturate(1.25);
  -webkit-backdrop-filter: blur(24px) saturate(1.25);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  /* padding: 4.5rem 5.5rem 6.5rem; */
  padding-top: 20px;
  padding-bottom: 94px;
  padding-left: 20px;
  padding-right: 20px;
  box-sizing: border-box;
}

.stage {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  min-height: 0;
  max-height: 100%;
}

.photo {
  display: block;
  max-width: 100%;
  max-height: 100%;
  width: auto;
  height: auto;
  object-fit: contain;
  border-radius: 4px;
  user-select: none;
}

.chrome-btn {
  position: absolute;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
  cursor: pointer;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  transition:
    background 0.15s,
    border-color 0.15s,
    transform 0.15s;
}

.chrome-btn:hover {
  background: rgba(255, 255, 255, 0.14);
  border-color: rgba(255, 255, 255, 0.22);
}

.chrome-btn:active {
  transform: scale(0.96);
}

.close {
  top: 24px;
  right: 1.5rem;
  width: 44px;
  height: 44px;
  border-radius: 50%;
}

.nav {
  top: 50%;
  transform: translateY(-50%);
  width: 52px;
  height: 52px;
  border-radius: 50%;
}

.nav:hover {
  transform: translateY(-50%) scale(1.04);
}

.nav:active {
  transform: translateY(-50%) scale(0.96);
}

.prev {
  left: 1.5rem;
}

.next {
  right: 1.5rem;
}

.footer {
  position: absolute;
  bottom: 1.75rem;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.45rem;
  max-width: min(90vw, 900px);
  width: 100%;
}

.path {
  margin: 0;
  padding: 0.55rem 1.35rem;
  background: rgba(0, 0, 0, 0.55);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 999px;
  color: var(--text-soft);
  font-size: 0.82rem;
  word-break: break-all;
  text-align: center;
  max-width: 100%;
}

.counter {
  margin: 0;
  color: var(--muted);
  font-size: 0.78rem;
}

@media (max-width: 640px) {
  .overlay {
    padding: 4.5rem 3.75rem 6rem;
  }

  .close {
    top: 5rem;
    right: 1rem;
  }

  .nav {
    width: 44px;
    height: 44px;
  }

  .prev {
    left: 0.75rem;
  }

  .next {
    right: 0.75rem;
  }
}
</style>
