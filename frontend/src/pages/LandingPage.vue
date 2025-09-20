<!-- dummy sample, can change name later, this can be home page w all the user's tasks instead, just rmb to change all the names in router/index.js -->
<!-- idk how yall do it, mayb instead of this we can have one folder for one page then put one vue file and one css file in each folder -->

 <script setup>
import { ref, onMounted } from 'vue'
import { api } from '../services/api'
const health = ref(null)
onMounted(async () => { health.value = await api.health().catch(() => ({ ok: false })) })
</script>

<template>
  <h1>Landing page</h1>
  <pre>Backend health: {{ health }}</pre>
</template>
