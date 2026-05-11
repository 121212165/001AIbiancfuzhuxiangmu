# ai-support-group

AI-assisted sobriety support group — Next.js 15 app with gamification.

## Tech Stack

- **Framework:** Next.js 15 (App Router) + React 19 + TypeScript 5
- **Database:** SQLite via Prisma 6
- **Auth:** SecondMe identity/auth service
- **Styling:** Tailwind CSS 3
- **Deploy:** Vercel

## Architecture

```
src/
  app/            → Pages + API routes
    dashboard/    → Stats, leaderboard, messages
    checkin/      → Daily check-in
    crisis/       → Crisis support
    api/auth/     → Login/logout/callback/me
    api/checkin/  → Check-in CRUD
    api/crisis/   → Crisis request
    api/dashboard/→ Dashboard data
  components/     → Shared UI
  lib/
    auth.ts       → SecondMe auth integration
    db.ts         → Prisma client
    secondme.ts   → SecondMe API client
prisma/
  schema.prisma   → DB schema
```

## Common Commands

```bash
npm run dev          # Next.js dev server
npm run build        # Build (prebuild: prisma generate)
npm run lint         # ESLint
npx prisma studio    # DB admin
npx prisma db push   # Sync schema
```

## DB Models

User (sobriety days, crisis count), CheckIn (daily mood), Crisis (help requests), Message (chat), Achievement, UserAchievement

## Code Conventions

- App Router with `page.tsx` and `route.ts`
- Server components by default, client components with `"use client"`
- Prisma for all DB access via `lib/db.ts`
- Chinese comments in schema, English in code

> Detailed conventions: [ai-support-group rules](../.claude/rules/projects/ai-support-group.md)
