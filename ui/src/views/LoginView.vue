<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import PasswordInput from '../components/common/PasswordInput.vue'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const username = ref('')
const password = ref('')
const loading = ref(false)

async function handleLogin() {
  loading.value = true
  try {
    await auth.login(username.value, password.value)
    const redirect = (route.query.redirect as string) || '/'
    router.push(redirect)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main class="flex min-h-screen items-center justify-center bg-background">
    <form
      class="w-full max-w-sm rounded-xl bg-surface p-8 shadow-lg border border-border-subtle"
      @submit.prevent="handleLogin"
    >
      <h1 class="mb-6 text-center text-2xl font-bold text-foreground">MythicForge</h1>

      <p v-if="auth.error" class="mb-4 rounded-lg bg-danger/10 border border-danger/25 p-2 text-sm text-danger">
        {{ auth.error }}
      </p>

      <label for="username" class="mb-1 block text-sm text-foreground-muted">Username</label>
      <input
        id="username"
        v-model="username"
        type="text"
        required
        autocomplete="username"
        class="mb-4 w-full rounded-lg border border-border bg-surface-elevated px-3 py-2 text-foreground placeholder-foreground-muted focus:border-primary focus:outline-none"
      />

      <label for="password" class="mb-1 block text-sm text-foreground-muted">Password</label>
      <div class="mb-6">
        <PasswordInput id="password" v-model="password" autocomplete="current-password" />
      </div>

      <button
        type="submit"
        :disabled="loading"
        class="w-full rounded-lg bg-primary py-2 font-semibold text-white hover:bg-primary-hover disabled:opacity-50 transition-colors"
      >
        {{ loading ? 'Signing in...' : 'Sign In' }}
      </button>

      <p class="mt-4 text-center text-sm text-foreground-muted">
        Don't have an account?
        <RouterLink to="/signup" class="text-primary hover:underline">Sign up</RouterLink>
      </p>
    </form>
  </main>
</template>
