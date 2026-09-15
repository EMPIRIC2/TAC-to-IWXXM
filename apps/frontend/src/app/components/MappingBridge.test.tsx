/**
 * MappingBridge unit tests (TC-EVBRIDGE-006 columns).
 */

import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';

import { MappingBridge } from './MappingBridge';

describe('MappingBridge', () => {
  it('renders three columns and unmatched fail-closed hint', () => {
    render(
      <MappingBridge
        tacGroup="VRB03KT"
        templateName="Wind group"
        matched={false}
        iwxxmBlock=""
      />,
    );
    expect(screen.getByTestId('mapping-bridge')).toBeInTheDocument();
    expect(
      screen.getByTestId('mapping-bridge').querySelector('[data-testid="beta-badge"]'),
    ).toBeTruthy();
    expect(screen.getByTestId('mapping-bridge-col-tac')).toHaveTextContent('VRB03KT');
    expect(screen.getByTestId('mapping-bridge-col-template')).toHaveTextContent(
      'Wind group',
    );
    expect(screen.getByTestId('mapping-bridge-match-status')).toHaveTextContent(
      /No matching conversion rule/i,
    );
    expect(screen.getByTestId('mapping-bridge-unmatched-hint')).toBeInTheDocument();
    expect(screen.getByTestId('mapping-bridge-col-iwxxm')).toBeInTheDocument();
  });

  it('renders matched IWXXM block and skip chips', () => {
    render(
      <MappingBridge
        tacGroup="18012G20KT"
        templateName="Wind group"
        matched={true}
        iwxxmBlock="<iwxxm:WindObservation/>"
        skipChips={[{ label: 'noise', gloss: 'etc.' }]}
      />,
    );
    expect(screen.getByTestId('mapping-bridge-iwxxm-block')).toHaveTextContent(
      'WindObservation',
    );
    expect(screen.getByTestId('mapping-bridge-skip-chips')).toHaveTextContent('noise');
  });
});
