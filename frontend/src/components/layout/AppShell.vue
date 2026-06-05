<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { useApiHealth } from '../../composables/useApi'

const { online, checking } = useApiHealth()
</script>

<template>
  <div class="shell">
    <div class="header-sticky">
      <header class="header glass-panel-strong">
        <RouterLink to="/" class="brand">Face Gallery</RouterLink>
        <nav class="nav-center">
          <RouterLink to="/">Home</RouterLink>
          <RouterLink to="/scans">Scans</RouterLink>
          <RouterLink to="/settings">Settings</RouterLink>
        </nav>
        <span
          class="status-pill"
          :class="{ ok: online, bad: !online && !checking, wait: checking && !online }"
        >
          <span class="dot" />
          {{
            checking && !online
              ? 'Connecting…'
              : online
                ? 'API online'
                : 'API offline'
          }}
        </span>
      </header>
    </div>
    <main class="main">
      <slot />
    </main>
  </div>
</template>

<style scoped>
.shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
.header-sticky {
  position: sticky;
  top: 0;
  z-index: 100;
  padding: 1rem 1.5rem 0.75rem;
  margin-bottom: 0.25rem;
  background: linear-gradient(
    180deg,
    var(--bg-deep) 0%,
    var(--bg-deep) 70%,
    transparent 100%
  );
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}
.header {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: 1rem;
  padding: 0.85rem 1.75rem;
  margin: 0;
  border-radius: 18px;
}
.brand {
  font-weight: 700;
  font-size: 1.1rem;
  color: var(--text);
  text-decoration: none;
  justify-self: start;
}
.nav-center {
  display: flex;
  gap: 0.5rem;
  justify-self: center;
}
.nav-center a {
  color: var(--muted);
  text-decoration: none;
  padding: 0.45rem 1rem;
  font-size: 0.92rem;
  font-weight: 500;
  border-bottom: 2px solid transparent;
  transition:
    color 0.15s,
    border-color 0.15s;
}
.nav-center a:hover {
  color: var(--text-soft);
}
.nav-center a.router-link-active {
  color: var(--accent-teal);
  border-bottom-color: var(--accent-teal);
}
.header .status-pill {
  justify-self: end;
}
.main {
  flex: 1;
  padding: 0.5rem 1.5rem 2.5rem;
  max-width: 1400px;
  width: 100%;
  margin: 0 auto;
  box-sizing: border-box;
}
@media (max-width: 640px) {
  .header {
    grid-template-columns: 1fr;
    text-align: center;
  }
  .brand,
  .header .status-pill {
    justify-self: center;
  }
  .nav-center {
    justify-self: center;
    flex-wrap: wrap;
    justify-content: center;
  }
}
</style>
