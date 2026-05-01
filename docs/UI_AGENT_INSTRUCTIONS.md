# MythicForge UI — Agent Instructions

This document provides everything an AI agent needs to build and maintain the MythicForge frontend.

---

## 1. Project Context

MythicForge is a Fantasy League of Legends platform. The backend is Python/FastAPI, split into three microservices:

- **Fantasy API** (port 8000) — User auth, fantasy league CRUD, team drafting, scoring
- **Riot Data API** (port 8002) — Read-only esports data (leagues, tournaments, matches, games, teams, players, stats)
- **Riot Scraper** (port 8004) — Background data ingestion (no UI interaction needed)

The UI lives in `ui/` at the repo root, alongside the existing `src/` (Python backend).

---

## 2. Tech Stack

| Layer | Choice | Why |
|---|---|---|
| Framework | Vue 3 (Composition API + `<script setup>`) | Owner's choice |
| Language | TypeScript (strict mode) | Owner's choice |
| Build tool | Vite | Standard for Vue + TS, fast HMR |
| Routing | Vue Router 4 | Official Vue router |
| State management | Pinia | Official Vue store, TS-first |
| HTTP client | Axios | Interceptors for JWT refresh, request/response typing |
| UI component library | PrimeVue 4 (unstyled mode) | Rich component set (data tables, dialogs, forms), good a11y |
| CSS approach | Tailwind CSS + PrimeVue Tailwind preset | Utility-first, consistent design system, AI-friendly |
| Form validation | VeeValidate + Zod | Schema-based validation matching backend Pydantic models |
| Testing | Vitest + Vue Test Utils | Fast, Vite-native unit tests |
| E2E testing | Playwright | Cross-browser, reliable |
| Linting/formatting | ESLint (flat config) + Prettier | Consistent code style |

---

## 3. Project Structure

The UI lives in `ui/` at the repo root. Keep this section updated as the project evolves.

```
ui/
├── src/
│   ├── api/           # Axios client instance and typed API call modules
│   ├── types/         # TypeScript interfaces mirroring backend Pydantic schemas
│   ├── stores/        # Pinia stores (one per domain: auth, fantasy, riot data)
│   ├── router/        # Vue Router config with auth guards
│   ├── composables/   # Reusable composition functions
│   ├── components/    # Reusable Vue components, organized by feature area
│   ├── views/         # Page-level components (one per route)
│   └── utils/         # Formatting, validation helpers
├── tests/
│   ├── unit/          # Vitest
│   └── e2e/           # Playwright
└── (config files: vite, tsconfig, eslint, prettier, playwright at root)
```

**Rules:**
- Components go in feature subdirectories under `components/` (e.g., `components/league/`, `components/team/`). Shared/layout components go in `components/layout/` and `components/common/`.
- Views are flat — one file per route, no nesting.
- Stores, API modules, and types are flat files, not nested directories.

---

## 4. Backend API Reference

All endpoints are prefixed with `/api/v1`. The UI talks to two services.

### Fantasy API (port 8000)

**Auth** — JWT bearer tokens. Login returns a token; include as `Authorization: Bearer <token>` on all protected requests.

| Method | Path | Auth | Purpose |
|---|---|---|---|
| POST | `/user/signup` | No | Create account (`{username, email, password}`) |
| POST | `/user/login` | No | Login (`{username, password}`) → returns JWT |
| PUT | `/user/delete` | Yes | Soft-delete account |
| GET | `/user/verify-email/{token}` | No | Email verification |
| POST | `/user/request-verification-email` | No | Resend verification |

| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET | `/leagues` | Yes | Get user's leagues (pending + accepted) |
| POST | `/leagues` | Yes | Create league (`FantasyLeagueSettings`) |
| GET | `/leagues/{id}/settings` | Yes | Get league settings (owner only) |
| PUT | `/leagues/{id}/settings` | Yes | Update league settings (owner only) |
| GET | `/leagues/{id}/scoring` | Yes | Get scoring settings |
| PUT | `/leagues/{id}/scoring` | Yes | Update scoring settings |
| POST | `/leagues/{id}/invite/{username}` | Yes | Invite user |
| POST | `/leagues/{id}/join` | Yes | Accept invite |
| POST | `/leagues/{id}/leave` | Yes | Leave league |
| POST | `/leagues/{id}/revoke/{userId}` | Yes | Revoke member (owner only) |
| GET | `/leagues/{id}/draft-order` | Yes | Get draft order |
| PUT | `/leagues/{id}/draft-order` | Yes | Update draft order (owner only) |

| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET | `/teams/{leagueId}` | Yes | Get user's team by week |
| PUT | `/teams/{leagueId}/pickup/{playerId}` | Yes | Pick up player |
| PUT | `/teams/{leagueId}/drop/{playerId}` | Yes | Drop player |
| PUT | `/teams/{leagueId}/swap/{dropId}/{pickupId}` | Yes | Swap players |

### Riot Data API (port 8002)

Uses the same JWT from the Fantasy API for auth.

