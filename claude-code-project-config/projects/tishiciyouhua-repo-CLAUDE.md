# tishiciyouhua_repo

提示词优化工具 — Expo 54 + React Native 应用。

## Tech Stack

- **Framework:** Expo 54 + React Native 0.81
- **Backend:** Supabase
- **AI:** Anthropic API
- **State:** Zustand
- **Build:** Expo (Android/iOS)

## Architecture

```
app/              → Expo Router pages
  (tabs)/         → Tab navigation
  refine/         → Prompt refinement pages
src/
  components/
    tools/        → Tool sections (3 tools)
  config/         → App config
  constants/      → Constants
  hooks/          → Custom hooks
  lib/            → API clients (Anthropic, Supabase, clipboard)
  store/          → Zustand stores
  types/          → Shared types
```

## Common Commands

```bash
npx expo start         # Dev server
npx expo start --android  # Android emulator
npx expo start --ios   # iOS simulator
npx expo run:android   # Build + install Android
```

## Note

This is the refactored version. The original is at `~/InsightFlow/`.

> Detailed conventions: [tishiciyouhua rules](../.claude/rules/projects/tishiciyouhua.md)
