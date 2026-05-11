# new-image-gen-feature

Add a new feature to the image-gen-saas project (image-gen-saas/next-app/).

## Trigger

When user asks to add a new feature to image-gen-saas (new AI provider, new image style, new pricing tier, etc.)

## Structure

### New AI Provider
1. Create provider file in `lib/ai-services/<name>.ts`
2. Implement the provider interface from `lib/ai-services/types.ts`
3. Register in `lib/ai-services/index.ts` dispatcher
4. Add provider option to `components/ImageGenerator.tsx`
5. Update DB schema if needed (new model/cost fields)

### New API Endpoint
1. Create `app/api/<feature>/route.ts`
2. Add auth check with `getServerSession`
3. Validate input
4. Business logic in a new `lib/<feature>.ts` file
5. Return proper `NextResponse`

### New Page
1. Create `app/<page>/page.tsx`
2. Add link to navigation
3. Use existing components (`AuthShell`, `LoadingSpinner`, `ErrorMessage`)

## Common Patterns

- DB queries via Prisma: `import { prisma } from '@/lib/db'`
- Auth: `import { getServerSession } from 'next-auth'`
- Blob storage: `import { put, del } from '@vercel/blob'`
- Error response: `NextResponse.json({ error: 'message' }, { status: 4xx })`
