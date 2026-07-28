/**
 * TC-F22-001..003 — Privacy preference center contract (F22 / UJ-033 / ADR-031).
 *
 * Red until T6.2 (notice + settings + localStorage) and T6.3 (GPC honor).
 */

import { beforeEach, describe, expect, it } from 'vitest';
import {
  PRIVACY_PREFS_STORAGE_KEY,
  PRIVACY_SCHEMA_VERSION,
  STORAGE_INVENTORY,
  acknowledgePrivacyNotice,
  applyGpcToPreferences,
  clearPrivacyPreferences,
  defaultPrivacyPreferences,
  detectGlobalPrivacyControl,
  loadPrivacyPreferences,
  savePrivacyPreferences,
  shouldShowPrivacyNotice,
} from './privacyPreferences';

describe('privacyPreferences (TC-F22)', () => {
  beforeEach(() => {
    localStorage.clear();
    try {
      clearPrivacyPreferences();
    } catch {
      // Stub throws until T6.2 — ignore so individual assertions surface.
    }
  });

  describe('TC-F22-001: First-visit privacy notice', () => {
    it('shows notice when preferences have never been acknowledged', () => {
      expect(shouldShowPrivacyNotice()).toBe(true);
    });

    it('hides notice after acknowledge and persists across load', () => {
      const afterAck = acknowledgePrivacyNotice();
      expect(afterAck.noticeAcknowledgedAt).toBeTruthy();
      expect(afterAck.noticeSchemaVersion).toBe(PRIVACY_SCHEMA_VERSION);
      expect(shouldShowPrivacyNotice()).toBe(false);

      const reloaded = loadPrivacyPreferences();
      expect(reloaded.noticeAcknowledgedAt).toBe(afterAck.noticeAcknowledgedAt);
      expect(shouldShowPrivacyNotice()).toBe(false);
    });

    it('re-shows notice after preference schema version bump', () => {
      acknowledgePrivacyNotice();
      expect(shouldShowPrivacyNotice()).toBe(false);

      savePrivacyPreferences({
        schemaVersion: PRIVACY_SCHEMA_VERSION + 1,
      });
      expect(shouldShowPrivacyNotice()).toBe(true);
    });

    it('discloses IndexedDB work history in the storage inventory (no CMP)', () => {
      const idb = STORAGE_INVENTORY.find((item) => item.kind === 'indexedDB');
      expect(idb).toBeDefined();
      expect(idb?.purpose).toMatch(/work history|session/i);
      expect(idb?.necessary).toBe(true);

      // Solution A: inventory covers only tech in use — no analytics CDN/cookie rows.
      expect(STORAGE_INVENTORY.every((item) => item.kind !== 'cdn')).toBe(true);
    });
  });

  describe('TC-F22-002: Privacy settings preference center', () => {
    it('defaults to Solution A: necessary on, non-essential off', () => {
      const prefs = defaultPrivacyPreferences();
      expect(prefs.schemaVersion).toBe(PRIVACY_SCHEMA_VERSION);
      expect(prefs.necessary).toBe(true);
      expect(prefs.analytics).toBe(false);
      expect(prefs.marketing).toBe(false);
      expect(prefs.saleOrSharingOptOut).toBe(false);
      expect(prefs.targetedAdvertisingOptOut).toBe(false);
    });

    it('round-trips preferences through localStorage only', () => {
      const saved = savePrivacyPreferences({
        analytics: false,
        marketing: false,
        saleOrSharingOptOut: true,
      });
      expect(saved.necessary).toBe(true);
      expect(saved.saleOrSharingOptOut).toBe(true);

      const raw = localStorage.getItem(PRIVACY_PREFS_STORAGE_KEY);
      expect(raw).toBeTruthy();
      expect(raw).not.toMatch(/supabase|jwt|password/i);

      const loaded = loadPrivacyPreferences();
      expect(loaded.saleOrSharingOptOut).toBe(true);
      expect(loaded.necessary).toBe(true);
    });

    it('keeps necessary true even if a caller tries to unset it', () => {
      const saved = savePrivacyPreferences({
        analytics: true,
        ...({ necessary: false } as Record<string, unknown>),
      } as Parameters<typeof savePrivacyPreferences>[0]);
      expect(saved.necessary).toBe(true);
    });

    it('resets preferences when site data (localStorage) is cleared', () => {
      savePrivacyPreferences({ saleOrSharingOptOut: true });
      localStorage.clear();

      const loaded = loadPrivacyPreferences();
      expect(loaded.saleOrSharingOptOut).toBe(false);
      expect(loaded.noticeAcknowledgedAt).toBeNull();
      expect(shouldShowPrivacyNotice()).toBe(true);
    });
  });

  describe('TC-F22-003: Global Privacy Control (GPC) honor', () => {
    it('detects navigator.globalPrivacyControl === true', () => {
      expect(detectGlobalPrivacyControl({ navigatorGpc: true })).toBe(true);
      expect(detectGlobalPrivacyControl({ navigatorGpc: false })).toBe(false);
    });

    it('detects Sec-GPC: 1 header signal', () => {
      expect(detectGlobalPrivacyControl({ secGpc: '1' })).toBe(true);
      expect(detectGlobalPrivacyControl({ secGpc: '0' })).toBe(false);
      expect(detectGlobalPrivacyControl({ secGpc: null })).toBe(false);
    });

    it('forces sale/sharing and targeted-advertising opt-outs when GPC is on', () => {
      const base = defaultPrivacyPreferences();
      const withGpc = applyGpcToPreferences(base, true);
      expect(withGpc.saleOrSharingOptOut).toBe(true);
      expect(withGpc.targetedAdvertisingOptOut).toBe(true);
      // Disclosed IndexedDB work history remains necessary — not wiped by GPC.
      expect(withGpc.necessary).toBe(true);
      expect(withGpc.analytics).toBe(false);
      expect(withGpc.marketing).toBe(false);
    });

    it('does not force opt-outs when GPC is off', () => {
      const base = defaultPrivacyPreferences();
      const without = applyGpcToPreferences(base, false);
      expect(without.saleOrSharingOptOut).toBe(false);
      expect(without.targetedAdvertisingOptOut).toBe(false);
    });

    it('loadPrivacyPreferences applies GPC overrides when signal is present', () => {
      // Simulate GPC via save path after detect — implementation wires navigator in T6.3.
      const gpcOn = detectGlobalPrivacyControl({ navigatorGpc: true });
      expect(gpcOn).toBe(true);

      savePrivacyPreferences({
        saleOrSharingOptOut: false,
        targetedAdvertisingOptOut: false,
      });

      // With GPC stubbed into detect, load must still force opt-outs (T6.3).
      // Tests stub navigator on globalThis when implementation reads it.
      Object.defineProperty(globalThis.navigator, 'globalPrivacyControl', {
        configurable: true,
        get: () => true,
      });

      const loaded = loadPrivacyPreferences();
      expect(loaded.saleOrSharingOptOut).toBe(true);
      expect(loaded.targetedAdvertisingOptOut).toBe(true);
    });

    it('detectGlobalPrivacyControl reads navigator when called without options', () => {
      Object.defineProperty(globalThis.navigator, 'globalPrivacyControl', {
        configurable: true,
        get: () => true,
      });
      expect(detectGlobalPrivacyControl()).toBe(true);

      Object.defineProperty(globalThis.navigator, 'globalPrivacyControl', {
        configurable: true,
        get: () => false,
      });
      expect(detectGlobalPrivacyControl()).toBe(false);

      Object.defineProperty(globalThis.navigator, 'globalPrivacyControl', {
        configurable: true,
        get: () => '1' as unknown as boolean,
      });
      expect(detectGlobalPrivacyControl()).toBe(false);
    });

    it('recovers from corrupt localStorage JSON', () => {
      localStorage.setItem(PRIVACY_PREFS_STORAGE_KEY, '{not-json');
      const loaded = loadPrivacyPreferences();
      expect(loaded.schemaVersion).toBe(PRIVACY_SCHEMA_VERSION);
      expect(loaded.necessary).toBe(true);
    });

    it('tolerates missing localStorage APIs', () => {
      const original = globalThis.localStorage;
      Object.defineProperty(globalThis, 'localStorage', {
        configurable: true,
        value: undefined,
      });
      try {
        expect(loadPrivacyPreferences().necessary).toBe(true);
        expect(savePrivacyPreferences({ saleOrSharingOptOut: true }).necessary).toBe(
          true,
        );
        expect(() => clearPrivacyPreferences()).not.toThrow();
      } finally {
        Object.defineProperty(globalThis, 'localStorage', {
          configurable: true,
          value: original,
        });
      }
    });
  });
});
