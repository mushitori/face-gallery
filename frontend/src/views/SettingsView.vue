<script setup lang="ts">
import AppShell from '../components/layout/AppShell.vue'
import { api } from '../api/client'
</script>

<template>
  <AppShell>
    <h1>Settings</h1>
    <dl class="settings">
      <dt>API base URL</dt>
      <dd>{{ api.base }}</dd>
      <dt>Offline</dt>
      <dd>All face detection and storage run locally. No cloud uploads.</dd>
      <dt>Models</dt>
      <dd>
        InsightFace buffalo_l — place under
        <code>backend/models/buffalo_l/</code> or app data models folder.
      </dd>
    </dl>
  </AppShell>
</template>

<style scoped>
.settings {
  display: grid;
  grid-template-columns: 140px 1fr;
  gap: 0.75rem 1rem;
  max-width: 640px;
}
dt {
  color: var(--muted);
}
code {
  font-size: 0.85rem;
}
</style>
