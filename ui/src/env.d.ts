/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_FANTASY_API_URL: string
  readonly VITE_RIOT_API_URL: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
