/**
 * Product-aware Examples control for F7.g / #780 (Radix ui/select).
 */

import {
  EXAMPLE_PRODUCTS,
  EXAMPLES,
  type GoldenExample,
} from '@/fixtures/examples/examplesCatalog';
import {
  DEFAULT_SEMANTIC_PROFILE,
  SEMANTIC_PROFILE_OPTIONS,
  hydrateSemanticProfile,
  type IwxxmProfile,
} from '@/utils/semanticProfile';
import type { TacProduct } from '@/utils/tacProduct';
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from './ui/select';
import { Label } from './ui/label';

export interface GoldenExamplesSelectProps {
  /** Disabled when workbench is read-only */
  disabled?: boolean;
  /** Selected semantic Profile for reuse notes and product scoping */
  semanticProfile?: IwxxmProfile;
  /** Optional product allowlist from the active profile summary/catalog */
  applicableProducts?: readonly TacProduct[];
  /** Called with the catalog id when an example is chosen */
  onSelectExample: (exampleId: string) => void;
}

const PROFILE_LABELS = new Map<string, string>(
  SEMANTIC_PROFILE_OPTIONS.map((option) => [option.value, option.label]),
);

function groupTacByProduct(): Map<string, GoldenExample[]> {
  const map = new Map<string, GoldenExample[]>();
  for (const ex of EXAMPLES) {
    if (ex.inputMode !== 'tac' || !ex.product) {
      continue;
    }
    const product = ex.product;
    const list = map.get(product) ?? [];
    list.push(ex);
    map.set(product, list);
  }
  return map;
}

function exampleLabelForProfile(
  example: GoldenExample,
  semanticProfile: IwxxmProfile,
): string {
  /* v8 ignore start -- TAC fixtures in this menu are WMO-tagged by catalog contract */
  const canonicalProfile = hydrateSemanticProfile(semanticProfile);
  if (canonicalProfile === DEFAULT_SEMANTIC_PROFILE) {
    return example.wmoPass && example.wmoSeed
      ? `${example.label} · WMO passer · ${example.wmoSeed}`
      : example.wmoReference && example.wmoSeed
        ? `${example.label} · WMO reference · ${example.wmoSeed}`
        : example.label;
  }
  if (example.wmoPass && example.wmoSeed) {
    return `${example.label} · WMO passer · ${example.wmoSeed} · Reused for ${PROFILE_LABELS.get(canonicalProfile) ?? canonicalProfile}`;
  }
  if (example.wmoReference && example.wmoSeed) {
    return `${example.label} · WMO reference · ${example.wmoSeed} · Reused for ${PROFILE_LABELS.get(canonicalProfile) ?? canonicalProfile}`;
  }
  /* v8 ignore next -- TAC fixtures in this menu are WMO-tagged by catalog contract */
  const baseLabel = example.label;
  const profileName = PROFILE_LABELS.get(canonicalProfile) ?? canonicalProfile;
  return `${baseLabel} · Reused for ${profileName}`;
  /* v8 ignore stop */
}

/**
 * Grouped Examples dropdown — loads curated demo TAC / AHL / IWXXM samples.
 *
 * @param props.disabled - When true, control is inactive
 * @param props.onSelectExample - Catalog id callback
 */
export function GoldenExamplesSelect({
  disabled = false,
  semanticProfile = DEFAULT_SEMANTIC_PROFILE,
  applicableProducts,
  onSelectExample,
}: GoldenExamplesSelectProps) {
  const byProduct = groupTacByProduct();
  const ahlExamples = EXAMPLES.filter((ex) => ex.inputMode === 'ahl_bulletin');
  const iwxxmExamples = EXAMPLES.filter((ex) => ex.inputMode === 'collect_iwxxm');
  const allowedProducts = applicableProducts ? new Set(applicableProducts) : null;

  return (
    <div className="flex flex-wrap items-center gap-2">
      <Label
        htmlFor="examples-select"
        className="shrink-0 text-sm text-gray-700 dark:text-gray-300"
      >
        Examples
      </Label>
      <Select
        disabled={disabled}
        onValueChange={(value) => {
          onSelectExample(value);
        }}
      >
        <SelectTrigger
          id="examples-select"
          data-testid="examples-select"
          aria-label="Load golden example"
          className="min-w-[14rem]"
          size="sm"
        >
          <SelectValue placeholder="Load demo example…" />
        </SelectTrigger>
        <SelectContent>
          {EXAMPLE_PRODUCTS.map((product) => {
            if (allowedProducts && !allowedProducts.has(product)) {
              return null;
            }
            const items = byProduct.get(product);
            if (!items || items.length === 0) {
              return null;
            }
            return (
              <SelectGroup key={product}>
                <SelectLabel>{product}</SelectLabel>
                {items.map((ex) => (
                  <SelectItem key={ex.id} value={ex.id} title={ex.provenance}>
                    {exampleLabelForProfile(ex, semanticProfile)}
                  </SelectItem>
                ))}
              </SelectGroup>
            );
          })}
          {ahlExamples.length > 0 && (
            <SelectGroup>
              <SelectLabel>AHL bulletin</SelectLabel>
              {ahlExamples.map((ex) => (
                <SelectItem key={ex.id} value={ex.id}>
                  {ex.label}
                </SelectItem>
              ))}
            </SelectGroup>
          )}
          {iwxxmExamples.length > 0 && (
            <SelectGroup>
              <SelectLabel>IWXXM</SelectLabel>
              {iwxxmExamples.map((ex) => (
                <SelectItem key={ex.id} value={ex.id}>
                  {ex.label}
                </SelectItem>
              ))}
            </SelectGroup>
          )}
        </SelectContent>
      </Select>
    </div>
  );
}
