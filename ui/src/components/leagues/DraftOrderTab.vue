<script setup lang="ts">
import { ref, watch } from 'vue'
import draggable from 'vuedraggable'
import { updateDraftOrder } from '../../api/fantasyApi'
import type { DraftOrderEntry } from '../../api/fantasyApi'
import { GripVertical } from 'lucide-vue-next'

const props = defineProps<{
  leagueId: string
  draftOrder: DraftOrderEntry[]
  isOwner: boolean
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
      <!-- Owner: draggable -->
      <draggable
        v-if="isOwner"
        v-model="localOrder"
        item-key="user_id"
        handle=".drag-handle"
        class="flex flex-col gap-2"
      >
        <template #item="{ element, index }">
          <div class="flex items-center gap-3 px-4 py-3 rounded-xl border border-border-subtle bg-surface">
            <span class="drag-handle cursor-grab active:cursor-grabbing text-foreground-muted">
              <GripVertical class="w-4 h-4" />
            </span>
            <span class="text-xs font-bold text-foreground-muted w-5">{{ index + 1 }}</span>
            <div class="w-7 h-7 rounded-full bg-surface-elevated flex items-center justify-center text-xs font-bold text-foreground-muted">
              {{ element.username.slice(0, 2).toUpperCase() }}
            </div>
            <span class="text-sm text-foreground">{{ element.username }}</span>
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
          <span class="text-xs font-bold text-foreground-muted w-5">{{ index + 1 }}</span>
          <div class="w-7 h-7 rounded-full bg-surface-elevated flex items-center justify-center text-xs font-bold text-foreground-muted">
            {{ entry.username.slice(0, 2).toUpperCase() }}
          </div>
          <span class="text-sm text-foreground">{{ entry.username }}</span>
        </div>
      </div>

      <!-- Save button (owner only) -->
      <div v-if="isOwner" class="flex items-center gap-3">
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
