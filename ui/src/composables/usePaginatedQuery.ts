import { ref, watch, type Ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { PaginatedResponse } from '../api/client'

type ApiFn<T> = (params: Record<string, unknown>) => Promise<PaginatedResponse<T>>

export function usePaginatedQuery<T>(apiFn: ApiFn<T>, filters: Ref<Record<string, string | undefined>>) {
  const route = useRoute()
  const router = useRouter()

  const data = ref<T[]>([]) as Ref<T[]>
  const loading = ref(false)
  const error = ref<string | null>(null)
  const totalPages = ref(0)
  const currentPage = ref(Number(route.query.page) || 1)
  const pageSize = ref(Number(route.query.size) || 20)

  let debounceTimer: ReturnType<typeof setTimeout> | null = null

  async function fetch() {
    loading.value = true
    error.value = null
    try {
      const params: Record<string, unknown> = {
        page: currentPage.value,
        size: pageSize.value,
      }
      for (const [key, val] of Object.entries(filters.value)) {
        if (val) params[key] = val
      }
      const result = await apiFn(params)
      data.value = result.items
      totalPages.value = result.pages
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Request failed'
    } finally {
      loading.value = false
    }
  }

  function syncToUrl() {
    const query: Record<string, string> = { page: String(currentPage.value), size: String(pageSize.value) }
    for (const [key, val] of Object.entries(filters.value)) {
      if (val) query[key] = val
    }
    router.replace({ query })
  }

  watch([currentPage, pageSize], () => {
    syncToUrl()
    fetch()
  })

  watch(filters, () => {
    if (debounceTimer) clearTimeout(debounceTimer)
    debounceTimer = setTimeout(() => {
      currentPage.value = 1
      syncToUrl()
      fetch()
    }, 300)
  }, { deep: true })

  // Initial fetch
  fetch()

  return { data, loading, error, totalPages, currentPage, pageSize }
}
