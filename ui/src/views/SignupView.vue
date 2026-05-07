<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import PasswordInput from '../components/common/PasswordInput.vue'

const auth = useAuthStore()
const router = useRouter()

const username = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const loading = ref(false)

const passwordMismatch = computed(
  () => confirmPassword.value.length > 0 && password.value !== confirmPassword.value
)

const usernameError = computed(() => {
  if (username.value.length === 0) return ''
  if (username.value.length < 3) return 'Username must be at least 3 characters'
  if (username.value.length > 32) return 'Username must be at most 32 characters'
  return ''
})

const passwordError = computed(() => {
  if (password.value.length === 0) return ''
  if (password.value.length < 8) return 'Password must be at least 8 characters'
  if (password.value.length > 128) return 'Password must be at most 128 characters'
  return ''
})

const formValid = computed(
  () =>
    username.value.length >= 3 &&
    username.value.length <= 32 &&
    email.value.length > 0 &&
    password.value.length >= 8 &&
    password.value.length <= 128 &&
    !passwordMismatch.value
)

async function handleSignup() {
  if (!formValid.value) return
  loading.value = true
  try {
    await auth.signup(username.value, email.value, password.value)
    router.push('/login')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main class="flex min-h-screen items-center justify-center bg-gray-900">
    <form
      class="w-full max-w-sm rounded-lg bg-gray-800 p-8 shadow-lg"
      @submit.prevent="handleSignup"
    >
      <h1 class="mb-6 text-center text-2xl font-bold text-white">Create Account</h1>

      <p v-if="auth.error" class="mb-4 rounded bg-red-900/50 p-2 text-sm text-red-300">
        {{ auth.error }}
      </p>

      <label for="username" class="mb-1 block text-sm text-gray-300">Username</label>
      <input
        id="username"
        v-model="username"
        type="text"
        required
        minlength="3"
        maxlength="32"
        autocomplete="username"
        class="mb-1 w-full rounded border border-gray-600 bg-gray-700 px-3 py-2 text-white placeholder-gray-400 focus:border-indigo-500 focus:outline-none"
      />
      <p v-if="usernameError" class="mb-4 text-sm text-red-400">{{ usernameError }}</p>
      <div v-else class="mb-4" />

      <label for="email" class="mb-1 block text-sm text-gray-300">Email</label>
      <input
        id="email"
        v-model="email"
        type="email"
        required
        autocomplete="email"
        class="mb-4 w-full rounded border border-gray-600 bg-gray-700 px-3 py-2 text-white placeholder-gray-400 focus:border-indigo-500 focus:outline-none"
      />

      <label for="password" class="mb-1 block text-sm text-gray-300">Password</label>
      <div class="mb-1">
        <PasswordInput id="password" v-model="password" autocomplete="new-password" :minlength="8" />
      </div>
      <p v-if="passwordError" class="mb-4 text-sm text-red-400">{{ passwordError }}</p>
      <div v-else class="mb-4" />

      <label for="confirmPassword" class="mb-1 block text-sm text-gray-300">Confirm Password</label>
      <div class="mb-1">
        <PasswordInput
          id="confirmPassword"
          v-model="confirmPassword"
          autocomplete="new-password"
          :minlength="8"
          :has-error="passwordMismatch"
        />
      </div>
      <p v-if="passwordMismatch" class="mb-4 text-sm text-red-400">Passwords do not match</p>
      <div v-else class="mb-4" />

      <button
        type="submit"
        :disabled="loading || !formValid"
        class="w-full rounded bg-indigo-600 py-2 font-semibold text-white hover:bg-indigo-500 disabled:opacity-50"
      >
        {{ loading ? 'Creating account...' : 'Sign Up' }}
      </button>

      <p class="mt-4 text-center text-sm text-gray-400">
        Already have an account?
        <RouterLink to="/login" class="text-indigo-400 hover:underline">Sign in</RouterLink>
      </p>
    </form>
  </main>
</template>
