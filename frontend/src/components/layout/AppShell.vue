<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { useApiHealth } from '../../composables/useApi'

const { online, checking } = useApiHealth()
</script>

<template>
  <div class="shell">
    <header class="header">
      <RouterLink to="/" class="brand">Face Gallery</RouterLink>
      <nav>
        <RouterLink to="/">Home</RouterLink>
        <RouterLink to="/settings">Settings</RouterLink>
      </nav>
      <span class="status" :class="{ ok: online, bad: !online && !checking }">
        {{ checking ? 'API…' : online ? 'API online' : 'API offline' }}
      </span>
    </header>
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
.header {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 0.75rem 1.25rem;
  border-bottom: 1px solid var(--border);
  background: var(--surface);
}
.brand {
  font-weight: 700;
  color: var(--text);
  text-decoration: none;
}
nav {
  display: flex;
  gap: 1rem;
}
nav a {
  color: var(--muted);
  text-decoration: none;
}
nav a.router-link-active {
  color: var(--accent);
}
.status {
  margin-left: auto;
  font-size: 0.85rem;
  color: var(--muted);
}
.status.ok {
  color: #3dd68c;
}
.status.bad {
  color: #f07178;
}
.main {
  flex: 1;
  padding: 1.25rem;
}
</style>
