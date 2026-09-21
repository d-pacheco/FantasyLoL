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
  getLeaderboard,
  leaveLeague,
  startDraft,
} from '../api/fantasyApi'
import type {
  LeagueMember,
  DraftOrderEntry,
} from '../api/fantasyApi'
import type {
  FantasyLeague,
  FantasyLeagueSettings,
  FantasyLeagueScoringSettings,
  LeaderboardResponse,
} from '../types/fantasy'
import LeagueHero from '../components/leagues/LeagueHero.vue'
import MembersTab from '../components/leagues/MembersTab.vue'
import SettingsTab from '../components/leagues/SettingsTab.vue'
import ScoringTab from '../components/leagues/ScoringTab.vue'
import DraftOrderTab from '../components/leagues/DraftOrderTab.vue'
import LeaderboardTab from '../components/leagues/LeaderboardTab.vue'
import WeekScoresTab from '../components/leagues/WeekScoresTab.vue'
import MyRosterTab from '../components/leagues/MyRosterTab.vue'
import InviteMemberModal from '../components/leagues/InviteMemberModal.vue'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const leagueId = route.params.id as string

const league = ref<FantasyLeague | null>(null)
const settingsTabRef = ref<InstanceType<typeof SettingsTab> | null>(null)
const scoringTabRef = ref<InstanceType<typeof ScoringTab> | null>(null)

const isOwner = computed(() => !!auth.userId && league.value?.owner_id === auth.userId)
const isActive = computed(() => league.value?.status === 'active' || league.value?.status === 'completed')

type Tab = 'standings' | 'scores' | 'roster' | 'members' | 'settings' | 'scoring' | 'draft-order'
const activeTab = ref<Tab>('members')
const tabs = computed(() => {
  const base: { key: Tab; label: string }[] = []
  if (isActive.value) {
    base.push({ key: 'standings', label: 'Standings' })
    base.push({ key: 'scores', label: 'Scores' })
    base.push({ key: 'roster', label: 'My Roster' })
  }
  base.push({ key: 'members', label: 'Members' })
  base.push({ key: 'settings', label: 'Settings' })
  base.push({ key: 'scoring', label: 'Scoring' })
  base.push({ key: 'draft-order', label: 'Draft Order' })
  return base
})

const canEditActiveTab = computed(
  () => isOwner.value && league.value?.status === 'pre-draft' && (activeTab.value === 'settings' || activeTab.value === 'scoring'),
)

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

const leaderboard = ref<LeaderboardResponse | null>(null)

const startingDraft = ref(false)
const startDraftError = ref('')
const leavingLeague = ref(false)
const showInviteModal = ref(false)

// Hero stats: only meaningful once the season is under way (active/completed).
const heroStats = computed(() => {
  const lb = leaderboard.value
  if (!lb || !isActive.value) return null
  const me = lb.members.find((m) => m.user_id === auth.userId)
  if (!me) return null
  const second = lb.members.find((m) => m.position === 2)
  const leader = lb.members.find((m) => m.position === 1) ?? lb.members[0]
  const pointsBehind =
    me.position === 1
      ? me.total_points - (second?.total_points ?? me.total_points)
      : (leader?.total_points ?? me.total_points) - me.total_points
  return { rank: me.position, points: me.total_points, pointsBehind, week: lb.current_week }
})

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

  // Standings/Scores + hero stats only apply once active/completed.
  if (isActive.value) {
    activeTab.value = 'standings'
    try {
      leaderboard.value = await getLeaderboard(leagueId)
    } catch {
      // stats simply stay hidden
    }
  }
}

onMounted(fetchAll)

function onInvited(username: string) {
  members.value.push({ user_id: username, username, status: 'pending' })
}

function onSettingsUpdated(updated: FantasyLeagueSettings) {
  settings.value = updated
  if (league.value) {
    league.value.name = updated.name
    league.value.number_of_teams = updated.number_of_teams
    league.value.available_leagues = updated.available_leagues
  }
}

