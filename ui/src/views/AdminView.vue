<script setup lang="ts">
import { ref } from 'vue'
import { api } from '../api/client'

const jobs = [
  { name: 'fetch-leagues', label: 'Fetch Leagues' },
  { name: 'fetch-tournaments', label: 'Fetch Tournaments' },
  { name: 'fetch-teams', label: 'Fetch Teams' },
  { name: 'fetch-matches', label: 'Fetch Matches' },
  { name: 'fetch-games', label: 'Fetch Games' },
  { name: 'update-game-states', label: 'Update Game States' },
  { name: 'run-game-analysis', label: 'Run Game Analysis' },
]

const results = ref<Record<string, string>>({})
const loading = ref<Record<string, boolean>>({})
const triggeringAll = ref(false)

async function triggerJob(jobName: string) {
  loading.value[jobName] = true
  results.value[jobName] = ''
  try {
    const res = await api.post(`/admin/trigger/${jobName}`)
    results.value[jobName] = res.data.message || res.data.error
  } catch {
    results.value[jobName] = 'Failed to trigger'
  } finally {
    loading.value[jobName] = false
  }
}

async function triggerAll() {
  triggeringAll.value = true
  try {
    const res = await api.post('/admin/trigger-all')
    results.value = res.data.results
  } catch {
    results.value = { all: 'Failed to trigger' }
  } finally {
    triggeringAll.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-gray-900">
    <nav class="flex items-center justify-between border-b border-gray-700 px-6 py-4">
      <h1 class="text-xl font-bold text-white">MythicForge Admin</h1>
      <RouterLink to="/" class="text-sm text-gray-400 hover:text-white">← Back</RouterLink>
    </nav>
    <main class="mx-auto max-w-2xl p-6">
      <h2 class="mb-6 text-lg font-semibold text-white">Scraper Job Triggers</h2>

      <button
        class="mb-6 w-full rounded bg-indigo-600 px-4 py-3 font-semibold text-white hover:bg-indigo-500 disabled:opacity-50"
        :disabled="triggeringAll"
        @click="triggerAll"
      >
        {{ triggeringAll ? 'Triggering all...' : 'Trigger All Jobs' }}
      </button>

      <div class="space-y-3">
        <div
          v-for="job in jobs"
          :key="job.name"
          class="flex items-center justify-between rounded bg-gray-800 px-4 py-3"
        >
          <span class="text-white">{{ job.label }}</span>
          <div class="flex items-center gap-3">
            <span v-if="results[job.name]" class="text-sm text-gray-400">
              {{ results[job.name] }}
            </span>
            <button
              class="rounded bg-gray-700 px-3 py-1 text-sm text-gray-300 hover:bg-gray-600 disabled:opacity-50"
              :disabled="loading[job.name]"
              @click="triggerJob(job.name)"
            >
              {{ loading[job.name] ? '...' : 'Trigger' }}
            </button>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>
