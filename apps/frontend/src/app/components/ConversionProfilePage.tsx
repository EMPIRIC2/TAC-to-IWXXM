/**
 * ConversionProfile editor — catalog inspector, rule packs, signed overlays (UJ-072 / F7.w).
 * Requires sign-in.
 */

import { useCallback, useEffect, useMemo, useState } from 'react';
import { Loader2 } from 'lucide-react';
import {
  createOverlay,
  createRulePack,
  fetchProfileCatalog,
  listOverlays,
  listRulePacks,
  type OverlayOut,
  type ProfileCatalogEntry,
  type RulePackOut,
} from '@/utils/conversionProfilesApi';
import {
  PROFILES_EDITOR_LOGIN_REQUIRED,
  PROFILES_EDITOR_SIGN_IN,
  PROFILES_EDITOR_SUBTITLE,
  PROFILES_EDITOR_TITLE,
  PROFILES_ERROR_PREFIX,
  PROFILES_INSPECTOR_EMPTY,
  PROFILES_INSPECTOR_HEADING,
  PROFILES_INSPECTOR_LOADING,
  PROFILES_INSPECTOR_SELECT,
  PROFILES_OVERLAY_BASE,
  PROFILES_OVERLAY_BODY,
  PROFILES_OVERLAY_HINT,
  PROFILES_OVERLAY_SAVE,
  PROFILES_OVERLAY_SLUG,
  PROFILES_OVERLAYS_EMPTY,
  PROFILES_OVERLAYS_HEADING,
  PROFILES_OVERLAYS_LOADING,
  PROFILES_PACK_EXPORT,
  PROFILES_PACK_MESSAGE,
  PROFILES_PACK_PRODUCT,
  PROFILES_PACK_PROFILE,
  PROFILES_PACK_REF,
  PROFILES_PACK_SAVE,
  PROFILES_PACK_SEVERITY,
  PROFILES_PACK_SLUG,
  PROFILES_PACK_STAGE,
  PROFILES_PACK_WHEN,
  PROFILES_PACKS_EMPTY,
  PROFILES_PACKS_HEADING,
  PROFILES_PACKS_LOADING,
} from '@/utils/conversionProfilesCopy';
import { Button } from './ui/button';
import { Card } from './ui/card';

export interface ConversionProfilePageProps {
  /** Bearer JWT — when absent, show sign-in prompt. */
  accessToken?: string;
  /** Navigate to login. */
  onRequestLogin?: () => void;
}

function errorMessage(err: unknown): string {
  return err instanceof Error ? err.message : 'Unknown error';
}

interface AuthedProps {
  accessToken: string;
}

