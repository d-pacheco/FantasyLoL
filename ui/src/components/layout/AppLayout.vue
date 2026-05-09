<script setup lang="ts">
import AppSidebar from './AppSidebar.vue'
import AppHeader from './AppHeader.vue'
import { useLayoutState } from '../../composables/useLayoutState'

const { isCollapsed } = useLayoutState()
</script>

<template>
  <div class="min-h-screen bg-background">
    <AppSidebar />
    <div
      class="transition-all duration-300"
      :style="{ marginLeft: isCollapsed ? '64px' : '240px' }"
    >
      <AppHeader />
      <main class="p-6">
        <RouterView />
      </main>
    </div>
  </div>
</template>
