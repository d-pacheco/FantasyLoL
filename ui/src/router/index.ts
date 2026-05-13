import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import AppLayout from '../components/layout/AppLayout.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
      meta: { public: true },
    },
    {
      path: '/signup',
      name: 'signup',
      component: () => import('../views/SignupView.vue'),
      meta: { public: true },
    },
    {
      path: '/',
      component: AppLayout,
      children: [
        {
          path: '',
          name: 'dashboard',
          component: () => import('../views/DashboardView.vue'),
        },
        {
          path: 'leagues',
          name: 'leagues',
          component: () => import('../views/LeaguesView.vue'),
        },
        {
          path: 'leagues/:id',
          name: 'league-detail',
          component: () => import('../views/LeagueDetailView.vue'),
        },
        {
          path: 'leagues/:id/draft',
          name: 'league-draft',
          component: () => import('../views/DraftView.vue'),
        },
        {
          path: 'players',
          name: 'players',
          component: () => import('../views/PlayersView.vue'),
        },
        {
          path: 'teams',
          name: 'teams',
          component: () => import('../views/TeamsView.vue'),
        },
        {
          path: 'matches',
          name: 'matches',
          component: () => import('../views/MatchesView.vue'),
        },
        {
          path: 'settings',
          name: 'settings',
          component: () => import('../views/SettingsView.vue'),
        },
        {
          path: 'admin',
          name: 'admin',
          component: () => import('../views/AdminView.vue'),
        },
      ],
    },
  ],
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (!to.meta.public && !auth.isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
})

export default router
