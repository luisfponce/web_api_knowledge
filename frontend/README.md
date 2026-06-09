# Frontend

## Overview

This is a React + TypeScript + Vite app for login and prompts CRUD. The API client defaults to the relative base URL `/api/v1`, which works with both the Vite dev proxy and the production nginx proxy.

## Requirements

- Node.js 20.19+ recommended.
- Backend API available at `http://127.0.0.1:8000` for local Vite development.

## Local Development

Run these commands from `frontend/`:

```bash
npm install
npm run dev
```

Vite proxies `/api/*` requests to `http://127.0.0.1:8000` through [`vite.config.ts`](vite.config.ts). This proxy only applies to `npm run dev`.

## Manual Production Build

Run these commands from `frontend/`:

```bash
npm ci
npm run build
npm run preview
```

`npm run preview` serves the built static output for local inspection. It does not replace the production nginx proxy used by the full Docker stack.

## Docker Deployment

For the full production-like stack, run this from the repository root:

```bash
./scripts/run-compose-stack.sh
```

Open the frontend at `http://127.0.0.1:8080`.

To build only the frontend image, run this from `frontend/`:

```bash
docker build -t webapi-frontend:dev .
```

[`Dockerfile`](Dockerfile) uses a Node build stage and an nginx runtime stage. [`nginx.conf`](nginx.conf) serves the React SPA, falls back non-API routes to `index.html`, and proxies `/api/` to the Compose backend service at `http://backend:8000`.

The browser should keep using the relative API base URL `/api/v1`. Do not set a browser-facing API URL to `http://backend:8000`; `backend` is only resolvable inside the Docker network.

## Scripts

- `npm run dev`: start the Vite development server.
- `npm run build`: typecheck and create a production build.
- `npm run lint`: run ESLint.
- `npm run test`: run Vitest tests.
- `npm run preview`: serve the built output locally.

## Environment

Optional:

- `VITE_API_BASE_URL=/api/v1`

The default base URL is already `/api/v1` in [`src/lib/http/api-client.ts`](src/lib/http/api-client.ts).

## Architecture Summary

- Routing: [`src/app/router.tsx`](src/app/router.tsx)
- Providers: [`src/app/providers.tsx`](src/app/providers.tsx)
- In-memory auth session: [`src/features/auth/auth-store.tsx`](src/features/auth/auth-store.tsx)
- Login and user id resolution: [`src/features/auth/auth-service.ts`](src/features/auth/auth-service.ts)
- Prompts CRUD: [`src/features/prompts/prompts-service.ts`](src/features/prompts/prompts-service.ts)
- Design tokens and themes: [`src/styles/tokens.css`](src/styles/tokens.css), [`src/styles/themes.css`](src/styles/themes.css), and [`src/styles/base.css`](src/styles/base.css)

## UX Behavior

- Session is memory-only; page reload requires login again.
- `user_id` is resolved after login by calling `/api/v1/users` and matching the JWT username.
- The prompt list treats backend `404` responses for `No prompts found` as an empty state.
