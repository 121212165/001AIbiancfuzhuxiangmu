# ai-support-group Coding Conventions

## Prisma Schema

- SQLite provider
- IDs: `String @id @default(cuid())`
- Timestamps: `@map("created_at")` / `@map("updated_at")`
- Table mapping: `@@map("snake_case_plural")`
- Cascade delete on foreign keys
- Relation fields alongside scalar fields

## API Routes

- Named exports: `export async function GET(req)`, `POST`
- Always start with `const user = await requireAuth()` from `src/lib/auth.ts`
- Guard: `if (!user) return NextResponse.json({ error: '...' }, { status: 401 })`
- Wrap in try/catch: `catch (error) { console.error('...', error); return NextResponse.json({ error: '...' }, { status: 500 }) }`
- Error messages in Chinese

## Components

- `export default function ComponentName({ ... }: Props)`
- `interface Props { ... }` at component level
- Tailwind CSS for styling
- Conditional rendering: `{onDismiss && (...)}`

## Auth

- Centralized `requireAuth()` returns user or null
- `src/lib/db.ts`: singleton Prisma client via `globalThis` cache
- Zod validation where input parsing is needed
