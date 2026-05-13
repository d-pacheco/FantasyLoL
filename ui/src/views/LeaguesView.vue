<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Trophy } from 'lucide-vue-next'
import { getMyLeagues, joinLeague, leaveLeague } from '../api/fantasyApi'
import CreateLeagueModal from '../components/leagues/CreateLeagueModal.vue'
import type { FantasyLeague } from '../types/fantasy'

const router = useRouter()

const pending = ref<FantasyLeague[]>([])
const accepted = ref<FantasyLeague[]>([])
const loading = ref(true)
const error = ref('')
const showCreateModal = ref(false)

async function fetchLeagues() {
  loading.value = true
  error.value = ''
  try {
    const res = await getMyLeagues()
    pending.value = res.pending
    accepted.value = res.accepted
  } catch {
    error.value = 'Failed to load leagues.'
  } finally {
    loading.value = false
  }
}

onMounted(fetchLeagues)

async function acceptInvite(league: FantasyLeague) {
  try {
    await joinLeague(league.id)
    router.push({ name: 'league-detail', params: { id: league.id } })
  } catch {
    error.value = 'Failed to accept invite.'
  }
}

async function declineInvite(league: FantasyLeague) {
  try {
    await leaveLeague(league.id)
    pending.value = pending.value.filter((l) => l.id !== league.id)
  } catch {
    error.value = 'Failed to decline invite.'
  }
}

function onLeagueCreated(league: FantasyLeague) {
  showCreateModal.value = false
  router.push({ name: 'league-detail', params: { id: league.id } })
}

const statusColors: Record<string, string> = {
  'pre-draft': '#f59e0b',
  draft: '#3b82f6',
  active: '#22c55e',
  completed: '#64748b',
  deleted: '#ef4444',
}
</script>

<template>
  <div class="flex flex-col gap-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-lg font-semibold text-foreground">My Leagues</h2>
        <p class="mt-1 text-sm text-foreground-muted">Manage your fantasy leagues.</p>
      </div>
      <button
        class="px-4 py-2 rounded-lg bg-primary text-white text-sm font-semibold hover:bg-primary-hover transition-colors"
        @click="showCreateModal = true"
      >
        + Create League
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-16">
      <div class="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin" />
    </div>

    <!-- Error -->
    <div v-else-if="error" class="text-center py-12 text-danger text-sm">{{ error }}</div>

    <template v-else>
      <!-- Empty state -->
      <div
        v-if="pending.length === 0 && accepted.length === 0"
        class="flex flex-col items-center justify-center py-20"
      >
        <div class="w-16 h-16 rounded-full bg-surface-elevated flex items-center justify-center mb-4">
          <Trophy class="w-8 h-8 text-foreground-muted" />
        </div>
        <h3 class="text-base font-semibold text-foreground mb-2">No Leagues Yet</h3>
        <p class="text-sm text-foreground-muted mb-6 text-center max-w-sm">
          Create a new league or wait for an invite from a friend.
        </p>
        <button
          class="px-6 py-2.5 rounded-lg bg-primary text-white font-semibold text-sm hover:bg-primary-hover transition-colors"
          @click="showCreateModal = true"
        >
          Create League
        </button>
      </div>

      <template v-else>
        <!-- Pending Invites -->
        <section v-if="pending.length > 0">
          <h3 class="text-sm font-semibold text-foreground-muted uppercase tracking-wider mb-3">
            Pending Invites
          </h3>
          <div class="flex flex-col gap-3">
            <div
              v-for="league in pending"
              :key="league.id"
              class="flex items-center justify-between rounded-xl border border-border-subtle bg-surface px-5 py-4"
            >
              <div>
                <p class="font-medium text-sm text-foreground">{{ league.name }}</p>
                <p class="text-xs text-foreground-muted mt-0.5">{{ league.number_of_teams }} teams</p>
              </div>
              <div class="flex gap-2">
                <button
                  class="px-3 py-1.5 rounded-lg bg-primary text-white text-xs font-semibold hover:bg-primary-hover transition-colors"
                  @click="acceptInvite(league)"
                >
                  Accept
                </button>
                <button
                  class="px-3 py-1.5 rounded-lg border border-border-subtle text-xs text-foreground-muted hover:text-foreground transition-colors"
                  @click="declineInvite(league)"
                >
                  Decline
                </button>
              </div>
            </div>
          </div>
        </section>

        <!-- My Leagues -->
        <section v-if="accepted.length > 0">
          <h3 class="text-sm font-semibold text-foreground-muted uppercase tracking-wider mb-3">
            My Leagues
          </h3>
          <div class="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
            <RouterLink
              v-for="league in accepted"
              :key="league.id"
              :to="{ name: 'league-detail', params: { id: league.id } }"
              class="rounded-xl border border-border-subtle bg-surface px-5 py-4 hover:bg-surface-elevated transition-colors block"
            >
              <p class="font-semibold text-sm text-foreground">{{ league.name }}</p>
              <div class="flex items-center gap-3 mt-2">
                <span
                  class="text-xs font-bold px-2 py-0.5 rounded-md capitalize"
                  :style="{
                    background: `${statusColors[league.status] ?? '#64748b'}1a`,
                    color: statusColors[league.status] ?? '#64748b',
                  }"
                >
                  {{ league.status }}
                </span>
                <span class="text-xs text-foreground-muted">{{ league.number_of_teams }} teams</span>
              </div>
            </RouterLink>
          </div>
        </section>
      </template>
    </template>

    <!-- Create League Modal -->
    <CreateLeagueModal
      v-if="showCreateModal"
      @created="onLeagueCreated"
      @close="showCreateModal = false"
    />
  </div>
</template>
