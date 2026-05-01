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
  <main class="flex min-h-screen items-center justify-center bg-gray-900">
    <form
      class="w-full max-w-sm rounded-lg bg-gray-800 p-8 shadow-lg"
      @submit.prevent="handleLogin"
    >
      <h1 class="mb-6 text-center text-2xl font-bold text-white">MythicForge</h1>

      <p v-if="auth.error" class="mb-4 rounded bg-red-900/50 p-2 text-sm text-red-300">
        {{ auth.error }}
      </p>

      <label for="username" class="mb-1 block text-sm text-gray-300">Username</label>
      <input
        id="username"
        v-model="username"
        type="text"
        required
        autocomplete="username"
        class="mb-4 w-full rounded border border-gray-600 bg-gray-700 px-3 py-2 text-white placeholder-gray-400 focus:border-indigo-500 focus:outline-none"
      />

      <label for="password" class="mb-1 block text-sm text-gray-300">Password</label>
      <div class="mb-6">
        <PasswordInput id="password" v-model="password" autocomplete="current-password" />
      </div>

      <button
        type="submit"
        :disabled="loading"
        class="w-full rounded bg-indigo-600 py-2 font-semibold text-white hover:bg-indigo-500 disabled:opacity-50"
      >
        {{ loading ? 'Signing in...' : 'Sign In' }}
      </button>

      <p class="mt-4 text-center text-sm text-gray-400">
        Don't have an account?
        <RouterLink to="/signup" class="text-indigo-400 hover:underline">Sign up</RouterLink>
      </p>
    </form>
  </main>
</template>