| Resource | Endpoints |
|---|---|
| Leagues | GET `/leagues`, GET `/leagues/{id}` |
| Tournaments | GET `/tournaments`, GET `/tournaments/{id}` |
| Matches | GET `/matches`, GET `/matches/{id}` |
| Games | GET `/games`, GET `/games/{id}` |
| Game Stats | GET `/game-stats/{gameId}` |
| Teams | GET `/teams`, GET `/teams/{id}` |
| Players | GET `/players`, GET `/players/{id}` |

All list endpoints support pagination via `fastapi-pagination` (query params: `page`, `size`).

### Key Data Models

These TypeScript interfaces must mirror the backend Pydantic schemas exactly:

```typescript
// riot.ts
interface League {
  id: string;
  slug: string;
  name: string;
  region: string;
  image: string;
  priority: number;
  fantasy_available: boolean;
}

interface Tournament {
  id: string;
  slug: string;
  start_date: string;
  end_date: string;
  league_id: string;
}

interface Match {
  id: string;
  start_time: string;
  block_name: string;
  league_slug: string;
  strategy_type: string;
  strategy_count: number;
  tournament_id: string;
  team_1_name: string;
  team_2_name: string;
  has_games: boolean;
  state: 'completed' | 'inProgress' | 'unstarted';
  team_1_wins: number | null;
  team_2_wins: number | null;
  winning_team: string | null;
}

interface ProfessionalTeam {
  id: string;
  slug: string;
  name: string;
  code: string;
  image: string;
  alternative_image: string | null;
  background_image: string | null;
  status: string;
  home_league: string | null;
}

interface ProfessionalPlayer {
  id: string;
  summoner_name: string;
  image: string;
  role: 'top' | 'jungle' | 'mid' | 'bottom' | 'support' | 'none';
  team_id: string;
}

interface PlayerGameData {
  game_id: string;
  player_id: string;
  participant_id: number;
  champion_id: string;
  role: string;
  kills: number;
  deaths: number;
  assists: number;
  total_gold: number;
  creep_score: number;
  kill_participation: number;
  champion_damage_share: number;
  wards_placed: number;
  wards_destroyed: number;
}

// fantasy.ts
interface UserCreate {
  username: string;  // min 3 chars
  email: string;
  password: string;  // min 8 chars
}

interface FantasyLeagueSettings {
  name: string;
  number_of_teams: 4 | 6 | 8 | 10;
  available_leagues: string[];
}

interface FantasyLeague extends FantasyLeagueSettings {
  id: string;
  owner_id: string;
  status: 'pre-draft' | 'draft' | 'active' | 'completed' | 'deleted';
  current_week: number | null;
  current_draft_position: number | null;
}

interface FantasyLeagueScoringSettings {
  fantasy_league_id: string | null;
  kills: number;
  deaths: number;
  assists: number;
  creep_score: number;
  wards_placed: number;
  wards_destroyed: number;
  kill_participation: number;
  damage_percentage: number;
}

interface FantasyTeam {
  fantasy_league_id: string;
  user_id: string;
  week: number;
  top_player_id: string | null;
  jungle_player_id: string | null;
  mid_player_id: string | null;
  adc_player_id: string | null;
  support_player_id: string | null;
}
```

---

## 5. Standards and Practices

### TypeScript
- Enable `strict: true` in `tsconfig.json`. No `any` types — use `unknown` and narrow.
- All API responses must be typed. No untyped data flows from API to component.
- Use discriminated unions for state that can be loading/success/error.

### Vue Components
- Use `<script setup lang="ts">` exclusively. No Options API.
- Props must be typed with `defineProps<{}>()`. Emits with `defineEmits<{}>()`.
- Keep components focused: if a component exceeds ~150 lines, extract sub-components.
- Use `v-model` for two-way binding on form inputs.

### CSS and Styling
- **Tailwind utility classes in templates are the default.** All styling should be done with Tailwind classes directly on elements.
- **No inline styles** (`style="..."`) except for truly dynamic values that must be computed at runtime (e.g., `style` bindings for calculated widths or positions).
- **No `<style>` blocks by default.** Only add a scoped `<style>` block when Tailwind genuinely can't handle the case: complex keyframe animations, overriding third-party component internals, or CSS features with no Tailwind equivalent.
- **`@apply` is discouraged.** If you find yourself writing `@apply` to group utilities, extract a Vue component instead. The component *is* the abstraction.
- **PrimeVue must be configured in unstyled mode** with the official Tailwind preset so that PrimeVue components are styled via Tailwind, not PrimeVue's built-in theme CSS.
- **Use Tailwind's design tokens consistently.** Stick to the default spacing scale, color palette, and breakpoints. Extend the Tailwind config for project-specific tokens (brand colors, etc.) rather than using arbitrary values (`w-[347px]`).
- **Responsive design uses Tailwind breakpoint prefixes** (`sm:`, `md:`, `lg:`), mobile-first.
- **Dark mode:** If implemented, use Tailwind's `dark:` variant with class-based toggling.

