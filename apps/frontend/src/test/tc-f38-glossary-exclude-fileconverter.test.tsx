/**
 * TC-F38-003 — TAC / IWXXM hosts declare data-glossary-exclude in source.
 */

import { readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { describe, expect, it } from 'vitest';

const HERE = dirname(fileURLToPath(import.meta.url));
const FRONTEND_ROOT = resolve(HERE, '../..');

describe('glossary editor exclusion inventory (TC-F38-003)', () => {
  it('FileConverter TAC host sets data-glossary-exclude', () => {
    const src = readFileSync(
      resolve(FRONTEND_ROOT, 'src/app/components/FileConverter.tsx'),
      'utf8',
    );
    expect(src).toMatch(
      /data-testid=\{\s*[\s\S]*?convert-tac-editable[\s\S]*?data-glossary-exclude="true"/,
    );
  });

  it('IwxxmPreviewPane root sets data-glossary-exclude', () => {
    const src = readFileSync(
      resolve(FRONTEND_ROOT, 'src/app/components/IwxxmPreviewPane.tsx'),
      'utf8',
    );
    expect(src).toMatch(
      /data-testid="iwxxm-preview-pane"[\s\S]*?data-glossary-exclude="true"/,
    );
  });
});
