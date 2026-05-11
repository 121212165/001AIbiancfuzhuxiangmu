# image-gen-saas

Next.js 16 AI image generation SaaS.

## Tech Stack

- **Framework:** Next.js 16 (App Router) + React 19 + TypeScript
- **Database:** PostgreSQL via Prisma 7
- **Auth:** NextAuth v5 + Prisma Adapter
- **Storage:** Vercel Blob
- **AI APIs:** PiAPI, Stability AI
- **Styling:** Tailwind CSS 4
- **Testing:** Vitest + Testing Library
- **Deploy:** Vercel

## Architecture

```
app/              → App Router pages + API routes
  api/auth/       → NextAuth handlers
  api/images/     → Image generation CRUD
  api/user/       → User/register/usage
components/       → Shared React components
lib/
  ai-services/    → AI provider integrations (piapi, stability-ai, fallback)
  auth.ts         → NextAuth config
  blob-storage.ts → Vercel Blob client
prisma/
  schema.prisma   → DB schema (7 models)
```

## Common Commands

```bash
npm run dev       # Start dev server
npm run build     # Production build  
npm run test      # Vitest
npx prisma studio # DB admin UI
npx prisma db push  # Sync schema to dev DB
npx prisma migrate dev  # Create migration
```

## DB Models

User, SubscriptionPlan, GeneratedImage, UsageRecord, Payment, Account, Session, VerificationToken

## Code Conventions

- API routes in `app/api/` with `route.ts`
- Components in `components/` with PascalCase
- Business logic in `lib/`, not in route handlers
- AI providers abstracted behind `lib/ai-services/` interface
- Use `next-auth` session for user context

> Detailed conventions: [image-gen-saas rules](../.claude/rules/projects/image-gen-saas.md)
