<script setup lang="ts">
import { ref, watch } from 'vue'
import draggable from 'vuedraggable'
import { updateDraftOrder } from '../../api/fantasyApi'
import type { DraftOrderEntry } from '../../api/fantasyApi'
import { GripVertical } from 'lucide-vue-next'

const props = defineProps<{
  leagueId: string
  draftOrder: DraftOrderEntry[]
  editable: boolean
  loading: boolean
  error: string
}>()

const localOrder = ref<DraftOrderEntry[]>([])
const saving = ref(false)
const saveError = ref('')
const saved = ref(false)

watch(() => props.draftOrder, (val) => {
  localOrder.value = val.map(e => ({ ...e }))
}, { immediate: true })

const AVATAR_COLORS = ['#3b82f6', '#f59e0b', '#22c55e', '#a855f7', '#06b6d4', '#ef4444', '#ec4899', '#14b8a6', '#eab308', '#8b5cf6']
function avatarColor(seed: string): string {
  let h = 0
  for (let i = 0; i < seed.length; i++) h = (h * 31 + seed.charCodeAt(i)) % AVATAR_COLORS.length
  return AVATAR_COLORS[h]
}
function initials(name: string): string {
  return name.slice(0, 2).toUpperCase()
}

async function save() {
  saving.value = true
  saveError.value = ''
  saved.value = false
  try {
    const updated = localOrder.value.map((e, i) => ({ ...e, position: i + 1 }))
    await updateDraftOrder(props.leagueId, updated)
    saved.value = true
    setTimeout(() => { saved.value = false }, 2000)
  } catch {
    saveError.value = 'Failed to save draft order.'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="flex flex-col gap-4">
    <div v-if="loading" class="flex justify-center py-8">
      <div class="w-5 h-5 border-2 border-primary border-t-transparent rounded-full animate-spin" />
    </div>
    <div v-else-if="error" class="text-sm text-danger">{{ error }}</div>

    <template v-else>
      <!-- Context header -->
      <div>
        <h3 class="text-base font-semibold text-foreground">Draft Order</h3>
        <p class="text-sm text-foreground-muted mt-1">
          Snake draft — the order reverses each round.
          <span v-if="editable">Drag to reorder before the draft starts.</span>
        </p>
      </div>

      <!-- Owner: draggable -->
      <draggable
        v-if="editable"
        v-model="localOrder"
        item-key="user_id"
        handle=".drag-handle"
        class="flex flex-col gap-2"
      >
        <template #item="{ element, index }">
          <div class="flex items-center gap-3 px-4 py-3 rounded-xl border border-border-subtle bg-surface hover:border-primary/40 transition-colors">
            <span class="drag-handle cursor-grab active:cursor-grabbing text-foreground-muted">
              <GripVertical class="w-4 h-4" />
            </span>
            <span class="inline-flex items-center justify-center w-7 h-7 rounded-full bg-surface-elevated text-xs font-bold text-foreground-muted shrink-0">
              {{ index + 1 }}
            </span>
            <div
              class="w-8 h-8 rounded-full flex items-center justify-center text-[10px] font-bold text-white shrink-0"
              :style="{ background: avatarColor(element.username) }"
            >
              {{ initials(element.username) }}
            </div>
            <span class="text-sm font-medium text-foreground">{{ element.username }}</span>
          </div>
        </template>
      </draggable>

      <!-- Non-owner: static list -->
      <div v-else class="flex flex-col gap-2">
        <div
          v-for="(entry, index) in draftOrder"
          :key="entry.user_id"
          class="flex items-center gap-3 px-4 py-3 rounded-xl border border-border-subtle bg-surface"
        >
          <span class="inline-flex items-center justify-center w-7 h-7 rounded-full bg-surface-elevated text-xs font-bold text-foreground-muted shrink-0">
            {{ index + 1 }}
          </span>
          <div
            class="w-8 h-8 rounded-full flex items-center justify-center text-[10px] font-bold text-white shrink-0"
            :style="{ background: avatarColor(entry.username) }"
          >
            {{ initials(entry.username) }}
          </div>
          <span class="text-sm font-medium text-foreground">{{ entry.username }}</span>
        </div>
      </div>

      <!-- Save button (editable only) -->
      <div v-if="editable" class="flex items-center gap-3">
        <button
          class="px-4 py-2 rounded-lg bg-primary text-white text-sm font-semibold hover:bg-primary-hover transition-colors disabled:opacity-50"
          :disabled="saving"
          @click="save"
        >
          {{ saving ? 'Saving…' : 'Save Order' }}
        </button>
        <span v-if="saved" class="text-xs text-success">Saved!</span>
        <span v-if="saveError" class="text-xs text-danger">{{ saveError }}</span>
      </div>
    </template>
  </div>
</template>
