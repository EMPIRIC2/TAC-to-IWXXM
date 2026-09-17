/**
 * Draft authoring shell for Profile builder library kinds (EVPYL Phase C).
 */

import { CircleHelp } from 'lucide-react';
import { useCallback, useEffect, useMemo, useState } from 'react';

import type { LibraryAssetKind } from '../../utils/conversionProfilesApi';
import {
  createLibraryAsset,
  updateLibraryAsset,
} from '../../utils/conversionProfilesApi';
import {
  PROFILES_DRAFT_ACTIVATE,
  PROFILES_DRAFT_ACTIVATE_BLOCKED,
  PROFILES_DRAFT_BLOCK_CLOUD,
  PROFILES_DRAFT_BLOCK_OBSERVATION,
  PROFILES_DRAFT_BLOCK_RVR,
  PROFILES_DRAFT_BLOCKS_HEADING,
  PROFILES_DRAFT_BLOCKS_HELP,
  PROFILES_DRAFT_CAPTURES_HEADING,
  PROFILES_DRAFT_CARD_CLOUD_AMOUNT,
  PROFILES_DRAFT_CARD_RVR,
  PROFILES_DRAFT_CARD_VISIBILITY,
  PROFILES_DRAFT_CARD_WIND,
  PROFILES_DRAFT_DIAGNOSTICS_HEADING,
  PROFILES_DRAFT_DIAGNOSTICS_HELP,
  PROFILES_DRAFT_DUPLICATE,
  PROFILES_DRAFT_HEADING,
  PROFILES_DRAFT_HELP,
  PROFILES_DRAFT_IMPORT_LABEL,
  PROFILES_DRAFT_IMPORT_PLACEHOLDER,
  PROFILES_DRAFT_NEW_TEMPLATE,
  PROFILES_DRAFT_SAMPLE_HEADING,
  PROFILES_DRAFT_SAMPLE_HELP,
  PROFILES_DRAFT_SAMPLE_PLACEHOLDER,
  PROFILES_DRAFT_SAVE,
  PROFILES_DRAFT_STATUS_ACTIVATED,
  PROFILES_DRAFT_STATUS_DRAFT,
  PROFILES_DRAFT_STATUS_IDLE,
  PROFILES_DRAFT_STATUS_SAVED,
  PROFILES_DRAFT_TOOLTIP_ACTIVATE,
  PROFILES_DRAFT_TOOLTIP_DUPLICATE,
  PROFILES_DRAFT_TOOLTIP_IMPORT,
  PROFILES_DRAFT_TOOLTIP_NEW,
  PROFILES_DRAFT_TOOLTIP_SAVE,
  PROFILES_DRAFT_YAML_LOCK,
} from '../../utils/conversionProfilesCopy';
import {
  diagnosticsFromYaml,
  yamlLooksInvalid,
  type RegexDiagnostic,
} from '../../utils/libraryYamlDiagnostics';
import { Button } from './ui/button';
import { Card } from './ui/card';
import { Tooltip, TooltipContent, TooltipTrigger } from './ui/tooltip';

type DraftStatus = 'idle' | 'draft' | 'saved' | 'activated';

export type LibraryDraftSchemaBlock = {
  id: string;
  label: string;
  cards: Array<{ id: string; label: string }>;
};

export type LibraryDraftShellProps = {
  /** Library kind for template defaults. */
  kind: LibraryAssetKind;
  /** Optional JWT — persist draft / activate when signed in. */
  accessToken?: string;
  /** Optional built-in asset name shown when duplicating. */
  sourceAssetName?: string;
  /** Mined IWXXM schema blocks (Conversion Phase B); falls back to stub. */
  schemaBlocks?: LibraryDraftSchemaBlock[];
  /** Notifies parent when draft status changes (for catalog inspector). */
  onDraftStatusChange?: (status: DraftStatus) => void;
};

const TEMPLATE_YAML: Record<LibraryAssetKind, string> = {
  conversion: `# Conversion library draft
kind: conversion
name: New conversion draft
blocks:
  - observation
  - cloud
`,
  tac_validation: `# TAC validation draft
kind: tac_validation
name: New TAC validation draft
rules:
  - pattern: "(?P<wind>\\\\d{5})KT"
    sample: "18004KT"
`,
  iwxxm_validation: `# IWXXM validation draft
kind: iwxxm_validation
name: New IWXXM validation draft
profiles: []
`,
  dissemination: `# Dissemination draft
kind: dissemination
name: New dissemination draft
transforms: []
`,
  decoding: `# Decoding draft
kind: decoding
name: New decoding draft
entries: []
`,
};

