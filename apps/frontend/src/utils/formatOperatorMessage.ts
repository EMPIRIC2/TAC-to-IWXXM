/**
 * Format lint registry message templates for operators.
 *
 * Catalog and soft-preview often lack live kwargs. Prefer a readable noun
 * (for example ``report``) over literal ``{product}`` braces.
 */

const DEFAULTS: Record<string, string> = {
  product: 'report',
  token: 'token',
  expected: 'supported products',
  keywords: 'product keywords',
  hit: 'phenomena',
  family: 'register',
};

/**
 * Options for {@link formatOperatorMessageTemplate}.
 */
export type FormatOperatorMessageOptions = {
  product?: string | null;
  token?: string | null;
  expected?: string | null;
  keywords?: string | null;
  hit?: string | null;
  family?: string | null;
  [key: string]: string | null | undefined;
};

/**
 * Normalize a product label for operator sentences.
 *
 * @param product - Catalog or live product id
 * @returns Uppercase product when known; otherwise ``report``
 * @example
 * const _ = true;
 */
export function operatorProductLabel(product: string | null | undefined): string {
  const trimmed = (product ?? '').trim();
  if (!trimmed) {
    return DEFAULTS.product;
  }
  return trimmed.toUpperCase();
}

/**
 * Format a registry ``message_template`` without leaving raw ``{…}`` braces.
 *
 * Supports plain ``{name}`` and ``{name!r}`` (Python-style repr) fields used in
 * the tac-validate registry. Unknown fields are omitted.
 *
 * @param template - Registry message template
 * @param options - Optional placeholder values
 * @returns Operator-facing text
 * @example
 * const _ = true;
 */
export function formatOperatorMessageTemplate(
  template: string,
  options: FormatOperatorMessageOptions = {},
): string {
  const values: Record<string, string> = { ...DEFAULTS };
  for (const [key, raw] of Object.entries(options)) {
    if (raw == null) {
      continue;
    }
    const trimmed = String(raw).trim();
    if (!trimmed) {
      continue;
    }
    values[key] = key === 'product' ? operatorProductLabel(trimmed) : trimmed;
  }
  return template.replace(
    /\{([A-Za-z_][A-Za-z0-9_]*)(![rsa])?\}/g,
    (_full, name: string, conversion: string | undefined) => {
      if (!(name in values)) {
        return '';
      }
      const value = values[name]!;
      if (conversion === '!r') {
        return JSON.stringify(value);
      }
      return value;
    },
  );
}
