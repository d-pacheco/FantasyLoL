<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <div class="min-h-screen bg-gray-900">
    <nav class="flex items-center justify-between border-b border-gray-700 px-6 py-4">
      <h1 class="text-xl font-bold text-white">MythicForge</h1>
      <button
        class="rounded bg-gray-700 px-4 py-2 text-sm text-gray-300 hover:bg-gray-600"
        @click="handleLogout"
      >
        Logout
      </button>
    </nav>
    <main class="p-6">
      <h2 class="text-lg font-semibold text-white">Dashboard</h2>
      <p class="mt-2 text-gray-400">Welcome to MythicForge. Your fantasy leagues will appear here.</p>
    </main>
  </div>
</template>
