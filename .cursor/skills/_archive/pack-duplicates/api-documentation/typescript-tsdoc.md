# TypeScript — TSDoc Reference

Follow [TSDoc](https://tsdoc.org/) conventions. Validate syntax with `eslint-plugin-tsdoc` when enabled.

## Module

```typescript
/**
 * Backend API client for METAR → IWXXM conversion and validation.
 *
 * All endpoints use the versioned base path `/api/v1/`.
 *
 * @packageDocumentation
 */
```

Omit `@packageDocumentation` in app entry files unless publishing a package API surface.

## Function

```typescript
/**
 * Convert METAR/SPECI TAC text to IWXXM XML.
 *
 * Supports manual text input and file uploads.
 *
 * @param params - Conversion parameters
 * @param params.manualText - Optional METAR/SPECI text to convert
 * @param params.files - Optional files to convert
 * @param params.iwxxmVersion - Target IWXXM release line (e.g. `"2025-2"`)
 * @returns Conversion results with XML content and per-input errors
 * @throws {Error} When the backend is unreachable or returns a non-OK status
 *
 * @example
 * ```ts
 * const result = await convertMetarToIwxxm({ manualText: "METAR KJFK ..." });
 * console.log(result.results[0]?.content);
 * ```
 */
export async function convertMetarToIwxxm(params: {
  manualText?: string;
  files?: File[];
  iwxxmVersion?: string;
}): Promise<ConversionResponse> { ... }
```

## Interface / type

```typescript
/**
 * Result of a single METAR → IWXXM conversion.
 */
export interface ConversionResult {
  /** Display name of the source (filename or ``manual``). */
  name: string;

  /** Serialized IWXXM XML document. */
  content: string;

  /** Original TAC input that was converted. */
  source: string;

  /** Size of {@link ConversionResult.content} in bytes. */
  size_bytes: number;
}
```

## Class

```typescript
/**
 * HTTP client wrapper with auth headers and request timeouts.
 *
 * @remarks
 * Reads the Supabase access token from `localStorage` when present.
 */
export class ApiClient {
  /**
   * Perform an authenticated GET request.
   *
   * @param path - Path relative to the API base URL
   * @returns Parsed JSON response body
   */
  async get<T>(path: string): Promise<T> { ... }
}
```

## React component

Document props on the interface; keep the component doc brief:

```typescript
/** Props for {@link AirportDetailsCard}. */
export interface AirportDetailsCardProps {
  /** ICAO airport code (four letters). */
  airportCode: string;
  /** When true, show loading skeleton instead of data. */
  isLoading?: boolean;
}

/**
 * Display airport metadata and linked IWXXM region for a selected ICAO code.
 */
export function AirportDetailsCard(props: AirportDetailsCardProps) { ... }
```

## Tag reference

| Tag | Purpose |
|-----|---------|
| `@param` | Parameter description; use dot notation for object properties |
| `@returns` | Return value (not `@return`) |
| `@throws` | Errors / rejected promises |
| `@example` | Usage sample; fence with language tag |
| `@remarks` | Extra constraints, side effects, browser storage |
| `@see` | Related symbols or external URLs |
| `@deprecated` | Scheduled removal; include migration hint |
| `@internal` | Not part of public API (package exports) |
| `@defaultValue` | Default when not obvious from signature |

## Formatting rules

1. First line is a **complete sentence** summarizing purpose.
2. Blank line between summary and body/tags.
3. Use `{@link SymbolName}` for cross-references within the project.
4. Match parameter names exactly (including destructured `params.foo` style).
5. Do not restate types already clear from TypeScript signatures unless clarifying unions.
6. Prefer `@throws {Error}` with message context over generic "may throw".

## Internal helpers

Non-exported functions: one-line `/** ... */` or omit if name is self-explanatory:

```typescript
/** Read Supabase JWT from browser local storage. */
function getAccessToken(): string | null { ... }
```

## Tests

Test files: file-level comment describing what behavior is covered; skip full `@param` blocks on test helpers.
