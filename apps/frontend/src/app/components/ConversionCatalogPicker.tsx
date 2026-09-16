/**
 * Grouped searchable Conversion rule catalog from mined schema_blocks.
 */

import { Loader2 } from 'lucide-react';
import { useCallback, useEffect, useMemo, useState } from 'react';

import { listLibraryAssets } from '../../utils/conversionProfilesApi';
import {
  PROFILES_CONV_TEMPLATES_CATALOG_EMPTY,
  PROFILES_CONV_TEMPLATES_CATALOG_HEADING,
  PROFILES_CONV_TEMPLATES_CATALOG_HELP,
  PROFILES_CONV_TEMPLATES_CATALOG_LOADING,
  PROFILES_CONV_TEMPLATES_SEARCH,
  PROFILES_CONV_TEMPLATES_SEARCH_PLACEHOLDER,
} from '../../utils/conversionProfilesCopy';

export type ConversionCatalogCard = {
  id: string;
  label: string;
  groupId: string;
  groupLabel: string;
};

export type ConversionCatalogPickerProps = {
  accessToken: string;
  selectedCardId?: string | null;
  onSelectCard: (card: ConversionCatalogCard) => void;
};

type SchemaBlock = {
  id: string;
  label: string;
  cards: Array<{ id: string; label: string }>;
};

function parseSchemaBlocks(body: Record<string, unknown> | undefined): SchemaBlock[] {
  const raw = body?.schema_blocks;
  if (!Array.isArray(raw)) {
    return [];
  }
  const blocks: SchemaBlock[] = [];
  for (const entry of raw) {
    if (!entry || typeof entry !== 'object') {
      continue;
    }
    const rec = entry as Record<string, unknown>;
    const id = typeof rec.id === 'string' ? rec.id : '';
    const label = typeof rec.label === 'string' ? rec.label : id;
    if (!id) {
      continue;
    }
    const cardsRaw = Array.isArray(rec.cards) ? rec.cards : [];
    const cards: Array<{ id: string; label: string }> = [];
    for (const card of cardsRaw) {
      if (!card || typeof card !== 'object') {
        continue;
      }
      const cardRec = card as Record<string, unknown>;
      const cardId = typeof cardRec.id === 'string' ? cardRec.id : '';
      const cardLabel =
        typeof cardRec.label === 'string' && cardRec.label ? cardRec.label : cardId;
      if (!cardId) {
        continue;
      }
      cards.push({ id: cardId, label: cardLabel });
    }
    if (cards.length > 0) {
      blocks.push({ id, label, cards });
    }
  }
  return blocks;
}

/**
 * Searchable grouped catalog of mined Conversion IWXXM schema cards.
 *
 * @param props.accessToken - Bearer JWT
 * @param props.selectedCardId - Highlighted card id
 * @param props.onSelectCard - Called when operator picks a catalog card
 */
