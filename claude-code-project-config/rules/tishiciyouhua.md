# tishiciyouhua Coding Conventions

## Components

- `export default function ScreenName() { ... }` — no `React.FC`
- `StyleSheet.create({})` at bottom of file
- Style values from `src/constants/theme.ts` (colors, spacing, borderRadius, fontSize)
- Conditional rendering: `{condition && <View>...</View>}`
- `KeyboardAvoidingView` wrapping `ScrollView` for input screens

## State (`src/store/`)

- Zustand: `create<AppState>()` with actions as store methods
- Action naming: `fetchX`, `addX`, `updateX`, `deleteX`
- Types in `src/types/index.ts`
- `interface` for entities, `type` for unions

## API

- Anthropic: direct SDK with `dangerouslyAllowBrowser: true`
- API key from `EXPO_PUBLIC_ANTHROPIC_API_KEY`
- Tag suggestion: pure keyword-map function, no AI call
- Supabase: single `createClient()` with `EXPO_PUBLIC_` env vars

## File Organization

- Kebab-case filenames throughout
- Constants grouped by domain in `src/constants/`
- Types centralized in `src/types/`
- API clients in `src/lib/`

## Relationship to InsightFlow

- This is the refactored version — make all changes here
- InsightFlow is the pre-refactor copy with Android build artifacts only
