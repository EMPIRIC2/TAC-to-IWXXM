/**
 * Product-aware Examples control for F7.g / #780 (Radix ui/select).
 */

import {
  EXAMPLE_PRODUCTS,
  EXAMPLES,
  type GoldenExample,
} from '@/fixtures/examples/examplesCatalog';
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
  /** Called with the catalog id when an example is chosen */
  onSelectExample: (exampleId: string) => void;
}

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

/**
 * Grouped Examples dropdown — loads curated demo TAC / AHL / IWXXM samples.
 *
 * @param props.disabled - When true, control is inactive
 * @param props.onSelectExample - Catalog id callback
 */
export function GoldenExamplesSelect({
  disabled = false,
  onSelectExample,
}: GoldenExamplesSelectProps) {
  const byProduct = groupTacByProduct();
  const ahlExamples = EXAMPLES.filter((ex) => ex.inputMode === 'ahl_bulletin');
  const iwxxmExamples = EXAMPLES.filter((ex) => ex.inputMode === 'collect_iwxxm');

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
            const items = byProduct.get(product);
            if (!items || items.length === 0) {
              return null;
            }
            return (
              <SelectGroup key={product}>
                <SelectLabel>{product}</SelectLabel>
                {items.map((ex) => (
                  <SelectItem key={ex.id} value={ex.id} title={ex.provenance}>
                    {ex.wmoPass && ex.wmoSeed
                      ? `${ex.label} · WMO passer · ${ex.wmoSeed}`
                      : ex.wmoReference && ex.wmoSeed
                        ? `${ex.label} · WMO reference · ${ex.wmoSeed}`
                        : ex.label}
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
