<script setup lang="ts">
import { ref } from 'vue'
import { inviteToLeague } from '../../api/fantasyApi'
import type { LeagueMember } from '../../api/fantasyApi'

const props = defineProps<{
  leagueId: string
  members: LeagueMember[]
  isOwner: boolean
  ownerId: string
  loading: boolean
  error: string
}>()

const emit = defineEmits<{
  invited: [username: string]
}>()

const inviteUsername = ref('')
const inviteError = ref('')
const inviting = ref(false)

async function sendInvite() {
  if (!inviteUsername.value.trim()) return
  inviting.value = true
  inviteError.value = ''
  try {
    await inviteToLeague(props.leagueId, inviteUsername.value.trim())
    emit('invited', inviteUsername.value.trim())
    inviteUsername.value = ''
  } catch (e: unknown) {
    const status = (e as { response?: { status: number } })?.response?.status
    if (status === 404) inviteError.value = 'User not found.'
    else if (status === 409) inviteError.value = 'User already invited or league is full.'
    else inviteError.value = 'Failed to send invite.'
  } finally {
    inviting.value = false
  }
}
</script>

<template>
  <div class="flex flex-col gap-6">
    <!-- Loading / Error -->
    <div v-if="loading" class="flex justify-center py-8">
      <div class="w-5 h-5 border-2 border-primary border-t-transparent rounded-full animate-spin" />
    </div>
    <div v-else-if="error" class="text-sm text-danger">{{ error }}</div>

    <template v-else>
      <!-- Accepted -->
      <div>
        <h3 class="text-xs font-semibold text-foreground-muted uppercase tracking-wider mb-2">Members</h3>
        <div class="flex flex-col divide-y divide-border-subtle rounded-xl border border-border-subtle overflow-hidden">
          <div
            v-for="m in members.filter(m => m.status === 'accepted')"
            :key="m.user_id"
            class="flex items-center gap-3 px-4 py-3 bg-surface"
          >
            <div class="w-7 h-7 rounded-full bg-surface-elevated flex items-center justify-center text-xs font-bold text-foreground-muted">
              {{ m.username.slice(0, 2).toUpperCase() }}
            </div>
            <span class="text-sm text-foreground">{{ m.username }}</span>
            <span v-if="m.user_id === ownerId" class="ml-auto text-xs text-foreground-muted">owner</span>
          </div>
          <div v-if="members.filter(m => m.status === 'accepted').length === 0" class="px-4 py-3 text-sm text-foreground-muted bg-surface">
            No members yet.
          </div>
        </div>
      </div>

      <!-- Pending -->
      <div v-if="members.filter(m => m.status === 'pending').length > 0">
        <h3 class="text-xs font-semibold text-foreground-muted uppercase tracking-wider mb-2">Pending Invites</h3>
        <div class="flex flex-col divide-y divide-border-subtle rounded-xl border border-border-subtle overflow-hidden">
          <div
            v-for="m in members.filter(m => m.status === 'pending')"
            :key="m.user_id"
            class="flex items-center gap-3 px-4 py-3 bg-surface"
          >
            <div class="w-7 h-7 rounded-full bg-surface-elevated flex items-center justify-center text-xs font-bold text-foreground-muted">
              {{ m.username.slice(0, 2).toUpperCase() }}
            </div>
            <span class="text-sm text-foreground">{{ m.username }}</span>
            <span class="ml-auto text-xs text-foreground-muted">pending</span>
          </div>
        </div>
      </div>

      <!-- Invite (owner only) -->
      <div v-if="isOwner">
        <h3 class="text-xs font-semibold text-foreground-muted uppercase tracking-wider mb-2">Invite Player</h3>
        <div class="flex gap-2">
          <input
            v-model="inviteUsername"
            type="text"
            placeholder="Enter username..."
            class="flex-1 rounded-lg bg-surface border border-border-subtle px-4 py-2 text-sm text-foreground placeholder:text-foreground-muted focus:outline-none focus:border-primary"
            @keydown.enter="sendInvite"
          />
          <button
            class="px-4 py-2 rounded-lg bg-primary text-white text-sm font-semibold hover:bg-primary-hover transition-colors disabled:opacity-50"
            :disabled="!inviteUsername.trim() || inviting"
            @click="sendInvite"
          >
            {{ inviting ? 'Sending…' : 'Send Invite' }}
          </button>
        </div>
        <p v-if="inviteError" class="mt-1.5 text-xs text-danger">{{ inviteError }}</p>
      </div>
    </template>
  </div>
</template>
