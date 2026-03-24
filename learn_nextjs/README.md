# learn_nextjs

A modern Next.js frontend implementation demonstrating best practices for building production-grade web applications.

## Overview

This module showcases a complete Next.js 15 setup with:

- **App Router** — modern file-based routing
- **TypeScript** — full type safety
- **Tailwind CSS** — utility-first styling
- **ESLint + Prettier** — code quality and formatting
- **React 19** — latest React features

## Project Structure

```text
learn_nextjs/
├── src/
│   ├── app/               # App Router pages and layouts
│   ├── components/        # Reusable React components
│   ├── lib/               # Utility functions and helpers
│   ├── styles/            # Global and shared styles
│   └── types/             # TypeScript type definitions
├── public/                # Static assets
├── .vscode/               # VSCode workspace settings
├── eslint.config.mjs      # ESLint configuration
├── next.config.ts         # Next.js configuration
├── postcss.config.mjs      # PostCSS configuration (Tailwind)
├── tailwind.config.ts      # Tailwind CSS configuration
├── tsconfig.json          # TypeScript configuration
├── package.json           # Dependencies and scripts
├── pnpm-lock.yaml         # Locked dependencies
└── README.md              # This file
```

## Key Features

### Pages & Routing

Built with Next.js App Router, enabling:

- File-based routing (`src/app/`)
- Nested layouts and template inheritance
- Route handlers for API endpoints
- Dynamic segments with `[id]` patterns

### Styling

- **Tailwind CSS 4** for utility-first styling
- **PostCSS** for advanced CSS processing
- **Prettier plugin** for automatic class sorting

### Code Quality

- **ESLint 9** with Next.js & React plugins
- **TypeScript** for type-safe development
- **Prettier** for consistent code formatting
- **React Compiler** (experimental) for auto-optimizations

### API Integration

Designed to consume the FastAPI backend at:

- **Base URL**: `http://localhost:8000/api`
- **Version**: `latest` (via `/latest/...` paths)

## Setup

### Prerequisites

- **pnpm** (or npm/yarn)
- **Node.js** 18+

### Installation

Dependencies are already installed via `pnpm install`.

To reinstall or update:

```bash
pnpm install
```

## Development

Run the development server:

```bash
pnpm dev
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

### Linting & Formatting

Check for lint issues:

```bash
pnpm lint
```

Format code with Prettier:

```bash
pnpm format
```

## Environment Variables

Create a `.env.local` file for environment-specific configuration:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api
```

**Note**: Variables prefixed with `NEXT_PUBLIC_` are exposed to the browser.

## API Client Integration

To communicate with the FastAPI backend, use the `fetch` API or a library like:

- **Fetch** (built-in, recommended)
- **Axios** (if you prefer)

Example with fetch:

```typescript
const response = await fetch(
  `${process.env.NEXT_PUBLIC_API_BASE_URL}/latest/items`,
  {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  }
);
```

## Comparison: Streamlit vs Next.js

| Aspect | Streamlit | Next.js |
|--------|-----------|---------|
| **Use Case** | Data dashboards, prototypes | Production web apps |
| **Development Speed** | Very fast | Moderate |
| **Customization** | Limited | Highly customizable |
| **Performance** | Good for dashboards | Optimized for web |
| **Deployment** | Simple (Streamlit Cloud) | Flexible (Vercel, Docker, etc.) |
| **Styling** | Built-in, minimal | Full CSS framework support |
| **SEO** | Limited | Excellent (SSR, metadata) |

## Resources

- [Next.js Official Docs](https://nextjs.org/docs)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [TypeScript Handbook](https://www.typescriptlang.org/docs)
- [ESLint Configuration](https://eslint.org/docs/latest/use/configure)

## Running Alongside FastAPI

Start the FastAPI backend:

```bash
uv run run-api-server
```

Then start Next.js dev server in another terminal:

```bash
cd learn_nextjs && pnpm dev
```

Both will be available:

- **FastAPI**: `http://localhost:8000` (API at `/api/latest`)
- **Next.js**: `http://localhost:3000` (frontend)

## Notes

- **Canary Build**: This uses a Next.js canary version. Upgrade path: `pnpm upgrade next@latest`
- **Build Scripts**: Some packages (sharp, @tailwindcss/oxide) have build steps disabled. Run `pnpm approve-builds` if needed.
- **Type Safety**: All components are fully typed with TypeScript.
