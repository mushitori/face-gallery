<script setup lang="ts">
import { useRouter } from 'vue-router'
import AppShell from '../components/layout/AppShell.vue'

const router = useRouter()
router.replace('/')
</script>

<template>
  <AppShell>
    <p>Redirecting…</p>
  </AppShell>
</template>
