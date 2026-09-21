<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { inviteToLeague } from '../../api/fantasyApi'

const props = defineProps<{
  leagueId: string
}>()

const emit = defineEmits<{
  invited: [username: string]
  close: []
}>()

const username = ref('')
const inviting = ref(false)
const error = ref('')
const lastInvited = ref('')

async function sendInvite() {
  const name = username.value.trim()
  if (!name) return
  inviting.value = true
  error.value = ''
  try {
    await inviteToLeague(props.leagueId, name)
    emit('invited', name)
    lastInvited.value = name
    username.value = ''
  } catch (e: unknown) {
    lastInvited.value = ''
    const status = (e as { response?: { status: number } })?.response?.status
    if (status === 404) error.value = 'User not found.'
    else if (status === 409) error.value = 'User already invited or league is full.'
    else error.value = 'Failed to send invite.'
  } finally {
    inviting.value = false
  }
}

function onBackdropClick(e: MouseEvent) {
  if (e.target === e.currentTarget) emit('close')
}

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape') emit('close')
}

onMounted(() => window.addEventListener('keydown', onKeydown))
onUnmounted(() => window.removeEventListener('keydown', onKeydown))
</script>

<template>
  <div
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/60"
    @click="onBackdropClick"
  >
    <div class="w-full max-w-md rounded-xl bg-surface border border-border-subtle p-6 shadow-xl">
      <h2 class="text-lg font-semibold text-foreground mb-1">Invite Player</h2>
      <p class="text-sm text-foreground-muted mb-5">Send an invite by username. They'll appear as pending until they accept.</p>

      <div class="flex flex-col gap-2">
        <label class="block text-xs font-medium text-foreground-muted">Username</label>
        <div class="flex gap-2">
          <input
            v-model="username"
            type="text"
            placeholder="Enter username..."
            class="flex-1 rounded-lg bg-surface-elevated border border-border-subtle px-4 py-2 text-sm text-foreground placeholder:text-foreground-muted focus:outline-none focus:border-primary"
            @keydown.enter="sendInvite"
          />
          <button
            class="px-4 py-2 rounded-lg bg-primary text-white text-sm font-semibold hover:bg-primary-hover transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            :disabled="!username.trim() || inviting"
            @click="sendInvite"
          >
            {{ inviting ? 'Sending…' : 'Send Invite' }}
          </button>
        </div>

        <!-- Feedback -->
        <p v-if="error" class="text-xs text-danger">{{ error }}</p>
        <p v-else-if="lastInvited" class="text-xs text-success">
          Invited {{ lastInvited }} — invite another or close.
        </p>
      </div>

      <div class="flex justify-end gap-3 mt-6">
        <button
          class="px-4 py-2 rounded-lg text-sm text-foreground-muted hover:text-foreground transition-colors"
          @click="emit('close')"
        >
          Cancel
        </button>
      </div>
    </div>
  </div>
</template>
