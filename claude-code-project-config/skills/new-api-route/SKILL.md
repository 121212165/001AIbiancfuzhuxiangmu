# new-api-route

Generate a Next.js App Router API route with validation and error handling.

## Usage

Ask me to create a new API route, specifying:
- Route path (e.g., `/api/projects`)
- HTTP methods needed
- Request/response shape
- Database operations required

## Generated Structure

```
app/api/<route>/
  route.ts         → Route handler with:
                     - Request validation
                     - Auth check (next-auth session)
                     - Error boundary
                     - Proper HTTP status codes
  schema.ts        → Zod validation schemas (optional)
  service.ts       → Business logic (optional, for complex routes)
```

## Conventions

- Always validate input with Zod or manual checks
- Always wrap with try/catch returning `NextResponse`
- Auth check first, validation second, business logic third
- Export named functions for each HTTP method: `GET`, `POST`, `PUT`, `DELETE`
- Use `lib/db.ts` (or prisma client) for database access
