/**
 * TC-EV052-009 — OpenAPI typed FE client (EV-052 / M4 / AC9).
 *
 * Locks: committed `openapi.d.ts`, `openapi:check` drift failure, and
 * convert/validate paths importing generated schema types.
 */
import { execFileSync } from 'node:child_process';
import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { describe, expect, it } from 'vitest';

/** Vitest runs with cwd = apps/frontend. */
const FRONTEND_ROOT = process.cwd();
const GENERATED = join(FRONTEND_ROOT, 'src/generated/openapi.d.ts');
const API_TS = join(FRONTEND_ROOT, 'src/utils/api.ts');
const OPENAPI_TYPES = join(FRONTEND_ROOT, 'src/utils/openapiTypes.ts');
const SNAPSHOT = join(FRONTEND_ROOT, 'openapi/openapi.json');

describe('TC-EV052-009 OpenAPI typed FE client', () => {
  it('keeps committed OpenAPI snapshot and generated types', () => {
    expect(
      existsSync(SNAPSHOT),
      'openapi/openapi.json missing — make openapi-refresh',
    ).toBe(true);
    expect(
      existsSync(GENERATED),
      'src/generated/openapi.d.ts missing — openapi:generate',
    ).toBe(true);
    const dts = readFileSync(GENERATED, 'utf8');
    expect(dts).toContain('ConversionResponse');
    expect(dts).toContain('ValidateResponse');
    expect(dts).toContain('LintTacResponse');
  });

  it('wires convert/validate types through openapiTypes → generated schemas', () => {
    const bridge = readFileSync(OPENAPI_TYPES, 'utf8');
    expect(bridge).toMatch(/from ['"]\.\.\/generated\/openapi['"]/);
    expect(bridge).toContain('ConversionResponse');
    expect(bridge).toContain('ValidateResponse');

    const api = readFileSync(API_TS, 'utf8');
    expect(api).toMatch(/from ['"]\.\/openapiTypes['"]/);
    expect(api).toContain('validateIwxxm');
    expect(api).toContain('ConversionResponse');
    expect(api).toContain('ValidateResponse');
  });

  it('openapi:check fails when generated types drift', () => {
    expect(existsSync(GENERATED)).toBe(true);
    const original = readFileSync(GENERATED, 'utf8');
    writeFileSync(GENERATED, `${original}\n// intentional-drift\n`, 'utf8');
    let exitCode = 0;
    try {
      execFileSync('pnpm', ['run', 'openapi:check'], {
        cwd: FRONTEND_ROOT,
        encoding: 'utf8',
        stdio: ['ignore', 'pipe', 'pipe'],
      });
    } catch (err) {
      const e = err as { status?: number };
      exitCode = typeof e.status === 'number' ? e.status : 1;
    } finally {
      writeFileSync(GENERATED, original, 'utf8');
    }
    expect(exitCode).not.toBe(0);
  });
});
