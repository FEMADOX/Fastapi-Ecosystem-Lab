# learn_nextjs

A modern Next.js frontend implementation demonstrating best practices for building production-grade web applications.

## Table of Contents

- [learn\_nextjs](#learn_nextjs)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Project Structure](#project-structure)
  - [Key Features](#key-features)
    - [Authentication](#authentication)
    - [Server Actions](#server-actions)
    - [Caching with `use cache`](#caching-with-use-cache)
    - [Server-only Fetch Layer](#server-only-fetch-layer)
    - [Pages \& Routing](#pages--routing)
    - [Styling](#styling)
    - [Code Quality](#code-quality)
  - [Setup](#setup)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
  - [Development](#development)
    - [Build for Production](#build-for-production)
    - [Start Production Server](#start-production-server)
    - [Linting](#linting)
  - [Testing](#testing)
    - [What is tested](#what-is-tested)
  - [Environment Variables](#environment-variables)
  - [Architecture Notes](#architecture-notes)
  - [Running Alongside FastAPI](#running-alongside-fastapi)
  - [Comparison: Streamlit vs Next.js](#comparison-streamlit-vs-nextjs)
  - [Resources](#resources)

## Overview

This module showcases a complete Next.js 16 (canary) setup with:

- **App Router** — modern file-based routing with nested layouts
- **TypeScript** — full type safety throughout
- **Tailwind CSS 4** — utility-first styling
- **ESLint 9 + StandardJS** — code quality and style consistency
- **React 19** — latest React features including `useActionState`
- **Zod v4** — runtime schema validation
- **Server Actions** — form submissions handled server-side
- **`use cache` directive** — fine-grained caching with `cacheTag`/`cacheLife`
- **Vitest** — fast unit testing

## Project Structure

```text
learn_nextjs/
├── src/
│   ├── actions/           # Server Actions ('use server')
│   │   ├── auth/          # loginAction, registerAction, logoutAction
│   │   └── items/         # createItemAction
│   ├── app/               # App Router pages and layouts
│   │   ├── (auth)/        # Route group: login, signup pages + AuthForm
│   │   ├── api/           # Route handlers + server-only fetch layer
│   │   ├── components/    # Server Components (NavBar, LogoutGroup)
│   │   ├── hooks/         # Client hooks (useAuth)
│   │   ├── items/         # Items listing and detail pages
│   │   └── utils/         # Form input validators (Zod preprocessors)
│   ├── common/            # Shared constants, types, and Zod schemas
│   ├── components/        # Reusable UI components (shadcn/ui based)
│   ├── lib/               # Utility functions (cn)
│   ├── schemas/           # Zod form schemas per feature
│   └── types/             # TypeScript type definitions per domain
├── public/                # Static assets
├── eslint.config.mjs      # ESLint flat config
├── vitest.config.ts       # Vitest configuration
├── next.config.ts         # Next.js configuration
├── postcss.config.mjs     # PostCSS configuration (Tailwind)
├── tsconfig.json          # TypeScript configuration
├── package.json           # Dependencies and scripts
└── proxy.ts               # Middleware (JWT-based route protection)
```

## Key Features

### Authentication

JWT-based authentication backed by a FastAPI backend:

- Cookies `access_token` and `refresh_token` are set server-side via **Server Actions**
- **Middleware** (`proxy.ts`) protects routes before rendering: checks JWT validity, redirects unauthenticated users to `/login?next=<path>`
- Auth-only routes (`/login`, `/signup`) redirect already-authenticated users to `/`
- `AuthForm` — shared Client Component for login and signup, with client-side Zod validation before dispatching the Server Action

### Server Actions

Form submissions bypass the client-fetch layer entirely:

- `loginAction` / `registerAction` — parse `FormData`, validate with Zod, call FastAPI directly, set cookies, redirect
- `createItemAction` — verifies user identity, validates item form, creates item, revalidates `items` cache tag
- All actions use `(prevState, formData) => Promise<State>` signature compatible with `useActionState`

### Caching with `use cache`

Data-fetching functions use the experimental `'use cache'` directive:

- `cookies()` is read **outside** the cached function and passed as `accessToken` argument — required because dynamic data sources cannot be called inside a `'use cache'` scope
- Cache entries are tagged with `cacheTag('items')` / `cacheTag('item-{id}')` and invalidated via `revalidateTag` after mutations

### Server-only Fetch Layer

`src/app/api/server-fetch.ts` provides typed wrappers (`serverGet`, `serverPost`, etc.) that:

- Call the FastAPI backend directly (no loopback through Next.js API routes)
- Accept an optional `accessToken` parameter for authenticated requests
- Return `ApiProxyResponse<T>` with typed `data` and `error`

### Pages & Routing

- `/` — home page
- `/login` — login form (Server Component wrapping `AuthForm`)
- `/signup` — signup form (Server Component wrapping `AuthForm`)
- `/items` — cached items listing (Server Component with `'use cache'`)
- `/items/[id]` — cached item detail (Server Component with per-item `cacheTag`)
- `/items/new` — protected new item form (Server Action on submit)
- `/api/[...path]` — proxy route handler for client-side API calls

### Styling

- **Tailwind CSS 4** with the `@theme` inline pattern
- **shadcn/ui** component primitives built on Base UI
- **PostCSS** for advanced CSS processing

### Code Quality

- **ESLint 9** flat config with Next.js, React, TypeScript, and StandardJS rules
- **TypeScript strict mode** — no implicit `any`, full inference
- **Prettier** for formatting
- **Vitest** for unit testing

## Setup

### Prerequisites

- **pnpm**
- **Node.js** 20+
- FastAPI backend running (see root `README.md`)

### Installation

```bash
pnpm install
```

## Development

Run the development server:

```bash
pnpm dev
```

Or with `.env` hot-reload:

```bash
pnpm dev:watch
```

The app will be available at `http://localhost:3000`.

### Build for Production

```bash
pnpm build
```

### Start Production Server

```bash
pnpm start
```

### Linting

```bash
pnpm lint          # check
pnpm lint:fix      # auto-fix
```

## Testing

Tests use [Vitest](https://vitest.dev/) with Node environment and `@/` path alias resolution.

```bash
pnpm test            # run all tests once
pnpm test:watch      # watch mode
pnpm test:coverage   # with v8 coverage report
```

### What is tested

| Test file | Covers |
|---|---|
| `src/__tests__/app/getSafeNextPath.test.ts` | Open-redirect prevention, path validation, array input |
| `src/__tests__/app/utils/formInputValidators.test.ts` | `stringFromForm`, `nonNegativeNumberFromForm`, `nullableImageUrlFromForm` |
| `src/__tests__/schemas/auth/parseAuthForm.test.ts` | Auth form parsing for login and signup variants, field error shapes |
| `src/__tests__/schemas/items/itemFormSchema.test.ts` | Item form schema coercion, URL handling, negative/invalid value rejection |
| `src/__tests__/lib/utils.test.ts` | `cn()` class merging and Tailwind conflict resolution |

## Environment Variables

Create a `.env.local` file (see `.env.local.example`):

```env
LEARN_FASTAPI_API_URL=http://localhost:8000/api
SECRET_KEY=your-jwt-secret-key
ENVIRONMENT=development
```

> `SECRET_KEY` must match the FastAPI backend secret used to sign JWT tokens (used by the middleware for verification).

## Architecture Notes

- **`proxy.ts`** — the Next.js middleware file. Exports `proxy` function and `config` matcher. JWT verification uses `jose` (`jwtVerify`). Only expiration errors are allowed through (access token refresh flow handled client-side).
- **`authSchemas`** live in `src/schemas/auth/forms.ts` — imported by both the Client Component (via `parseAuthForm`) and Server Actions (via Zod directly). This avoids passing non-serializable Zod instances across the RSC boundary.
- **`getSafeNextPath`** is a pure function in `src/app/(auth)/getSafeNextPath.ts`, safe to import in Server Actions. The `useSafeNext.ts` hook wraps it for client use and is marked `'use client'`.

## Running Alongside FastAPI

Start the FastAPI backend:

```bash
uv run run-api-server
```

Then start Next.js dev server:

```bash
cd learn_nextjs && pnpm dev:watch
```

Both will be available:

- **FastAPI**: `http://localhost:8000` (API at `/api/latest`)
- **Next.js**: `http://localhost:3000` (frontend)

## Comparison: Streamlit vs Next.js

| Aspect                | Streamlit                   | Next.js                         |
|-----------------------|-----------------------------|---------------------------------|
| **Use Case**          | Data dashboards, prototypes | Production web apps             |
| **Development Speed** | Very fast                   | Moderate                        |
| **Customization**     | Limited                     | Highly customizable             |
| **Performance**       | Good for dashboards         | Optimized for web               |
| **Deployment**        | Simple (Streamlit Cloud)    | Flexible (Vercel, Docker, etc.) |
| **Styling**           | Built-in, minimal           | Full CSS framework support      |
| **SEO**               | Limited                     | Excellent (SSR, metadata)       |

## Resources

- [Next.js Official Docs](https://nextjs.org/docs)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [Zod Docs](https://zod.dev)
- [Vitest Docs](https://vitest.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs)