export function ConversionCatalogPicker({
  accessToken,
  selectedCardId = null,
  onSelectCard,
}: ConversionCatalogPickerProps) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [blocks, setBlocks] = useState<SchemaBlock[]>([]);
  const [query, setQuery] = useState('');

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await listLibraryAssets(accessToken, 'conversion');
      const merged = new Map<string, SchemaBlock>();
      for (const asset of res.items) {
        for (const block of parseSchemaBlocks(asset.body)) {
          const existing = merged.get(block.id);
          if (!existing) {
            merged.set(block.id, {
              id: block.id,
              label: block.label,
              cards: [...block.cards],
            });
            continue;
          }
          const seen = new Set(existing.cards.map((c) => c.id));
          for (const card of block.cards) {
            if (!seen.has(card.id)) {
              existing.cards.push(card);
              seen.add(card.id);
            }
          }
        }
      }
      setBlocks(Array.from(merged.values()));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Catalog unavailable');
      setBlocks([]);
    } finally {
      setLoading(false);
    }
  }, [accessToken]);

  /* eslint-disable react-hooks/set-state-in-effect -- refetch when token changes */
  useEffect(() => {
    void load();
  }, [load]);
  /* eslint-enable react-hooks/set-state-in-effect */

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) {
      return blocks;
    }
    return blocks
      .map((block) => {
        const groupHit =
          block.label.toLowerCase().includes(q) || block.id.toLowerCase().includes(q);
        const cards = groupHit
          ? block.cards
          : block.cards.filter(
              (card) =>
                card.label.toLowerCase().includes(q) ||
                card.id.toLowerCase().includes(q),
            );
        return { ...block, cards };
      })
      .filter((block) => block.cards.length > 0);
  }, [blocks, query]);

  const totalCards = filtered.reduce((n, b) => n + b.cards.length, 0);

  return (
    <div className="space-y-2" data-testid="conversion-catalog-picker">
      <div>
        <h4 className="text-sm font-medium">
          {PROFILES_CONV_TEMPLATES_CATALOG_HEADING}
        </h4>
        <p className="text-xs text-gray-600 dark:text-gray-400">
          {PROFILES_CONV_TEMPLATES_CATALOG_HELP}
        </p>
      </div>
      <label className="block text-xs">
        <span className="sr-only">{PROFILES_CONV_TEMPLATES_SEARCH}</span>
        <input
          type="search"
          className="w-full rounded border border-gray-300 bg-white p-2 text-sm dark:border-gray-600 dark:bg-gray-900"
          data-testid="conversion-catalog-search"
          placeholder={PROFILES_CONV_TEMPLATES_SEARCH_PLACEHOLDER}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          aria-label={PROFILES_CONV_TEMPLATES_SEARCH}
        />
      </label>
      {loading ? (
        <p
          className="flex items-center gap-2 text-sm text-gray-600"
          data-testid="conversion-catalog-loading"
        >
          <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
          {PROFILES_CONV_TEMPLATES_CATALOG_LOADING}
        </p>
      ) : null}
      {error ? (
        <p className="text-sm text-red-600" data-testid="conversion-catalog-error">
          {error}
        </p>
      ) : null}
      {!loading && !error && totalCards === 0 ? (
        <p className="text-sm text-gray-600" data-testid="conversion-catalog-empty">
          {PROFILES_CONV_TEMPLATES_CATALOG_EMPTY}
        </p>
      ) : null}
      <div
        className="max-h-64 space-y-3 overflow-y-auto rounded border border-gray-200 p-2 dark:border-gray-700"
        data-testid="conversion-catalog-groups"
      >
        {filtered.map((block) => (
          <div key={block.id} data-testid={`conversion-catalog-group-${block.id}`}>
            <p className="text-xs font-medium uppercase tracking-wide text-gray-500">
              {block.label}
              <span className="ml-1 font-normal normal-case text-gray-400">
                ({block.cards.length})
              </span>
            </p>
            <ul className="mt-1 space-y-1">
              {block.cards.map((card) => {
                const selected = selectedCardId === card.id;
                return (
                  <li key={card.id}>
                    <button
                      type="button"
                      className={`w-full rounded px-2 py-1.5 text-left text-sm ${
                        selected
                          ? 'bg-sky-100 text-sky-900 dark:bg-sky-900/40 dark:text-sky-100'
                          : 'hover:bg-gray-100 dark:hover:bg-gray-800'
                      }`}
                      data-testid={`conversion-catalog-card-${card.id}`}
                      aria-pressed={selected}
                      onClick={() =>
                        onSelectCard({
                          id: card.id,
                          label: card.label,
                          groupId: block.id,
                          groupLabel: block.label,
                        })
                      }
                    >
                      <span className="font-medium">{card.label || card.id}</span>
                      <span className="mt-0.5 block truncate text-xs text-gray-500">
                        {card.id}
                      </span>
                    </button>
                  </li>
                );
              })}
            </ul>
          </div>
        ))}
      </div>
      {!loading && totalCards > 0 ? (
        <p className="text-xs text-gray-500" data-testid="conversion-catalog-count">
          {totalCards} rules in {filtered.length} groups
        </p>
      ) : null}
    </div>
  );
}
