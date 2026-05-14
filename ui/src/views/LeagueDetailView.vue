<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import {
  getLeagueById,
  getLeagueMembers,
  getLeagueSettings,
  getLeagueScoringSettings,
  getDraftOrder,
  leaveLeague,
  startDraft,
} from '../api/fantasyApi'
import type {
  LeagueMember,
  DraftOrderEntry,
} from '../api/fantasyApi'
import type { FantasyLeague, FantasyLeagueSettings, FantasyLeagueScoringSettings } from '../types/fantasy'
import MembersTab from '../components/leagues/MembersTab.vue'
import SettingsTab from '../components/leagues/SettingsTab.vue'
import ScoringTab from '../components/leagues/ScoringTab.vue'
import DraftOrderTab from '../components/leagues/DraftOrderTab.vue'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const leagueId = route.params.id as string

const league = ref<FantasyLeague | null>(null)

const isOwner = computed(() => !!auth.userId && league.value?.owner_id === auth.userId)
const acceptedCount = computed(() => members.value.filter(m => m.status === 'accepted').length)
const isFull = computed(() => !!league.value && acceptedCount.value >= league.value.number_of_teams)

type Tab = 'members' | 'settings' | 'scoring' | 'draft-order'
const activeTab = ref<Tab>('members')
const tabs: { key: Tab; label: string }[] = [
  { key: 'members', label: 'Members' },
  { key: 'settings', label: 'Settings' },
  { key: 'scoring', label: 'Scoring' },
  { key: 'draft-order', label: 'Draft Order' },
]

// Per-tab data
const members = ref<LeagueMember[]>([])
const membersLoading = ref(false)
const membersError = ref('')

const settings = ref<FantasyLeagueSettings | null>(null)
const settingsLoading = ref(false)
const settingsError = ref('')

const scoring = ref<FantasyLeagueScoringSettings | null>(null)
const scoringLoading = ref(false)
const scoringError = ref('')

const draftOrder = ref<DraftOrderEntry[]>([])
const draftOrderLoading = ref(false)
const draftOrderError = ref('')

const startingDraft = ref(false)
const startDraftError = ref('')
const leavingLeague = ref(false)

async function fetchAll() {
  membersLoading.value = true
  settingsLoading.value = true
  scoringLoading.value = true
  draftOrderLoading.value = true

  await Promise.allSettled([
    getLeagueById(leagueId).then(d => { league.value = d }).catch(() => {}),
    getLeagueMembers(leagueId).then(d => { members.value = d }).catch(() => { membersError.value = 'Unable to load members.' }).finally(() => { membersLoading.value = false }),
    getLeagueSettings(leagueId).then(d => { settings.value = d }).catch(() => { settingsError.value = 'Unable to load settings.' }).finally(() => { settingsLoading.value = false }),
    getLeagueScoringSettings(leagueId).then(d => { scoring.value = d }).catch(() => { scoringError.value = 'Unable to load scoring.' }).finally(() => { scoringLoading.value = false }),
    getDraftOrder(leagueId).then(d => { draftOrder.value = d }).catch(() => { draftOrderError.value = 'Unable to load draft order.' }).finally(() => { draftOrderLoading.value = false }),
  ])
}

onMounted(fetchAll)

function onInvited(username: string) {
  members.value.push({ user_id: username, username, status: 'pending' })
}

async function onLeave() {
  leavingLeague.value = true
  try {
    await leaveLeague(leagueId)
    router.push({ name: 'leagues' })
  } catch {
    leavingLeague.value = false
  }
}

async function onStartDraft() {
  startingDraft.value = true
  startDraftError.value = ''
  try {
    await startDraft(leagueId)
    router.push({ name: 'league-draft', params: { id: leagueId } })
  } catch {
    startDraftError.value = 'Failed to start draft.'
    startingDraft.value = false
  }
}

const statusColors: Record<string, string> = {
  'pre-draft': '#f59e0b',
  draft: '#3b82f6',
  active: '#22c55e',
  completed: '#64748b',
}
</script>

<template>
  <div class="flex flex-col gap-6">
    <!-- Header -->
    <div class="flex items-start justify-between gap-4">
      <div>
        <h2 class="text-lg font-semibold text-foreground">{{ league?.name ?? 'League' }}</h2>
        <div class="flex items-center gap-3 mt-1">
          <span
            v-if="league"
            class="text-xs font-bold px-2 py-0.5 rounded-md capitalize"
            :style="{
              background: `${statusColors[league.status] ?? '#64748b'}1a`,
              color: statusColors[league.status] ?? '#64748b',
            }"
          >
            {{ league.status }}
          </span>
          <span class="text-sm text-foreground-muted">
            {{ acceptedCount }}/{{ league?.number_of_teams ?? '?' }} members
          </span>
        </div>
      </div>

      <div class="flex flex-col items-end gap-1">
        <!-- Owner: Start Draft -->
        <button
          v-if="isOwner"
          class="px-4 py-2 rounded-lg text-sm font-semibold transition-colors"
          :class="isFull
            ? 'bg-primary text-white hover:bg-primary-hover'
            : 'bg-surface border border-border-subtle text-foreground-muted cursor-not-allowed'"
          :disabled="!isFull || startingDraft"
          @click="onStartDraft"
        >
          {{ startingDraft ? 'Starting…' : 'Start Draft' }}
        </button>
        <!-- Non-owner: Leave -->
        <button
          v-else
          class="px-4 py-2 rounded-lg border border-border-subtle text-sm text-foreground-muted hover:text-foreground transition-colors"
          :disabled="leavingLeague"
          @click="onLeave"
        >
          {{ leavingLeague ? 'Leaving…' : 'Leave League' }}
        </button>
        <p v-if="startDraftError" class="text-xs text-danger">{{ startDraftError }}</p>
        <p v-if="!isFull && isOwner" class="text-xs text-foreground-muted">
          Need {{ (league?.number_of_teams ?? 0) - acceptedCount }} more member(s) to start
        </p>
      </div>
    </div>

    <!-- Tabs -->
    <div class="flex gap-1 p-1 rounded-lg bg-surface border border-border-subtle w-fit">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        class="px-4 py-1.5 rounded-md text-xs font-medium transition-colors"
        :class="activeTab === tab.key
          ? 'bg-primary text-white'
          : 'text-foreground-muted hover:text-foreground'"
        @click="activeTab = tab.key"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- Tab content -->
    <MembersTab
      v-if="activeTab === 'members'"
      :league-id="leagueId"
      :members="members"
      :is-owner="isOwner"
      :owner-id="league?.owner_id ?? ''"
      :loading="membersLoading"
      :error="membersError"
      @invited="onInvited"
    />
    <SettingsTab
      v-else-if="activeTab === 'settings'"
      :settings="settings"
      :loading="settingsLoading"
      :error="settingsError"
    />
    <ScoringTab
      v-else-if="activeTab === 'scoring'"
      :scoring="scoring"
      :loading="scoringLoading"
      :error="scoringError"
    />
    <DraftOrderTab
      v-else-if="activeTab === 'draft-order'"
      :league-id="leagueId"
      :draft-order="draftOrder"
      :is-owner="isOwner"
      :loading="draftOrderLoading"
      :error="draftOrderError"
    />
  </div>
</template>
