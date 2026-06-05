# ODIN Operator Console

Next.js 15 observability UI for the Odin runtime. Connects to live backend APIs only (no mocks).

## Prerequisites

- Odin backend running at `http://127.0.0.1:8000`
- Node.js 20+

## Setup

```bash
cd odin/operator
cp .env.local.example .env.local
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) — redirects to `/runtime`.

API calls are proxied via Next.js rewrites (`/api/v1/*` → backend), avoiding CORS.

## Routes

| Path | Feature |
|------|---------|
| `/runtime` | Orchestration dashboard |
| `/missions` | Mission list |
| `/missions/[id]` | Mission timeline viewer |
| `/tasks/[id]` | Task timeline |
| `/graph` | Signal graph (React Flow) |
| `/diagnostics` | Root-cause introspection |
| `/memory` | Memory mutation audit |
| `/traces` | Recent trace index |
| `/traces/[id]` | Causal trace explorer |

## Stack

- Next.js 15 App Router
- TanStack Query (polling)
- Zustand (poll interval / live toggle)
- Tailwind + custom operator theme
- Recharts, React Flow, Framer Motion

## Architecture

```
src/lib/api/       Typed client + runtime endpoints
src/lib/hooks/     React Query hooks with centralized polling
src/lib/graph/     Signal graph → React Flow transform
src/components/    UI by domain
src/app/           App Router pages
```

WebSocket-ready: `createEventSource()` in `lib/api/client.ts` for future SSE wiring.
