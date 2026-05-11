# image-gen-saas Coding Conventions

## API Routes (`app/api/`)

- Export named functions per HTTP method: `export async function GET(req, { params })`, `POST`, `PATCH`, `DELETE`
- Dynamic params: `{ params }: { params: Promise<{ id: string }> }` with `await params`
- Always start with `const session = await getServerSession(authOptions)` then null-check
- Return `NextResponse.json({ error: 'message' }, { status: 4xx })` on failures
- Wrap handler body in try/catch with generic error fallback
- Use `console.error('context:', error)` for server logging

## Prisma Schema

- Models: PascalCase singular (`GeneratedImage`, `UsageRecord`)
- IDs: `String @id @default(cuid())`
- Column mapping: `@map("snake_case_field")`, `@@map("snake_case_table")`
- Timestamps: `createdAt` / `updatedAt` with `@default(now())` / `@updatedAt`
- JSON fields: `Json?`, Decimal: `@db.Decimal(10, 2)`
- Add `@@index([field])` on query-critical columns

## Components

- `'use client'` directive at top
- `export default function ComponentName({ ...props }: Props)`
- `interface ComponentNameProps { ... }` above component
- Path alias: `@/lib/*`, `@/components/*`

## AI Services (`lib/ai-services/`)

- `types.ts` defines `interface AIService { generateImage(params): Promise<result> }`
- Each provider in own file, implements `AIService`
- `index.ts` exports `getAIService(id)` factory + `listAIServices()` for UI
- API keys checked at construction time
- Fallback provider returns SVG on failure, never throws

## Naming

| Context | Style | Example |
|---------|-------|---------|
| Models, components, classes | PascalCase | `StabilityAIService` |
| Variables, functions, fields | camelCase | `imageUrl`, `modelUsed` |
| API dirs | kebab-case | `[...nextauth]`, `generate` |
| Env vars | SCREAMING_SNAKE_CASE | `PIAPI_API_KEY` |
