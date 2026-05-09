<script setup lang="ts">
import { useRoute } from 'vue-router'
import {
  LayoutDashboard,
  Trophy,
  Users,
  Shield,
  Radio,
  Settings,
  Flame,
  ChevronLeft,
  ChevronRight,
} from 'lucide-vue-next'
import { useLayoutState } from '../../composables/useLayoutState'

const { isCollapsed, toggle } = useLayoutState()
const route = useRoute()

const navItems = [
  { icon: LayoutDashboard, label: 'Dashboard', to: '/' },
  { icon: Trophy, label: 'My Leagues', to: '/leagues' },
  { icon: Users, label: 'Browse Players', to: '/players' },
  { icon: Shield, label: 'Browse Teams', to: '/teams' },
  { icon: Radio, label: 'Live Matches', to: '/matches' },
  { icon: Settings, label: 'Settings', to: '/settings' },
]

function isActive(to: string) {
  return route.path === to
}
</script>

<template>
  <aside
    class="fixed left-0 top-0 h-full z-40 flex flex-col bg-surface transition-all duration-300 border-r border-border-subtle"
    :style="{ width: isCollapsed ? '64px' : '240px' }"
  >
    <!-- Logo -->
    <div class="h-16 flex items-center justify-between px-4 shrink-0 border-b border-border-subtle">
      <div class="flex items-center gap-3 min-w-0">
        <div class="w-8 h-8 rounded-lg flex items-center justify-center shrink-0 bg-primary">
          <Flame class="w-4 h-4 text-white" />
        </div>
        <span v-if="!isCollapsed" class="font-bold text-base truncate text-foreground">
          MythicForge
        </span>
      </div>
      <button
        class="p-1.5 rounded-md text-foreground-muted hover:bg-surface-elevated shrink-0"
        @click="toggle"
      >
        <ChevronLeft v-if="!isCollapsed" class="w-4 h-4" />
        <ChevronRight v-else class="w-4 h-4" />
      </button>
    </div>

    <!-- Nav -->
    <nav class="flex-1 py-4 px-2 flex flex-col gap-1 overflow-hidden">
      <RouterLink
        v-for="item in navItems"
        :key="item.to"
        :to="item.to"
        :title="isCollapsed ? item.label : undefined"
        class="flex items-center gap-3 px-3 py-2.5 rounded-lg w-full transition-all text-left"
        :class="
          isActive(item.to)
            ? 'bg-primary/12 border border-primary/25 text-primary'
            : 'border border-transparent text-foreground-muted hover:bg-surface-elevated hover:text-foreground'
        "
      >
        <component :is="item.icon" class="w-5 h-5 shrink-0" />
        <span v-if="!isCollapsed" class="text-sm font-medium truncate">{{ item.label }}</span>
      </RouterLink>
    </nav>

    <!-- User -->
    <div class="p-3 shrink-0 border-t border-border-subtle">
      <div class="flex items-center gap-3">
        <div class="w-9 h-9 rounded-full shrink-0 flex items-center justify-center text-sm font-bold text-white bg-primary">
          S
        </div>
        <p v-if="!isCollapsed" class="text-sm font-medium truncate text-foreground">Summoner42</p>
      </div>
    </div>
  </aside>
</template>
