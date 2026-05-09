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
  <div class="mx-auto max-w-2xl">
    <h2 class="mb-6 text-lg font-semibold text-foreground">Scraper Job Triggers</h2>

    <button
      class="mb-6 w-full rounded-lg bg-primary px-4 py-3 font-semibold text-white hover:bg-primary-hover disabled:opacity-50"
      :disabled="triggeringAll"
      @click="triggerAll"
    >
      {{ triggeringAll ? 'Triggering all...' : 'Trigger All Jobs' }}
    </button>

    <div class="space-y-3">
      <div
        v-for="job in jobs"
        :key="job.name"
        class="flex items-center justify-between rounded-lg bg-surface px-4 py-3"
      >
        <span class="text-foreground">{{ job.label }}</span>
        <div class="flex items-center gap-3">
          <span v-if="results[job.name]" class="text-sm text-foreground-muted">
            {{ results[job.name] }}
          </span>
          <button
            class="rounded-lg bg-surface-elevated px-3 py-1 text-sm text-foreground-muted hover:text-foreground disabled:opacity-50"
            :disabled="loading[job.name]"
            @click="triggerJob(job.name)"
          >
            {{ loading[job.name] ? '...' : 'Trigger' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
