/**
 * TC-EVYCL-001 — Profile Builder authoring modules removed (#1251 / ADR-044).
 */

import { describe, expect, it } from 'vitest';
import { existsSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const componentsDir = join(
  dirname(fileURLToPath(import.meta.url)),
  '../app/components',
);

const RETIRED_AUTHORING_MODULES = [
  'ProfileBuilderLibraries.tsx',
  'LibraryDraftShell.tsx',
  'LibraryWorkbenchShell.tsx',
  'ConversionProfilePage.tsx',
  'ConversionTemplatesPanel.tsx',
  'ConversionCatalogPicker.tsx',
  'DecodingLibraryPanel.tsx',
  'DisseminationLibraryPanel.tsx',
  'TacValidationRulesPanel.tsx',
  'IwxxmValidationRulesPanel.tsx',
  'LibraryAssetsListPanel.tsx',
  'ProfileOverviewPanel.tsx',
  'WorkbenchMappingBridge.tsx',
] as const;

describe('TC-EVYCL-001 Profile Builder authoring deleted', () => {
  it.each(RETIRED_AUTHORING_MODULES)('removes %s from the tree', (name) => {
    expect(existsSync(join(componentsDir, name))).toBe(false);
  });
});
