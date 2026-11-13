import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { MetarSpeciStructuredForm } from './MetarSpeciStructuredForm';
import { buildMetarSpeciTac } from './metarSpeciStructuredTac';

describe('MetarSpeciStructuredForm', () => {
  it('builds SPECI LUDO handbook-style TAC', () => {
    const tac = buildMetarSpeciTac({
      product: 'SPECI',
      cor: false,
      auto: false,
      nil: false,
      cccc: 'LUDO',
      dayTime: '211025Z',
      wind: '31015G27KT 280V350',
      visibility: '4000',
      rvr: 'R24/P2000',
      weather: '+SHRA',
      cloud: 'FEW005 SCT018',
      temperature: '10/03',
      qnh: 'Q0995',
      supplementary: '',
      rmk: '',
      includeRmk: true,
    });
    expect(tac).toBe(
      'SPECI LUDO 211025Z 31015G27KT 280V350 4000 R24/P2000 +SHRA FEW005 SCT018 10/03 Q0995=',
    );
  });

  it('omits RMK when include remarks is off', () => {
    const tac = buildMetarSpeciTac({
      product: 'METAR',
      cor: false,
      auto: false,
      nil: false,
      cccc: 'KJFK',
      dayTime: '211025Z',
      wind: '18010KT',
      visibility: 'CAVOK',
      rvr: '',
      weather: '',
      cloud: '',
      temperature: '15/07',
      qnh: 'Q1013',
      supplementary: '',
      rmk: 'AO2 SLP176',
      includeRmk: false,
    });
    expect(tac).toBe('METAR KJFK 211025Z 18010KT CAVOK 15/07 Q1013=');
    expect(tac).not.toContain('RMK');
  });

  it('inserts TAC from the form', async () => {
    const user = userEvent.setup();
    const onInsertTac = vi.fn();
    render(
      <MetarSpeciStructuredForm onInsertTac={onInsertTac} defaultProduct="SPECI" />,
    );
    await user.type(screen.getByTestId('structured-cccc'), 'LUDO');
    await user.type(screen.getByTestId('structured-daytime'), '211025Z');
    await user.type(screen.getByTestId('structured-wind'), '31015KT');
    await user.type(screen.getByTestId('structured-visibility'), 'CAVOK');
    await user.type(screen.getByTestId('structured-temperature'), '10/03');
    await user.type(screen.getByTestId('structured-qnh'), 'Q0995');
    await user.click(screen.getByTestId('structured-insert-tac'));
    expect(onInsertTac).toHaveBeenCalledWith(
      'SPECI LUDO 211025Z 31015KT CAVOK 10/03 Q0995=',
    );
  });

  it('converts with assembled TAC through the existing converter callback', async () => {
    const user = userEvent.setup();
    const onConvertWithTac = vi.fn();
    render(
      <MetarSpeciStructuredForm
        onInsertTac={vi.fn()}
        onConvertWithTac={onConvertWithTac}
        defaultProduct="METAR"
      />,
    );
    await user.type(screen.getByTestId('structured-cccc'), 'KJFK');
    await user.type(screen.getByTestId('structured-daytime'), '211025Z');
    await user.type(screen.getByTestId('structured-wind'), '18005KT');
    await user.type(screen.getByTestId('structured-visibility'), '9999');
    await user.type(screen.getByTestId('structured-temperature'), '15/07');
    await user.type(screen.getByTestId('structured-qnh'), 'Q1013');
    await user.click(screen.getByTestId('structured-convert-tac'));
    expect(onConvertWithTac).toHaveBeenCalledWith(
      'METAR KJFK 211025Z 18005KT 9999 15/07 Q1013=',
    );
  });
});
