# type-master

金山打字通复刻版 — 现代打字练习桌面应用。

## Tech Stack

- **Frontend:** Vite 6 + React 19 + TypeScript 5.9 + Tailwind 4
- **Desktop:** Electron 40
- **State:** Zustand 5 (3 stores)
- **UI:** Ant Design 6, ECharts 6
- **Game:** Phaser 3
- **Testing:** Vitest 4 + Playwright

## Architecture

```
src/
  components/     → UI components
    common/       → Shared UI (buttons, modals, layouts)
    practice/     → Typing practice UI
    game/         → Game mode UI
    progress/     → Progress/stats UI
  modules/        → Domain logic
    typing/       → Typing engine, key detection
    audio/        → Sound effects
    game/         → Game mechanics
    statistics/   → Stats tracking
    storage/      → Local data persistence
  hooks/          → React hooks (useTypingEngine, useAudio)
  store/          → Zustand stores
  types/          → TypeScript types
  styles/         → Global CSS
  electron/       → Electron main + preload
```

## Common Commands

```bash
npm run dev          # Vite dev server (HMR)
npm run build        # tsc + vite build
npm run electron:dev # Dev with Electron
npm run electron:build # Package desktop app
npm run test         # Vitest
npm run test:e2e     # Playwright E2E
```

## State Management (Zustand)

- `appStore`: global app state (theme, settings)
- `gameStore`: game mode state (score, level, timer)
- `practiceStore`: practice session state (text, progress, stats)

## Code Conventions

- Components in PascalCase, organized by feature in `components/`
- Business logic in `modules/`, not in components
- Zustand stores in `store/` with clear slice separation
- Custom hooks for reusable stateful logic (`useTypingEngine`)
- Tests alongside source: `src/**/*.test.ts`

## Project Status

Actively developed. Electron packaging configured with `electron-builder`.

> Detailed conventions: [type-master rules](../.claude/rules/projects/type-master.md)
