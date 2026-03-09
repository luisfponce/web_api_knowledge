# Frontend v1

Minimal React + TypeScript + Vite frontend for login and prompts CRUD.

## Requirements

- Node.js 20.19+ recommended (project can build with warnings on Node 18 in this environment)
- Backend API running at `http://127.0.0.1:8000`

## Run locally

```bash
npm install
npm run dev
```

Vite proxies `/api/*` requests to `http://127.0.0.1:8000` via [`vite.config.ts`](vite.config.ts).

## Scripts

- `npm run dev` start development server
- `npm run build` typecheck and production build
- `npm run lint` run ESLint
- `npm run test` run Vitest tests

## Environment

Optional:

- `VITE_API_BASE_URL=/api/v1`

Default base URL is already `/api/v1` in [`src/lib/http/api-client.ts`](src/lib/http/api-client.ts).

## Architecture summary

- Routing in [`src/app/router.tsx`](src/app/router.tsx)
- Providers in [`src/app/providers.tsx`](src/app/providers.tsx)
- In-memory auth session in [`src/features/auth/auth-store.tsx`](src/features/auth/auth-store.tsx)
- Login + user id resolution in [`src/features/auth/auth-service.ts`](src/features/auth/auth-service.ts)
- Prompts CRUD in [`src/features/prompts/prompts-service.ts`](src/features/prompts/prompts-service.ts)
- Design tokens and themes in [`src/styles/tokens.css`](src/styles/tokens.css), [`src/styles/themes.css`](src/styles/themes.css), and [`src/styles/base.css`](src/styles/base.css)

## UX behavior

- Session is memory-only; page reload requires login again
- `user_id` is resolved after login by calling `/api/v1/users` and matching JWT username
- Prompt list treats backend 404 (`No prompts found`) as empty state
