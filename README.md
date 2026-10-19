# Rehearse — AI mock interview front end

Next.js 16 (App Router) · React 19 · TypeScript · Tailwind CSS v4.

## Run

```bash
cp .env.example .env.local   # set BACKEND_URL if the API isn't on :8081
npm install
npm run dev
```

The browser calls `/backend/*`; `next.config.ts` rewrites it to `BACKEND_URL` (+ optional `BACKEND_API_PREFIX`). Backend: `ai-interview-dev`, default port 8081.

## Structure

```
src/
  app/
    (marketing)/   landing
    (auth)/        login, register (2-step)
    (app)/         dashboard, interview, feedback/[id]  (behind AuthGuard)
  components/
    ui/            button, field, primitives (design system)
    layout/        logo, app header, auth guard
    features/      interview list, recorder, feedback report
  hooks/           use-recorder (mic -> WAV), use-speech (TTS)
  lib/             api client, wav encoder, constants, utils
  providers/       session (localStorage via useSyncExternalStore)
  types/
```

## Flow

Landing → Register / Sign in → Dashboard → Interview (10 spoken questions) → "Get my feedback" (generated once, saved) → `/feedback/:id`, also reachable from history.

## Design

Warm paper background, ink text, one forest-green accent; light and dark follow the OS. Serif headings (Newsreader), Inter body.
