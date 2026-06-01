<script setup lang="ts">
defineProps<{ show: boolean }>()
const emit = defineEmits<{ goToLeague: [] }>()
</script>

<template>
  <div v-if="show" data-testid="modal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
    <div class="bg-surface rounded-2xl border border-border-subtle px-10 py-8 flex flex-col items-center gap-6 shadow-xl">
      <h2 class="text-2xl font-bold text-foreground">🏆 Draft Complete!</h2>
      <p class="text-foreground-muted text-sm">All picks have been made. Your league is now active.</p>
      <button
        class="px-6 py-2 rounded-lg bg-primary text-white font-semibold hover:bg-primary-hover transition-colors"
        @click="emit('goToLeague')"
      >
        Go to League
      </button>
    </div>
  </div>
</template>
