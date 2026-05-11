# new-electron-feature

Add a desktop feature to type-master (Electron + Vite + React).

## Key Architecture

- Main process: `src/electron/main.ts` — system-level APIs (file, window, menu)
- Preload: `src/electron/preload.ts` — exposed to renderer via contextBridge
- Renderer: `src/` — React components, hooks, Zustand stores
- Communication: IPC via `contextBridge` + `ipcRenderer.invoke`

## Adding a Main-Process Feature

1. Add IPC handler in `src/electron/main.ts`
2. Expose API in `src/electron/preload.ts` via `contextBridge`
3. Create React hook in `src/hooks/` to wrap the IPC call
4. Use hook in component

## Adding a Renderer Feature

1. Business logic in `src/modules/<domain>/`
2. State in `src/store/` (Zustand)
3. UI in `src/components/<feature>/`
4. Hook in `src/hooks/` if needed

## Patterns

- Zustand store: `create<StoreType>()(set => ({...}))`
- Component: `function FeatureName() { ... }` with named export
- Module: pure functions, no React dependency
- Access Electron API: `window.electronAPI.<method>()` (typed in `types/`)
