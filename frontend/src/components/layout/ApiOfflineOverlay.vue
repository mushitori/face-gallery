<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { useApiHealthStore } from '../../stores/apiHealth'

const store = useApiHealthStore()
const { showOverlay, overlayTitle, overlayMessage, overlayHint, overlayPhase, checking } =
  storeToRefs(store)
</script>

<template>
  <Teleport to="body">
    <div
      v-if="showOverlay"
      class="api-overlay"
      role="alertdialog"
      aria-modal="true"
      :aria-busy="checking"
      :aria-label="overlayTitle"
    >
      <div class="api-overlay__backdrop" />
      <div class="api-overlay__card glass-panel-strong">
        <div class="api-overlay__icon" :class="{ pulse: overlayPhase !== 'recovered' }">
          <span v-if="overlayPhase === 'recovered'" class="check">✓</span>
          <span v-else class="spinner" aria-hidden="true" />
        </div>
        <h2 class="api-overlay__title">{{ overlayTitle }}</h2>
        <p class="api-overlay__message">{{ overlayMessage }}</p>
        <p v-if="overlayHint" class="api-overlay__hint">{{ overlayHint }}</p>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.api-overlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  display: grid;
  place-items: center;
  padding: 1.5rem;
}

.api-overlay__backdrop {
  position: absolute;
  inset: 0;
  background: rgba(8, 10, 16, 0.82);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.api-overlay__card {
  position: relative;
  width: min(100%, 440px);
  padding: 2rem 1.75rem;
  text-align: center;
}

.api-overlay__icon {
  width: 3.25rem;
  height: 3.25rem;
  margin: 0 auto 1.25rem;
  border-radius: 999px;
  display: grid;
  place-items: center;
  background: rgba(34, 211, 238, 0.12);
  border: 1px solid rgba(34, 211, 238, 0.35);
}

.api-overlay__icon.pulse {
  animation: pulse-ring 1.6s ease-in-out infinite;
}

.spinner {
  width: 1.35rem;
  height: 1.35rem;
  border-radius: 999px;
  border: 2px solid rgba(34, 211, 238, 0.25);
  border-top-color: var(--accent-teal);
  animation: spin 0.8s linear infinite;
}

.check {
  color: var(--status-online);
  font-size: 1.5rem;
  font-weight: 700;
  line-height: 1;
}

.api-overlay__title {
  margin: 0 0 0.75rem;
  font-size: 1.35rem;
  font-weight: 650;
  color: var(--text);
}

.api-overlay__message {
  margin: 0;
  color: var(--text-soft);
  font-size: 0.98rem;
  line-height: 1.55;
}

.api-overlay__hint {
  margin: 1rem 0 0;
  color: var(--muted);
  font-size: 0.85rem;
  line-height: 1.5;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@keyframes pulse-ring {
  0%,
  100% {
    box-shadow: 0 0 0 0 rgba(34, 211, 238, 0.25);
  }
  50% {
    box-shadow: 0 0 0 10px rgba(34, 211, 238, 0);
  }
}
</style>