const DUPLICATE_YAML: Record<LibraryAssetKind, string> = {
  conversion: `# Duplicated conversion asset
kind: conversion
name: Forked conversion asset
fork_of: built-in
blocks:
  - observation
`,
  tac_validation: `# Duplicated TAC validation asset
kind: tac_validation
name: Forked TAC validation asset
fork_of: built-in
rules: []
`,
  iwxxm_validation: `# Duplicated IWXXM validation asset
kind: iwxxm_validation
name: Forked IWXXM validation asset
fork_of: built-in
profiles: []
`,
  dissemination: `# Duplicated dissemination asset
kind: dissemination
name: Forked dissemination asset
fork_of: built-in
transforms: []
`,
  decoding: `# Duplicated decoding asset
kind: decoding
name: Forked decoding asset
fork_of: built-in
entries: []
`,
};

const BLOCKS = [
  {
    id: 'observation',
    label: PROFILES_DRAFT_BLOCK_OBSERVATION,
    cards: [PROFILES_DRAFT_CARD_WIND, PROFILES_DRAFT_CARD_VISIBILITY],
  },
  {
    id: 'cloud',
    label: PROFILES_DRAFT_BLOCK_CLOUD,
    cards: [PROFILES_DRAFT_CARD_CLOUD_AMOUNT],
  },
  {
    id: 'rvr',
    label: PROFILES_DRAFT_BLOCK_RVR,
    cards: [PROFILES_DRAFT_CARD_RVR],
  },
] as const;

function DraftHelpTooltip({ label, tooltip }: { label: string; tooltip: string }) {
  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <button
          type="button"
          className="inline-flex h-6 w-6 items-center justify-center rounded text-gray-500 hover:text-gray-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 dark:text-gray-400 dark:hover:text-gray-100"
          aria-label={label}
        >
          <CircleHelp className="h-3.5 w-3.5" aria-hidden />
        </button>
      </TooltipTrigger>
      <TooltipContent side="bottom" className="max-w-xs text-balance">
        {tooltip}
      </TooltipContent>
    </Tooltip>
  );
}

function yamlName(raw: string, fallback: string): string {
  const match = raw.match(/^name:\s*(.+)$/m);
  const value = match?.[1]?.trim();
  return value && value.length > 0 ? value.replaceAll('"', '') : fallback;
}

/**
 * Draft authoring shell with live regex diagnostics, YAML lock, and Activate.
 *
 * @param props.kind - Active library kind
 * @param props.accessToken - Optional JWT for persist
 * @param props.sourceAssetName - Built-in asset label for duplicate hint
 */
