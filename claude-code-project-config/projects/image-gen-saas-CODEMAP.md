# CODEMAP

## Directory Responsibilities

| Path | Responsibility |
|------|---------------|
| `app/api/auth/[...nextauth]/route.ts` | NextAuth config & handlers |
| `app/api/images/generate/route.ts` | POST: generate image via AI provider |
| `app/api/images/route.ts` | GET: list user's images, POST: create |
| `app/api/images/[id]/route.ts` | GET/DELETE single image |
| `app/api/user/me/route.ts` | Current user profile |
| `app/api/user/register/route.ts` | User registration |
| `app/api/user/usage/route.ts` | Usage quota |
| `components/AuthShell.tsx` | Auth-protected layout wrapper |
| `components/ImageGallery.tsx` | Gallery grid display |
| `components/ImageGenerator.tsx` | Generation form + preview |
| `lib/ai-services/index.ts` | AI provider dispatcher |
| `lib/ai-services/piapi.ts` | PiAPI integration |
| `lib/ai-services/stability-ai.ts` | Stability AI integration |
| `lib/ai-services/fallback.ts` | Fallback logic |
| `lib/auth.ts` | NextAuth config |
| `prisma/schema.prisma` | Database schema |

## Data Flow: Image Generation

```
User → ImageGenerator (form)
     → POST /api/images/generate
     → lib/ai-services/ (choose provider)
     → External AI API
     → Save to Vercel Blob
     → Save GeneratedImage record to DB
     → Return URL to frontend
     → Display in ImageGallery
```

## Key Types

- `GenerateImageInput`: prompt, model, style params
- `GeneratedImage`: id, url, prompt, model, cost, userId
- `User`: auth + subscription fields
- `SubscriptionPlan`: tier, price, limits, stripeId
