/**
 * TC-UX-DECLUTTER-005 — Settings cog accessible name.
 *
 * [Corpus: tests §TC-UX-DECLUTTER]
 */

import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';

import { ConvertSettingsCog } from './ConvertSettingsCog';

describe('ConvertSettingsCog', () => {
  it('TC-UX-DECLUTTER-005: cog has Settings accessible name and hover card', () => {
    render(
      <ConvertSettingsCog>
        <div>body</div>
      </ConvertSettingsCog>,
    );
    const cog = screen.getByTestId('convert-settings-cog');
    expect(cog).toHaveAttribute('aria-label', 'Settings');
    expect(cog).not.toHaveAttribute('title');
    expect(screen.getByTestId('icon-hover-card')).toHaveTextContent('Settings');
  });
});
