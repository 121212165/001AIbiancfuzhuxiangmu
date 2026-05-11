# type-master Coding Conventions

## Electron IPC (`src/electron/`)

- `contextIsolation: true`, `nodeIntegration: false`
- `ipcMain.handle('channel', handler)` in main.ts
- `contextBridge.exposeInMainWorld('electronAPI', { ... })` in preload.ts
- Renderer calls: `window.electronAPI.methodName(args)`

## Zustand Stores (`src/store/`)

- Interface-first pattern: `interface StoreState { data; actions }`
- `create<StoreState>()(set => ({ initialState, ... }))`
- Immutable updates: `set(state => ({ field: { ...state.field, update } }))`
- Persist with `persist` middleware + `partialize` to whitelist fields
- Async actions: `async/await` inside setter

## React Hooks (`src/hooks/`)

- Wrap class instances in `useRef` (not `useState`)
- Subscribe events in `useEffect` with cleanup return
- Expose methods via `useCallback`
- Return `{ stateValues, methods }` object

## Components (`src/components/`)

- PascalCase files matching component name
- `export const Name: React.FC<Props> = ({ ... }) => { ... }`
- `interface NameProps { ... }` above component
- CSS colocated as `.css` in same directory
- Group by feature: `common/`, `practice/`, `game/`, `progress/`

## Modules (`src/modules/`)

- One file per domain: `TypingEngine.ts`, `AudioManager.ts`
- Class implements interface from `@/types/api`
- EventEmitter base for runtime modules
- IndexedDB via `IndexedDBHelper` wrapper
- Tests co-located: `__tests__/ModuleName.spec.ts`
