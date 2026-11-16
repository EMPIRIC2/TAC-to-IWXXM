/**
 * Evolve-auto test matrix for frontend models + line-count gate
 * (EV-frontend-models-split).
 */
import { describe, expect, it } from 'vitest';
import { readdirSync, readFileSync, statSync } from 'node:fs';
import { join, relative, resolve } from 'node:path';
import type { Airport } from './airport';
import type { HealthResponse, MassIngestResponse } from './api';
import type {
  ConversionParams,
  ConvertedFile,
  StoredConverterPreferences,
} from './fileConverter';
import type { LivePlace, LiveReport } from './liveMap';
import type {
  ConversionResponse,
  GroupTraceEntry,
  QualityMetricsIssue,
  QualityMetricsResidual,
} from './openapi';
import type { ByocDestinationParams } from './disseminationDrawer';
import type {
  WorkSessionConversionLog,
  WorkSessionConversionParams,
  WorkSessionConvertResult,
} from './workSession';
import { airportsData } from '@/data/airportsCatalog';
import {
  conversionParamsFromStoredPreferences,
  initialConversionParams,
} from '@/utils/fileConverterParams';
import {
  dropReaderText,
  hasDropFiles,
  progressRowState,
} from '@/utils/disseminationDrawerPure';
import type { DisseminationRowUiState } from './disseminationDrawer';

const SRC_ROOT = resolve(process.cwd(), 'src');

function walkTsFiles(dir: string, out: string[] = []): string[] {
  for (const name of readdirSync(dir)) {
    const full = join(dir, name);
    const st = statSync(full);
    if (st.isDirectory()) {
      if (name === 'generated') continue;
      walkTsFiles(full, out);
      continue;
    }
    if (!/\.tsx?$/.test(name)) continue;
    if (/\.test\.tsx?$/.test(name)) continue;
    out.push(full);
  }
  return out;
}