export function LibraryDraftShell({
  kind,
  accessToken,
  sourceAssetName,
  schemaBlocks,
  onDraftStatusChange,
}: LibraryDraftShellProps) {
  const [yaml, setYaml] = useState('');
  const [status, setStatus] = useState<DraftStatus>('idle');
  const [sample, setSample] = useState('');
  const [savedId, setSavedId] = useState<string | null>(null);
  const [persistError, setPersistError] = useState<string | null>(null);

  useEffect(() => {
    onDraftStatusChange?.(status);
  }, [onDraftStatusChange, status]);

  const invalidYaml = yamlLooksInvalid(yaml);
  const diagnostics = useMemo(
    () => diagnosticsFromYaml(yaml, sample.trim() || undefined),
    [yaml, sample],
  );
  const failCount = diagnostics.filter((item) => item.severity === 'fail').length;
  const canActivate = !invalidYaml && failCount === 0 && yaml.trim().length > 0;

  const displayBlocks = useMemo(() => {
    if (schemaBlocks && schemaBlocks.length > 0) {
      return schemaBlocks.map((block) => ({
        id: block.id,
        label: block.label,
        cards: block.cards.map((card) => card.label),
        cardIds: block.cards.map((card) => card.id),
      }));
    }
    return BLOCKS.map((block) => ({
      id: block.id,
      label: block.label,
      cards: [...block.cards],
      cardIds: block.cards.map((card) => card),
    }));
  }, [schemaBlocks]);

  const statusLabel = useMemo(() => {
    if (status === 'activated') {
      return PROFILES_DRAFT_STATUS_ACTIVATED;
    }
    if (status === 'saved') {
      return PROFILES_DRAFT_STATUS_SAVED;
    }
    if (status === 'draft') {
      return PROFILES_DRAFT_STATUS_DRAFT;
    }
    return PROFILES_DRAFT_STATUS_IDLE;
  }, [status]);

  const loadTemplate = useCallback(() => {
    setYaml(TEMPLATE_YAML[kind]);
    setStatus('draft');
    setPersistError(null);
  }, [kind]);

  const duplicateBuiltin = useCallback(() => {
    const header = sourceAssetName ? `# Duplicated from ${sourceAssetName}\n` : '';
    setYaml(`${header}${DUPLICATE_YAML[kind]}`);
    setStatus('draft');
    setPersistError(null);
  }, [kind, sourceAssetName]);

  const persist = useCallback(
    async (lifecycle: 'draft' | 'activated') => {
      const token = accessToken?.trim();
      if (!token) {
        setStatus(lifecycle === 'activated' ? 'activated' : 'saved');
        return;
      }
      const name = yamlName(yaml, `New ${kind} draft`);
      const slug = `draft-${kind}-${Date.now().toString(36)}`;
      try {
        if (savedId) {
          const updated = await updateLibraryAsset(token, savedId, {
            name,
            yamlBody: yaml,
            status: lifecycle,
          });
          setSavedId(updated.id);
        } else {
          const created = await createLibraryAsset(token, {
            slug,
            name,
            kind,
            engineProfileId: 'ICAO_2025',
            attachedNationalLine: 'ICAO_2025',
            yamlBody: yaml,
            status: lifecycle,
          });
          setSavedId(created.id);
        }
        setPersistError(null);
        setStatus(lifecycle === 'activated' ? 'activated' : 'saved');
      } catch (error) {
        setPersistError(error instanceof Error ? error.message : 'Save failed');
      }
    },
    [accessToken, kind, savedId, yaml],
  );

  const saveDraft = useCallback(() => {
    void persist('draft');
  }, [persist]);

  const activate = useCallback(() => {
    void persist('activated');
  }, [persist]);

  return (
    <Card
      className="mt-4 space-y-4 border-dashed p-4"
      data-testid={`library-draft-shell-${kind}`}
    >
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div className="space-y-1">
          <h3 className="text-sm font-medium text-gray-900 dark:text-gray-100">
            {PROFILES_DRAFT_HEADING}
          </h3>
          <p className="text-xs text-gray-600 dark:text-gray-400">
            {PROFILES_DRAFT_HELP}
          </p>
        </div>
        <span
          className="rounded-full border border-amber-300 bg-amber-50 px-2 py-0.5 text-xs font-medium text-amber-900 dark:border-amber-700 dark:bg-amber-950/40 dark:text-amber-100"
          data-testid={`library-draft-status-${kind}`}
        >
          {statusLabel}
        </span>
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <div className="flex items-center gap-1">
          <Button
            type="button"
            variant="outline"
            size="sm"
            data-testid={`library-draft-new-template-${kind}`}
            onClick={loadTemplate}
          >
            {PROFILES_DRAFT_NEW_TEMPLATE}
          </Button>
          <DraftHelpTooltip
            label={`About ${PROFILES_DRAFT_NEW_TEMPLATE}`}
            tooltip={PROFILES_DRAFT_TOOLTIP_NEW}
          />
        </div>
        <div className="flex items-center gap-1">
          <Button
            type="button"
            variant="outline"
            size="sm"
            data-testid={`library-draft-duplicate-${kind}`}
            onClick={duplicateBuiltin}
          >
            {PROFILES_DRAFT_DUPLICATE}
          </Button>
          <DraftHelpTooltip
            label={`About ${PROFILES_DRAFT_DUPLICATE}`}
            tooltip={PROFILES_DRAFT_TOOLTIP_DUPLICATE}
          />
        </div>
        <div className="ml-auto flex items-center gap-1">
          <Button
            type="button"
            size="sm"
            data-testid={`library-draft-save-${kind}`}
            onClick={saveDraft}
            disabled={!yaml.trim()}
          >
            {PROFILES_DRAFT_SAVE}
          </Button>
          <DraftHelpTooltip
            label={`About ${PROFILES_DRAFT_SAVE}`}
            tooltip={PROFILES_DRAFT_TOOLTIP_SAVE}
          />
          <Button
            type="button"
            size="sm"
            data-testid={`library-draft-activate-${kind}`}
            onClick={activate}
            disabled={!canActivate}
          >
            {PROFILES_DRAFT_ACTIVATE}
          </Button>
          <DraftHelpTooltip
            label={`About ${PROFILES_DRAFT_ACTIVATE}`}
            tooltip={PROFILES_DRAFT_TOOLTIP_ACTIVATE}
          />
        </div>
      </div>

      {invalidYaml && yaml.trim() ? (
        <p
          className="text-xs text-amber-800 dark:text-amber-200"
          data-testid={`library-draft-yaml-lock-${kind}`}
        >
          {PROFILES_DRAFT_YAML_LOCK}
        </p>
      ) : null}
      {!canActivate && yaml.trim() && !invalidYaml ? (
        <p
          className="text-xs text-amber-800 dark:text-amber-200"
          data-testid={`library-draft-activate-blocked-${kind}`}
        >
          {PROFILES_DRAFT_ACTIVATE_BLOCKED}
        </p>
      ) : null}
      {persistError ? (
        <p
          className="text-xs text-red-700 dark:text-red-300"
          data-testid={`library-draft-persist-error-${kind}`}
        >
          {persistError}
        </p>
      ) : null}

      <label className="block space-y-1 text-sm">
        <span className="flex items-center gap-1 text-gray-700 dark:text-gray-300">
          {PROFILES_DRAFT_IMPORT_LABEL}
          <DraftHelpTooltip
            label={`About ${PROFILES_DRAFT_IMPORT_LABEL}`}
            tooltip={PROFILES_DRAFT_TOOLTIP_IMPORT}
          />
        </span>
        <textarea
          className="min-h-28 w-full rounded border border-gray-300 bg-white p-2 font-mono text-xs dark:border-gray-600 dark:bg-gray-900"
          data-testid={`library-draft-yaml-${kind}`}
          placeholder={PROFILES_DRAFT_IMPORT_PLACEHOLDER}
          value={yaml}
          onChange={(event) => {
            setYaml(event.target.value);
            setStatus(event.target.value.trim() ? 'draft' : 'idle');
          }}
        />
      </label>

      <details
        className="rounded border border-gray-200 p-3 dark:border-gray-700"
        data-testid={`library-draft-sample-${kind}`}
      >
        <summary className="cursor-pointer text-sm font-medium text-gray-900 dark:text-gray-100">
          {PROFILES_DRAFT_SAMPLE_HEADING}
        </summary>
        <p className="mt-1 text-xs text-gray-600 dark:text-gray-400">
          {PROFILES_DRAFT_SAMPLE_HELP}
        </p>
        <textarea
          className="mt-2 min-h-16 w-full rounded border border-gray-300 bg-white p-2 font-mono text-xs dark:border-gray-600 dark:bg-gray-900"
          data-testid={`library-draft-sample-input-${kind}`}
          placeholder={PROFILES_DRAFT_SAMPLE_PLACEHOLDER}
          value={sample}
          onChange={(event) => setSample(event.target.value)}
        />
      </details>

      <div className="space-y-2" data-testid={`library-draft-diagnostics-${kind}`}>
        <div>
          <h4 className="text-sm font-medium text-gray-900 dark:text-gray-100">
            {PROFILES_DRAFT_DIAGNOSTICS_HEADING}
          </h4>
          <p className="text-xs text-gray-600 dark:text-gray-400">
            {PROFILES_DRAFT_DIAGNOSTICS_HELP}
          </p>
        </div>
        <ul className="space-y-1 text-xs">
          {diagnostics.map((item: RegexDiagnostic) => (
            <li
              key={`${item.path}-${item.pattern}`}
              data-testid={`library-draft-diag-${item.severity}-${kind}`}
            >
              <span className="font-medium uppercase">{item.severity}</span>
              {` ${item.path}: ${item.message}`}
              {item.captures.length > 0 ? (
                <span>
                  {` ${PROFILES_DRAFT_CAPTURES_HEADING}: ${item.captures.map((c) => c.name).join(', ')}`}
                </span>
              ) : null}
            </li>
          ))}
        </ul>
      </div>

      <div className="space-y-2" data-testid={`library-draft-blocks-${kind}`}>
        <div>
          <h4 className="text-sm font-medium text-gray-900 dark:text-gray-100">
            {PROFILES_DRAFT_BLOCKS_HEADING}
          </h4>
          <p className="text-xs text-gray-600 dark:text-gray-400">
            {PROFILES_DRAFT_BLOCKS_HELP}
          </p>
        </div>
        <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
          {displayBlocks.map((block) => (
            <div
              key={block.id}
              className="min-h-32 rounded-lg border border-dashed border-gray-300 bg-gray-50/80 p-3 dark:border-gray-600 dark:bg-gray-900/40"
              data-testid={`library-draft-block-${block.id}-${kind}`}
              aria-disabled={invalidYaml}
            >
              <p className="text-xs font-medium uppercase tracking-wide text-gray-500">
                {block.label}
              </p>
              <ul className="mt-2 space-y-2">
                {block.cards.map((card, index) => (
                  <li
                    key={`${block.id}-${index}`}
                    className={`rounded border border-gray-200 bg-white px-2 py-1.5 text-xs shadow-sm dark:border-gray-700 dark:bg-gray-800 ${invalidYaml ? 'opacity-60' : ''}`}
                    data-testid={`library-draft-card-${block.id}-${card.replace(/\s+/g, '-').toLowerCase()}-${kind}`}
                    title={block.cardIds[index]}
                  >
                    {card}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </Card>
  );
}