function onScoringUpdated(updated: FantasyLeagueScoringSettings) {
  scoring.value = updated
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

function onJoinDraft() {
  router.push({ name: 'league-draft', params: { id: leagueId } })
}

function onInviteShortcut() {
  showInviteModal.value = true
}

function triggerEdit() {
  if (activeTab.value === 'settings') settingsTabRef.value?.startEditing()
  else if (activeTab.value === 'scoring') scoringTabRef.value?.startEditing()
}
</script>

<template>
  <div class="flex flex-col gap-6">
    <!-- Breadcrumb -->
    <nav class="flex items-center gap-2 text-sm text-foreground-muted">
      <RouterLink :to="{ name: 'leagues' }" class="hover:text-foreground transition-colors">My Leagues</RouterLink>
      <span class="opacity-50">/</span>
      <span class="text-foreground font-medium">{{ league?.name ?? 'League' }}</span>
    </nav>

    <!-- Hero -->
    <LeagueHero
      :league="league"
      :members="members"
      :is-owner="isOwner"
      :current-user-id="auth.userId ?? ''"
      :starting="startingDraft"
      :leaving="leavingLeague"
      :start-error="startDraftError"
      :stats="heroStats"
      @start-draft="onStartDraft"
      @leave="onLeave"
      @join-draft="onJoinDraft"
      @invite="onInviteShortcut"
    />

    <!-- Tabs -->
    <div class="sticky top-0 z-20 -mx-1 px-1 py-2 bg-background/80 backdrop-blur border-b border-border-subtle">
      <div class="flex items-center justify-between gap-4">
        <div class="flex items-center gap-1 overflow-x-auto">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            data-testid="league-tab"
            class="relative px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors"
            :class="activeTab === tab.key
              ? 'text-foreground bg-surface'
              : 'text-foreground-muted hover:text-foreground hover:bg-surface/50'"
            @click="activeTab = tab.key"
          >
            {{ tab.label }}
            <span v-if="activeTab === tab.key" class="absolute left-3 right-3 -bottom-2 h-0.5 rounded-full bg-primary" />
          </button>
        </div>
        <button
          v-if="canEditActiveTab"
          class="shrink-0 px-4 py-1.5 rounded-lg text-sm font-medium bg-surface-elevated border border-border-subtle text-foreground hover:bg-primary hover:text-white transition-colors"
          @click="triggerEdit"
        >
          Edit
        </button>
      </div>
    </div>

    <!-- Tab content -->
    <LeaderboardTab
      v-if="activeTab === 'standings'"
      :league-id="leagueId"
    />
    <WeekScoresTab
      v-if="activeTab === 'scores'"
      :league-id="leagueId"
      :current-week="league?.current_week ?? 1"
      :start-week="league?.start_week ?? 1"
    />
    <MyRosterTab
      v-if="activeTab === 'roster'"
      :league-id="leagueId"
      :current-week="league?.current_week ?? 1"
    />
    <MembersTab
      v-if="activeTab === 'members'"
      :members="members"
      :owner-id="league?.owner_id ?? ''"
      :loading="membersLoading"
      :error="membersError"
    />
    <SettingsTab
      v-else-if="activeTab === 'settings'"
      ref="settingsTabRef"
      :settings="settings"
      :loading="settingsLoading"
      :error="settingsError"
      :editable="isOwner && league?.status === 'pre-draft'"
      :league-id="leagueId"
      @updated="onSettingsUpdated"
    />
    <ScoringTab
      v-else-if="activeTab === 'scoring'"
      ref="scoringTabRef"
      :scoring="scoring"
      :loading="scoringLoading"
      :error="scoringError"
      :editable="isOwner && league?.status === 'pre-draft'"
      :league-id="leagueId"
      @updated="onScoringUpdated"
    />
    <DraftOrderTab
      v-else-if="activeTab === 'draft-order'"
      :league-id="leagueId"
      :draft-order="draftOrder"
      :editable="isOwner && league?.status === 'pre-draft'"
      :loading="draftOrderLoading"
      :error="draftOrderError"
    />

    <!-- Invite modal -->
    <InviteMemberModal
      v-if="showInviteModal"
      :league-id="leagueId"
      @invited="onInvited"
      @close="showInviteModal = false"
    />
  </div>
</template>
