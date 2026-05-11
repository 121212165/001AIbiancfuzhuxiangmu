# Project-Specific Coding Rules

These files capture real conventions extracted from the actual project codebases. Each file records what the code already does — naming, patterns, structure — so future work stays consistent.

| File | Project | Extracts patterns from |
|------|---------|----------------------|
| [image-gen-saas.md](image-gen-saas.md) | image-gen-saas/next-app | API routes, Prisma schema, components, AI services |
| [type-master.md](type-master.md) | type-master | IPC, Zustand stores, hooks, components, modules |
| [quant-engine.md](quant-engine.md) | quant-engine | Strategy classes, config YAML, data fetching, backtests |
| [ai-support-group.md](ai-support-group.md) | ai-support-group | Prisma schema, API routes, auth, components |
| [tishiciyouhua.md](tishiciyouhua.md) | tishiciyouhua_repo | React Native components, Zustand, API clients |

## Adding a New Project

1. Scan the project's source files to find real patterns (not hypothetical preferences)
2. Note: naming conventions, file structure, error handling, data flow
3. Create a new `.md` file here
4. Reference from the project's CLAUDE.md