function ConversionProfileAuthed({ accessToken }: AuthedProps) {
  const [catalog, setCatalog] = useState<ProfileCatalogEntry[] | null>(null);
  const [packs, setPacks] = useState<RulePackOut[] | null>(null);
  const [overlays, setOverlays] = useState<OverlayOut[] | null>(null);
  const [selectedId, setSelectedId] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [savingOverlay, setSavingOverlay] = useState(false);

  const [slug, setSlug] = useState('my-pack');
  const [profile, setProfile] = useState('ICAO_2025');
  const [product, setProduct] = useState('METAR');
  const [stage, setStage] = useState('lint');
  const [severity, setSeverity] = useState('warning');
  const [whenExpr, setWhenExpr] = useState('');
  const [message, setMessage] = useState('');
  const [standardRef, setStandardRef] = useState('');

  const [overlaySlug, setOverlaySlug] = useState('my-overlay');
  const [overlayBase, setOverlayBase] = useState('ICAO_2025');
  const [overlayBodyText, setOverlayBodyText] = useState('{}');

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [cat, packList, overlayList] = await Promise.all([
        fetchProfileCatalog(accessToken),
        listRulePacks(accessToken),
        listOverlays(accessToken),
      ]);
      setCatalog(cat.profiles);
      setPacks(packList.items);
      setOverlays(overlayList.items);
      const first = cat.profiles[0];
      if (!selectedId && first) {
        setSelectedId(first.id);
      }
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [accessToken, selectedId]);

  /* eslint-disable react-hooks/set-state-in-effect -- refetch when token changes */
  useEffect(() => {
    void load();
  }, [load]);
  /* eslint-enable react-hooks/set-state-in-effect */

  const selected = useMemo(
    () => catalog?.find((p) => p.id === selectedId) ?? null,
    [catalog, selectedId],
  );

  const onSave = async () => {
    setSaving(true);
    setError(null);
    try {
      await createRulePack(accessToken, {
        slug,
        profile,
        product,
        stage,
        severity,
        when: whenExpr,
        message,
        standardReference: standardRef,
      });
      await load();
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setSaving(false);
    }
  };

  const onSaveOverlay = async () => {
    setSavingOverlay(true);
    setError(null);
    try {
      let parsed: unknown;
      try {
        parsed = JSON.parse(overlayBodyText.trim() || '{}');
      } catch {
        throw new Error('Overlay JSON must be valid');
      }
      if (parsed === null || typeof parsed !== 'object' || Array.isArray(parsed)) {
        throw new Error('Overlay JSON must be an object');
      }
      await createOverlay(accessToken, {
        slug: overlaySlug,
        baseProfileId: overlayBase,
        body: parsed as Record<string, unknown>,
      });
      await load();
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setSavingOverlay(false);
    }
  };

  const onExport = () => {
    // Invoked only when the export control is enabled (packs loaded and non-empty).
    const blob = new Blob([JSON.stringify(packs, null, 2)], {
      type: 'application/json',
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'rule-packs.json';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div
      className="mx-auto max-w-6xl space-y-4 p-4"
      data-testid="conversion-profiles-page"
    >
      <header>
        <h1 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
          {PROFILES_EDITOR_TITLE}
        </h1>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          {PROFILES_EDITOR_SUBTITLE}
        </p>
      </header>

      {error && (
        <p className="text-sm text-red-600" data-testid="conversion-profiles-error">
          {PROFILES_ERROR_PREFIX} {error}
        </p>
      )}

      <Card className="space-y-3 p-4" data-testid="conversion-profiles-inspector">
        <h2 className="text-sm font-medium">{PROFILES_INSPECTOR_HEADING}</h2>
        {loading && catalog === null ? (
          <p className="flex items-center gap-2 text-sm text-gray-500">
            <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
            {PROFILES_INSPECTOR_LOADING}
          </p>
        ) : !catalog || catalog.length === 0 ? (
          <p className="text-sm text-gray-500">{PROFILES_INSPECTOR_EMPTY}</p>
        ) : (
          <>
            <label className="block text-sm">
              <span className="text-gray-700 dark:text-gray-300">
                {PROFILES_INSPECTOR_SELECT}
              </span>
              <select
                className="mt-1 w-full rounded border border-gray-300 bg-white p-2 dark:border-gray-600 dark:bg-gray-900"
                data-testid="conversion-profiles-select"
                value={selectedId}
                onChange={(e) => setSelectedId(e.target.value)}
              >
                {catalog.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.id} ({p.kind})
                  </option>
                ))}
              </select>
            </label>
            {selected && (
              <dl
                className="grid grid-cols-1 gap-2 text-sm sm:grid-cols-2"
                data-testid="conversion-profiles-inspector-detail"
              >
                <div>
                  <dt className="text-gray-500">Kind</dt>
                  <dd>{selected.kind}</dd>
                </div>
                <div>
                  <dt className="text-gray-500">Status</dt>
                  <dd>{selected.status ?? '—'}</dd>
                </div>
                <div>
                  <dt className="text-gray-500">Products</dt>
                  <dd>{selected.products.join(', ') || '—'}</dd>
                </div>
                <div>
                  <dt className="text-gray-500">Emit key</dt>
                  <dd>{selected.emit_key ?? '—'}</dd>
                </div>
              </dl>
            )}
          </>
        )}
      </Card>

      <Card className="space-y-3 p-4" data-testid="conversion-profiles-packs">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <h2 className="text-sm font-medium">{PROFILES_PACKS_HEADING}</h2>
          <Button
            type="button"
            variant="outline"
            size="sm"
            data-testid="conversion-profiles-export"
            onClick={onExport}
            disabled={!packs || packs.length === 0}
          >
            {PROFILES_PACK_EXPORT}
          </Button>
        </div>

        <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
          <label className="text-sm">
            {PROFILES_PACK_SLUG}
            <input
              className="mt-1 w-full rounded border p-2 dark:border-gray-600 dark:bg-gray-900"
              data-testid="conversion-profiles-pack-slug"
              value={slug}
              onChange={(e) => setSlug(e.target.value)}
            />
          </label>
          <label className="text-sm">
            {PROFILES_PACK_PROFILE}
            <input
              className="mt-1 w-full rounded border p-2 dark:border-gray-600 dark:bg-gray-900"
              data-testid="conversion-profiles-pack-profile"
              value={profile}
              onChange={(e) => setProfile(e.target.value)}
            />
          </label>
          <label className="text-sm">
            {PROFILES_PACK_PRODUCT}
            <input
              className="mt-1 w-full rounded border p-2 dark:border-gray-600 dark:bg-gray-900"
              data-testid="conversion-profiles-pack-product"
              value={product}
              onChange={(e) => setProduct(e.target.value)}
            />
          </label>
          <label className="text-sm">
            {PROFILES_PACK_STAGE}
            <input
              className="mt-1 w-full rounded border p-2 dark:border-gray-600 dark:bg-gray-900"
              data-testid="conversion-profiles-pack-stage"
              value={stage}
              onChange={(e) => setStage(e.target.value)}
            />
          </label>
          <label className="text-sm">
            {PROFILES_PACK_SEVERITY}
            <input
              className="mt-1 w-full rounded border p-2 dark:border-gray-600 dark:bg-gray-900"
              data-testid="conversion-profiles-pack-severity"
              value={severity}
              onChange={(e) => setSeverity(e.target.value)}
            />
          </label>
          <label className="text-sm">
            {PROFILES_PACK_WHEN}
            <input
              className="mt-1 w-full rounded border p-2 dark:border-gray-600 dark:bg-gray-900"
              data-testid="conversion-profiles-pack-when"
              value={whenExpr}
              onChange={(e) => setWhenExpr(e.target.value)}
            />
          </label>
          <label className="text-sm sm:col-span-2">
            {PROFILES_PACK_MESSAGE}
            <input
              className="mt-1 w-full rounded border p-2 dark:border-gray-600 dark:bg-gray-900"
              data-testid="conversion-profiles-pack-message"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
            />
          </label>
          <label className="text-sm sm:col-span-2">
            {PROFILES_PACK_REF}
            <input
              className="mt-1 w-full rounded border p-2 dark:border-gray-600 dark:bg-gray-900"
              data-testid="conversion-profiles-pack-ref"
              value={standardRef}
              onChange={(e) => setStandardRef(e.target.value)}
            />
          </label>
        </div>

        <Button
          type="button"
          data-testid="conversion-profiles-pack-save"
          onClick={() => void onSave()}
          disabled={saving}
        >
          {saving ? <Loader2 className="h-4 w-4 animate-spin" aria-hidden /> : null}
          {PROFILES_PACK_SAVE}
        </Button>

        {loading && packs === null ? (
          <p className="text-sm text-gray-500">{PROFILES_PACKS_LOADING}</p>
        ) : !packs || packs.length === 0 ? (
          <p className="text-sm text-gray-500">{PROFILES_PACKS_EMPTY}</p>
        ) : (
          <ul className="space-y-1 text-sm" data-testid="conversion-profiles-pack-list">
            {packs.map((p) => (
              <li key={p.id}>
                <code>{p.slug}</code> — {p.profile} / {p.product} ({p.severity})
              </li>
            ))}
          </ul>
        )}
      </Card>

      <Card className="space-y-3 p-4" data-testid="conversion-profiles-overlays">
        <h2 className="text-sm font-medium">{PROFILES_OVERLAYS_HEADING}</h2>
        <p className="text-xs text-gray-600 dark:text-gray-400">
          {PROFILES_OVERLAY_HINT}
        </p>
        <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
          <label className="text-sm">
            {PROFILES_OVERLAY_SLUG}
            <input
              className="mt-1 w-full rounded border p-2 dark:border-gray-600 dark:bg-gray-900"
              data-testid="conversion-profiles-overlay-slug"
              value={overlaySlug}
              onChange={(e) => setOverlaySlug(e.target.value)}
            />
          </label>
          <label className="text-sm">
            {PROFILES_OVERLAY_BASE}
            <input
              className="mt-1 w-full rounded border p-2 dark:border-gray-600 dark:bg-gray-900"
              data-testid="conversion-profiles-overlay-base"
              value={overlayBase}
              onChange={(e) => setOverlayBase(e.target.value)}
            />
          </label>
          <label className="text-sm sm:col-span-2">
            {PROFILES_OVERLAY_BODY}
            <textarea
              className="mt-1 w-full rounded border p-2 font-mono text-xs dark:border-gray-600 dark:bg-gray-900"
              data-testid="conversion-profiles-overlay-body"
              rows={4}
              value={overlayBodyText}
              onChange={(e) => setOverlayBodyText(e.target.value)}
            />
          </label>
        </div>
        <Button
          type="button"
          data-testid="conversion-profiles-overlay-save"
          onClick={() => void onSaveOverlay()}
          disabled={savingOverlay}
        >
          {savingOverlay ? (
            <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
          ) : null}
          {PROFILES_OVERLAY_SAVE}
        </Button>
        {loading && overlays === null ? (
          <p className="text-sm text-gray-500">{PROFILES_OVERLAYS_LOADING}</p>
        ) : !overlays || overlays.length === 0 ? (
          <p className="text-sm text-gray-500">{PROFILES_OVERLAYS_EMPTY}</p>
        ) : (
          <ul
            className="space-y-1 text-sm"
            data-testid="conversion-profiles-overlay-list"
          >
            {overlays.map((o) => (
              <li key={o.id}>
                <code>{o.slug}</code> — {o.baseProfileId}{' '}
                <span className="text-gray-500">({o.id})</span>
              </li>
            ))}
          </ul>
        )}
      </Card>
    </div>
  );
}

/**
 * Conversion profiles shell page.
 *
 * @param props.accessToken - Optional JWT
 * @param props.onRequestLogin - Sign-in handler
 */
export function ConversionProfilePage({
  accessToken,
  onRequestLogin,
}: ConversionProfilePageProps) {
  if (!accessToken) {
    return (
      <div
        className="mx-auto max-w-lg space-y-4 p-8 text-center"
        data-testid="conversion-profiles-page"
      >
        <h1 className="text-xl font-semibold">{PROFILES_EDITOR_TITLE}</h1>
        <p className="text-sm text-gray-600">{PROFILES_EDITOR_LOGIN_REQUIRED}</p>
        <Button
          type="button"
          data-testid="conversion-profiles-sign-in"
          onClick={() => onRequestLogin?.()}
        >
          {PROFILES_EDITOR_SIGN_IN}
        </Button>
      </div>
    );
  }
  return <ConversionProfileAuthed accessToken={accessToken} />;
}
