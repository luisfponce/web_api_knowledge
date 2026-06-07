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

## Run With Docker

From the repository root, run the full production-like stack:

```bash
./scripts/run-compose-stack.sh
```

The root startup script runs Docker Compose, waits for service readiness, and verifies frontend, backend, nginx API proxy, and MariaDB connectivity. Manual Compose startup also works with `docker compose up --build -d` or `docker-compose up --build -d`.

The frontend image is built by [`Dockerfile`](Dockerfile). It installs dependencies with `npm ci`, runs `npm run build`, and serves the generated `dist/` files with nginx.

Open the frontend at `http://127.0.0.1:8080`.

In Docker mode, nginx uses [`nginx.conf`](nginx.conf) to:

- Serve the React SPA from `/usr/share/nginx/html`
- Fallback unknown non-API routes to `index.html`
- Proxy `/api/*` requests to the Compose backend service at `http://backend:8000`

The browser still calls the relative default API base URL `/api/v1`. Do not set it to `http://backend:8000`; `backend` is only resolvable inside the Docker network, not from the browser.

The Vite proxy in [`vite.config.ts`](vite.config.ts) is only used by local `npm run dev`. Production Docker serving uses nginx instead.

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
