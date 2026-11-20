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

  it('prefixes RMK when remarks omit the token', () => {
    const tac = buildMetarSpeciTac({
      product: 'METAR',
      cor: true,
      auto: true,
      nil: false,
      cccc: 'KJFK',
      dayTime: '211025',
      wind: '18010KT',
      visibility: '9999',
      rvr: '',
      weather: '',
      cloud: 'FEW250',
      temperature: '15/07',
      qnh: 'Q1013',
      supplementary: '',
      rmk: 'AO2 SLP176',
      includeRmk: true,
    });
    expect(tac).toBe(
      'METAR COR KJFK 211025Z AUTO 18010KT 9999 FEW250 15/07 Q1013 RMK AO2 SLP176=',
    );
  });

  it('keeps an existing RMK token and builds NIL reports', () => {
    const withRmk = buildMetarSpeciTac({
      product: 'SPECI',
      cor: false,
      auto: false,
      nil: false,
      cccc: 'KJFK',
      dayTime: '211025Z',
      wind: '18010KT',
      visibility: '9999',
      rvr: '',
      weather: '',
      cloud: '',
      temperature: '15/07',
      qnh: 'Q1013',
      supplementary: '',
      rmk: 'RMK AO2',
      includeRmk: true,
    });
    expect(withRmk).toBe('SPECI KJFK 211025Z 18010KT 9999 15/07 Q1013 RMK AO2=');

    const nilTac = buildMetarSpeciTac({
      product: 'METAR',
      cor: false,
      auto: false,
      nil: true,
      cccc: 'KJFK',
      dayTime: '211025Z',
      wind: '',
      visibility: '',
      rvr: '',
      weather: '',
      cloud: '',
      temperature: '',
      qnh: '',
      supplementary: '',
      rmk: 'AO2',
      includeRmk: true,
    });
    expect(nilTac).toBe('METAR KJFK 211025Z NIL=');
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

  it('toggles product COR AUTO NIL and RMK include, and shows lint issues', async () => {
    const user = userEvent.setup();
    render(
      <MetarSpeciStructuredForm
        onInsertTac={vi.fn()}
        defaultProduct="METAR"
        lintIssues={[
          {
            severity: 'warning',
            code: 'COR_PRESENT',
            message: 'COR after product',
          },
        ]}
      />,
    );

    await user.selectOptions(screen.getByTestId('structured-product'), 'SPECI');
    await user.click(screen.getByTestId('structured-cor'));
    await user.click(screen.getByTestId('structured-auto'));
    await user.type(screen.getByTestId('structured-cccc'), 'KJFK');
    await user.type(screen.getByTestId('structured-daytime'), '211025Z');
    await user.type(screen.getByTestId('structured-rmk'), 'AO2');
    await user.click(screen.getByTestId('structured-include-rmk'));
    expect(screen.getByTestId('structured-tac-preview')).toHaveTextContent(
      'SPECI COR KJFK 211025Z AUTO',
    );
    expect(screen.getByTestId('structured-tac-preview')).not.toHaveTextContent('RMK');

    await user.click(screen.getByTestId('structured-nil'));
    expect(screen.getByTestId('structured-tac-preview')).toHaveTextContent(
      'SPECI COR KJFK 211025Z NIL=',
    );
    expect(screen.getByTestId('structured-auto')).toBeDisabled();
    expect(screen.getByTestId('structured-auto')).not.toBeChecked();
    // Uncheck NIL so the false branch of "if checked clear AUTO" is covered.
    await user.click(screen.getByTestId('structured-nil'));
    expect(screen.getByTestId('structured-nil')).not.toBeChecked();
    expect(screen.getByTestId('structured-auto')).not.toBeDisabled();
    expect(screen.getByTestId('structured-lint-summary')).toHaveTextContent(
      'warning: COR after product',
    );
  });
});
