/**
 * Draft authoring shell for Profile builder library kinds (Phase A stub).
 */

import { CircleHelp, GripVertical } from 'lucide-react';
import { useCallback, useEffect, useMemo, useState } from 'react';

import type { LibraryAssetKind } from '../../utils/conversionProfilesApi';
import {
  PROFILES_DRAFT_BLOCK_CLOUD,
  PROFILES_DRAFT_BLOCK_OBSERVATION,
  PROFILES_DRAFT_BLOCK_RVR,
  PROFILES_DRAFT_BLOCKS_HEADING,
  PROFILES_DRAFT_BLOCKS_HELP,
  PROFILES_DRAFT_CARD_CLOUD_AMOUNT,
  PROFILES_DRAFT_CARD_RVR,
  PROFILES_DRAFT_CARD_VISIBILITY,
  PROFILES_DRAFT_CARD_WIND,
  PROFILES_DRAFT_DUPLICATE,
  PROFILES_DRAFT_HEADING,
  PROFILES_DRAFT_HELP,
  PROFILES_DRAFT_IMPORT_LABEL,
  PROFILES_DRAFT_IMPORT_PLACEHOLDER,
  PROFILES_DRAFT_NEW_TEMPLATE,
  PROFILES_DRAFT_SAVE,
  PROFILES_DRAFT_STATUS_DRAFT,
  PROFILES_DRAFT_STATUS_IDLE,
  PROFILES_DRAFT_STATUS_SAVED,
  PROFILES_DRAFT_TOOLTIP_DUPLICATE,
  PROFILES_DRAFT_TOOLTIP_IMPORT,
  PROFILES_DRAFT_TOOLTIP_NEW,
  PROFILES_DRAFT_TOOLTIP_SAVE,
} from '../../utils/conversionProfilesCopy';
import { Button } from './ui/button';
import { Card } from './ui/card';
import { Tooltip, TooltipContent, TooltipTrigger } from './ui/tooltip';

type DraftStatus = 'idle' | 'draft' | 'saved';

export type LibraryDraftShellProps = {
  /** Library kind for template defaults. */
  kind: LibraryAssetKind;
  /** Optional built-in asset name shown when duplicating. */
  sourceAssetName?: string;
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
rules: []
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

/**
 * Draft authoring shell with template, duplicate, import YAML, and block skeleton.
 *
 * @param props.kind - Active library kind
 * @param props.sourceAssetName - Built-in asset label for duplicate hint
 */
export function LibraryDraftShell({
  kind,
  sourceAssetName,
  onDraftStatusChange,
}: LibraryDraftShellProps) {
  const [yaml, setYaml] = useState('');
  const [status, setStatus] = useState<DraftStatus>('idle');

  useEffect(() => {
    onDraftStatusChange?.(status);
  }, [onDraftStatusChange, status]);

  const statusLabel = useMemo(() => {
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
  }, [kind]);

  const duplicateBuiltin = useCallback(() => {
    const header = sourceAssetName ? `# Duplicated from ${sourceAssetName}\n` : '';
    setYaml(`${header}${DUPLICATE_YAML[kind]}`);
    setStatus('draft');
  }, [kind, sourceAssetName]);

  const saveDraft = useCallback(() => {
    if (!yaml.trim()) {
      return;
    }
    setStatus('saved');
  }, [yaml]);

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
        </div>
      </div>

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
          {BLOCKS.map((block) => (
            <div
              key={block.id}
              className="min-h-32 rounded-lg border border-dashed border-gray-300 bg-gray-50/80 p-3 dark:border-gray-600 dark:bg-gray-900/40"
              data-testid={`library-draft-block-${block.id}-${kind}`}
            >
              <p className="text-xs font-medium uppercase tracking-wide text-gray-500">
                {block.label}
              </p>
              <ul className="mt-2 space-y-2">
                {block.cards.map((card) => (
                  <li
                    key={card}
                    className="flex cursor-grab items-center gap-2 rounded border border-gray-200 bg-white px-2 py-1.5 text-xs shadow-sm active:cursor-grabbing dark:border-gray-700 dark:bg-gray-800"
                    data-testid={`library-draft-card-${block.id}-${card.replace(/\s+/g, '-').toLowerCase()}-${kind}`}
                  >
                    <GripVertical
                      className="h-3.5 w-3.5 shrink-0 text-gray-400"
                      aria-hidden
                    />
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