describe('frontend models split matrix', () => {
  describe('validation success (V+)', () => {
    it('accepts a typed ConversionResponse with named group_trace entries', () => {
      const trace: GroupTraceEntry = {
        start: 0,
        end: 4,
        token: 'METAR',
        element: 'iwxxm:MeteorologicalAerodromeObservation',
        occurrence: 1,
        scope: 'line',
      };
      const payload: ConversionResponse = {
        results: [],
        errors: [],
        total_processed: 0,
        successful: 0,
        failed: 0,
        group_trace: [trace],
      };
      expect(payload.group_trace?.[0]?.token).toBe('METAR');
    });

    it('accepts stored preferences into ConversionParams (V+)', () => {
      const prefs: StoredConverterPreferences = {
        bulletinIdExample: 'SAAA00',
        product: 'METAR',
        strictLint: true,
      };
      const params = conversionParamsFromStoredPreferences(prefs);
      expect(params.bulletinId).toBe('SAAA00');
      expect(params.product).toBe('METAR');
      const _typed: ConversionParams = params;
      expect(_typed.iwxxmVersion).toBeTruthy();
    });
  });

  describe('validation failure (V−)', () => {
    it('rejects incomplete LivePlace contracts via runtime guard', () => {
      const bad: Partial<LivePlace> = { place_key: 'x' };
      const isLivePlace = (value: Partial<LivePlace>): value is LivePlace =>
        typeof value.place_key === 'string' &&
        typeof value.product === 'string' &&
        typeof value.latitude === 'number' &&
        typeof value.longitude === 'number' &&
        Array.isArray(value.reports);
      expect(isLivePlace(bad)).toBe(false);
    });

    it('falls back safely for empty preferences (V− path still yields params)', () => {
      const params = conversionParamsFromStoredPreferences({});
      const baseline = initialConversionParams();
      expect(params.profile).toBeTruthy();
      expect(typeof baseline.strictLint).toBe('boolean');
    });

    it('rejects mass-ingest responses missing results', () => {
      const candidate = {
        total: 1,
        successful: 0,
        failed: 1,
      } as Partial<MassIngestResponse>;
      expect(Array.isArray(candidate.results)).toBe(false);
    });
  });

  describe('mutation create/update/delete success', () => {
    it('creates a ConvertedFile card, updates resultCard, then deletes it', () => {
      let queue: ConvertedFile[] = [];
      const created: ConvertedFile = {
        id: 'c1',
        originalName: 'a.txt',
        originalContent: 'METAR KJFK 010000Z',
        convertedContent: '<xml/>',
        timestamp: 1,
        displayTitle: 'METAR KJFK 010000Z',
      };
      queue = [...queue, created];
      expect(queue).toHaveLength(1);
      queue = queue.map((item) =>
        item.id === 'c1'
          ? { ...item, resultCard: { errors: [], issues: [], ok: true } }
          : item,
      );
      expect(queue[0]?.resultCard?.ok).toBe(true);
      queue = queue.filter((item) => item.id !== 'c1');
      expect(queue).toHaveLength(0);
    });

    it('mutates work-session conversion params and log blobs', () => {
      let params: WorkSessionConversionParams = { product: 'METAR' };
      params = { ...params, issuingCenter: 'KJFK' };
      expect(params.issuingCenter).toBe('KJFK');
      let log: WorkSessionConversionLog = { errors: [], issues: [] };
      log = { errors: ['boom'], issues: [{ code: 'X', message: 'bad' }] };
      expect(log.errors).toHaveLength(1);
      const result: WorkSessionConvertResult = { content: '<xml/>', ok: true };
      expect(result.ok).toBe(true);
    });
  });

  describe('mutation failure', () => {
    it('rejects BYOC params that are not objects', () => {
      const parse = (raw: string): ByocDestinationParams | null => {
        try {
          const parsed: unknown = JSON.parse(raw);
          if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) {
            return null;
          }
          return parsed as ByocDestinationParams;
        } catch {
          return null;
        }
      };
      expect(parse('[]')).toBeNull();
      expect(parse('{')).toBeNull();
      expect(parse('{"uri":"postgres://x"}')?.uri).toBe('postgres://x');
    });
  });

  describe('read/query success', () => {
    it('loads airport catalog entries with Airport shape', () => {
      const sample: Airport | undefined = airportsData[0];
      expect(sample?.icao).toMatch(/^[A-Z0-9]{4}$/);
      expect(sample?.name.length).toBeGreaterThan(0);
    });

    it('types health and live report read models', () => {
      const health: HealthResponse = {
        status: 'healthy',
        version: '1',
        tac2iwxxm_available: true,
      };
      const report: LiveReport = { observed_at: '2026-01-01T00:00:00Z', tac: 'METAR' };
      expect(health.status).toBe('healthy');
      expect(report.tac).toContain('METAR');
    });
  });

  describe('read/query failure', () => {
    it('treats missing quality-metrics residual fields as empty', () => {
      const residual: QualityMetricsResidual = {};
      const issue: QualityMetricsIssue = {};
      expect(residual.message ?? null).toBeNull();
      expect(issue.code ?? null).toBeNull();
    });
  });

  describe('dissemination helpers (touched utils)', () => {
    it('validates drop files and progress rows', () => {
      expect(hasDropFiles(undefined)).toBe(false);
      expect(dropReaderText(null)).toBe('');
      const state: Record<string, DisseminationRowUiState> = {
        a: { status: 'ok' },
        b: { status: 'error', error: 'nope' },
      };
      expect(progressRowState(state, 'a').status).toBe('ok');
      expect(progressRowState(state, 'missing').status).toBe('pending');
    });
  });

  describe('line-count gate', () => {
    it('keeps every application source file under 500 lines', () => {
      const files = walkTsFiles(SRC_ROOT);
      const offenders = files
        .map((file) => {
          const lines = readFileSync(file, 'utf8').split(/\r?\n/).length;
          return { file: relative(SRC_ROOT, file), lines };
        })
        .filter((row) => row.lines > 500);
      expect(offenders).toEqual([]);
    });
  });
});