### State Management (Pinia)
- One store per domain: `auth`, `fantasyLeague`, `riotData`.
- Stores handle API calls and caching. Components never call `axios` directly.
- Use `storeToRefs()` for reactive destructuring in components.

### API Layer
- Single Axios instance in `api/client.ts` with:
  - `baseURL` from environment variable
  - Request interceptor that attaches the JWT from the auth store
  - Response interceptor that handles 401 → redirect to login
- Each API module (`fantasyApi.ts`, `riotApi.ts`) exports typed functions, not raw Axios calls.

### Routing and Auth Guards
- Public routes: `/`, `/login`, `/signup`, `/verify-email/:token`
- Protected routes: everything else. Use a `beforeEach` navigation guard that checks the auth store.
- Redirect unauthenticated users to `/login` with a `redirect` query param to return them after login.

### Error Handling
- API errors should be caught in stores/composables, not in components.
- Display user-friendly error messages via a toast/notification system (PrimeVue Toast).
- Log detailed errors to console in development only.

### Forms and Validation
- Use VeeValidate with Zod schemas that match backend validation rules:
  - Username: min 3 characters
  - Password: min 8 characters
  - Email: valid email format
  - `number_of_teams`: must be 4, 6, 8, or 10
- Show inline validation errors. Disable submit buttons while invalid or submitting.

### Accessibility
- All interactive elements must be keyboard navigable.
- Use semantic HTML (`<nav>`, `<main>`, `<section>`, `<button>` not `<div @click>`).
- Images require `alt` text. Decorative images use `alt=""`.
- Form inputs must have associated `<label>` elements.
- Color contrast must meet WCAG 2.1 AA (4.5:1 for text).
- PrimeVue components handle most of this — don't override their ARIA attributes.

### Testing
- **Unit tests (Vitest):** Test stores, composables, and component logic. Mock API calls.
- **E2E tests (Playwright):** Cover critical user flows — signup, login, create league, draft player.
- Aim for tests on every store action and every form submission flow.
- Run `vitest` in CI. Run Playwright against a local Docker stack.

### Code Quality
- ESLint with `@vue/eslint-config-typescript` and `eslint-plugin-vue` (recommended rules).
- Prettier for formatting (2-space indent, single quotes, trailing commas).
- No `console.log` in production code — use a logger utility or remove before commit.
- No commented-out code in commits.

### Environment Configuration
- Use Vite env files (`.env`, `.env.development`, `.env.production`).
- Required variables:
  ```
  VITE_FANTASY_API_URL=http://localhost:8000/api/v1
  VITE_RIOT_API_URL=http://localhost:8002/api/v1
  ```
- Access via `import.meta.env.VITE_FANTASY_API_URL`. Never hardcode URLs.

### Performance
- Lazy-load route components with `() => import('./views/SomeView.vue')`.
- Paginate all list views (players, matches, tournaments). Don't fetch everything at once.
- Use `keep-alive` on frequently revisited views (dashboard, league detail).
- Debounce search inputs (300ms).

### Git and CI
- UI changes go on feature branches, PRs to `main`.
- CI pipeline should: install → lint → type-check (`vue-tsc --noEmit`) → unit test → build.
- The `ui/` directory is independent from the Python backend — separate `package.json`, separate build.

---

## 6. Docker Integration

Add a `ui` service to `docker-compose.local.yml`:

```yaml
ui:
  build:
    context: ..
    dockerfile: docker-files/Dockerfile-ui
  ports:
    - "3000:80"
  depends_on:
    - fantasy-app
    - riot-app
```

The Dockerfile should be a multi-stage build:
1. **Build stage:** Node 20 Alpine, `npm ci`, `npm run build`
2. **Serve stage:** Nginx Alpine serving the `dist/` folder with a config that proxies `/api` to the backend services or serves the SPA with history mode fallback.

---

## 7. Key UX Flows to Implement

1. **Signup → Email Verification → Login** — Full onboarding flow
2. **Dashboard** — List of user's fantasy leagues (pending invites + active)
3. **Create League** — Form with name, team count, available riot leagues picker
4. **League Detail** — Tabs for roster, standings, settings, scoring, members, draft order
5. **Team Management** — View weekly roster, pick up / drop / swap players
6. **Player Browser** — Searchable, filterable table of pro players with stats
7. **Match Browser** — View upcoming and completed matches with scores

---

## 8. Naming Conventions

| Item | Convention | Example |
|---|---|---|
| Vue files | PascalCase | `LeagueCard.vue` |
| TS files | camelCase | `fantasyApi.ts` |
| Components | PascalCase in templates | `<LeagueCard />` |
| Props/emits | camelCase | `leagueId`, `onUpdate` |
| API response fields | snake_case (match backend) | `fantasy_league_id` |
| Store IDs | camelCase | `useAuthStore` |
| CSS classes | kebab-case (scoped) | `.league-card` |
| Env vars | SCREAMING_SNAKE prefixed with VITE_ | `VITE_FANTASY_API_URL` |
| Test files | `*.spec.ts` or `*.test.ts` | `auth.spec.ts` |
