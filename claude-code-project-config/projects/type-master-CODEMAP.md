# CODEMAP

## Directory Responsibilities

| Path | Responsibility |
|------|---------------|
| `src/main.tsx` | React entry point |
| `src/App.tsx` | Root component with routing |
| `src/components/practice/` | Typing practice UI (keyboard display, text input) |
| `src/components/game/` | Game mode UI (score, timer, animations) |
| `src/components/progress/` | Statistics charts, progress tracking |
| `src/modules/typing/` | Core typing engine (WPM, accuracy, key detection) |
| `src/modules/audio/` | Sound effect management |
| `src/modules/game/` | Game logic (levels, scoring, timers) |
| `src/modules/statistics/` | Data aggregation, chart data |
| `src/modules/storage/` | localStorage/indexedDB persistence |
| `src/hooks/useTypingEngine.ts` | Main typing interaction hook |
| `src/hooks/useAudio.ts` | Audio playback hook |
| `src/electron/main.ts` | Electron main process |
| `src/electron/preload.ts` | Electron preload script |

## Data Flow: Typing Practice

```
User types → useTypingEngine hook
          → modules/typing/ (key detection, timing)
          → modules/statistics/ (WPM calc, accuracy)
          → store/practiceStore (state update)
          → components/practice/ (re-render UI)
          → modules/storage/ (persist progress)
```

## Store Relationships

`appStore` (global) → `practiceStore` (practice) 
                    → `gameStore` (game mode)
                    → (both read theme/settings from appStore)
