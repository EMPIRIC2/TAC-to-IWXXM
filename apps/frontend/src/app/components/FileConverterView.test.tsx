/* eslint-disable @typescript-eslint/no-explicit-any */
/**
 * FileConverterView: dissemination template change, profile radios, and profile reset.
 * Children and dialogs are stubbed so only the view's own handlers run.
 * FR-052..056 / DI-008: destinations default off; tests flip the flag and restore it.
 */
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { FileConverterView } from './FileConverterView';
import { operatorDisseminationUiConfig } from '@/utils/operatorDisseminationUi';
import { initialConversionParams } from '@/utils/fileConverterParams';
import { libraryResetForProfile } from '@/utils/profileLibraryReset';

vi.mock('/utils/supabase/logout', () => ({
  signOutWithScope: vi.fn().mockResolvedValue(true),
}));

vi.mock('./FileConverterHeader', () => ({ FileConverterHeader: () => null }));
vi.mock('./FileConverterIntro', () => ({ FileConverterIntro: () => null }));
vi.mock('./FileConverterGuestNotice', () => ({ FileConverterGuestNotice: () => null }));
vi.mock('./FileConverterActionStrip', () => ({ FileConverterActionStrip: () => null }));
vi.mock('./FileConverterDropZone', () => ({ FileConverterDropZone: () => null }));
vi.mock('./FileConverterFilename', () => ({ FileConverterFilename: () => null }));
vi.mock('./FileConverterBody', () => ({ FileConverterBody: () => null }));
vi.mock('./FileConverterChromeToolbar', () => ({
  FileConverterChromeToolbar: () => null,
}));
vi.mock('./FileConverterIwxxmPane', () => ({ FileConverterIwxxmPane: () => null }));
vi.mock('./FileConverterDecodePane', () => ({ FileConverterDecodePane: () => null }));
vi.mock('./FileConverterConsolePanel', () => ({
  FileConverterConsolePanel: () => null,
}));
vi.mock('./FileConverterDownloads', () => ({ FileConverterDownloads: () => null }));
vi.mock('./FileConverterQueue', () => ({ FileConverterQueue: () => null }));
vi.mock('./FileConverterRecentAside', () => ({ FileConverterRecentAside: () => null }));
vi.mock('./PrivacyNotice', () => ({ PrivacyNotice: () => null }));
vi.mock('./OperatorFooter', () => ({ OperatorFooter: () => null }));
vi.mock('./UserPreferencesDialog', () => ({ UserPreferencesDialog: () => null }));
vi.mock('./ConvertHelpChecklist', () => ({ ConvertHelpChecklist: () => null }));
vi.mock('./PrivacySettingsDialog', () => ({ PrivacySettingsDialog: () => null }));
vi.mock('./SiteTermsDialog', () => ({ SiteTermsDialog: () => null }));
vi.mock('./ConvertResultsDrawer', () => ({ ConvertResultsDrawer: () => null }));
vi.mock('./DisseminationDrawer', () => ({
  DisseminationDrawer: ({
    onDisseminationTemplateChange,
    onOpenChange,
    disseminationTemplateId,
    product,
    iwxxmXml,
  }: any) => (
    <div
      data-testid="dissemination-drawer-mock"
      data-template={disseminationTemplateId}
      data-product={product}
      data-xml={iwxxmXml}
    >
      <button type="button" onClick={() => onDisseminationTemplateChange('tpl-1')}>
        pick-template
      </button>
      <button type="button" onClick={() => onOpenChange(false)}>
        close-drawer
      </button>
    </div>
  ),
}));
vi.mock('./ConvertProfileDrawer', () => ({
  ConvertProfileDrawer: ({ nationalSection, onApply, onReset }: any) => (
    <div data-testid="profile-drawer-mock">
      {nationalSection}
      <button type="button" onClick={onApply}>
        apply-profile
      </button>
      <button type="button" onClick={onReset}>
        reset-profile
      </button>
    </div>
  ),
}));

/**
 *
 */
function buildProps(overrides: Record<string, unknown> = {}) {
  return {
    liveLayout: undefined,
    showGuestLossNotice: false,
    showPrivacyNotice: false,
    setShowPrivacyNotice: vi.fn(),
    setIsPrivacySettingsOpen: vi.fn(),
    setIsSiteTermsOpen: vi.fn(),
    onLoadWorkSession: undefined,
    isDisseminationOpen: false,
    handleDisseminationOpenChange: vi.fn(),
    convertedContent: '',
    convertedFiles: [],
    conversionParams: initialConversionParams(),
    packagingExchangeProfile: null,
    setPackagingExchangeProfile: vi.fn(),
    setConversionParams: vi.fn(),
    isPreferencesDialogOpen: false,
    setIsPreferencesDialogOpen: vi.fn(),
    isPrivacySettingsOpen: false,
    isSiteTermsOpen: false,
    userEmail: 'op@example.test',
    accessToken: '',
    manualInput: '',
    helpChecklistOpen: false,
    setHelpChecklistOpen: vi.fn(),
    profileDrawerOpen: true,
    setProfileDrawerOpen: vi.fn(),
    isReadOnly: false,
    conversionStatus: { type: 'idle' },
    recentWorkCollapsed: false,
    resultsDrawerOpen: false,
    setResultsDrawerOpen: vi.fn(),
    resultsTab: 'iwxxm',
    setResultsTab: vi.fn(),
    updateLiveLayout: vi.fn(),
    handlePreferencesSaved: vi.fn(),
    ...overrides,
  };
}

/** Run the functional updater passed to a ``setConversionParams`` spy. */
function applyUpdater(spy: ReturnType<typeof vi.fn>, prev: unknown, call = 0) {
  const updater = spy.mock.calls[call]![0] as (p: unknown) => unknown;
  return updater(prev);
}

describe('FileConverterView', () => {
  const originalEnabled = operatorDisseminationUiConfig.destinationsEnabled;

  beforeEach(() => {
    operatorDisseminationUiConfig.destinationsEnabled = true;
  });

  afterEach(() => {
    operatorDisseminationUiConfig.destinationsEnabled = originalEnabled;
    cleanup();
  });

  it('updates the dissemination template only when it changes', () => {
    const props = buildProps();
    render(<FileConverterView {...(props as any)} />);
    fireEvent.click(screen.getByText('pick-template'));
    const prev = props.conversionParams;
    const next = applyUpdater(props.setConversionParams, prev) as any;
    expect(next.disseminationTemplateId).toBe('tpl-1');
    const same = { ...prev, disseminationTemplateId: 'tpl-1' };
    expect(applyUpdater(props.setConversionParams, same)).toBe(same);
  });

  it('forwards drawer close to handleDisseminationOpenChange', () => {
    const props = buildProps();
    render(<FileConverterView {...(props as any)} />);
    fireEvent.click(screen.getByText('close-drawer'));
    expect(props.handleDisseminationOpenChange).toHaveBeenCalledWith(false);
  });

  it('passes product and IWXXM source to the dissemination drawer', () => {
    const speci = buildProps({
      conversionParams: { ...initialConversionParams(), product: 'SPECI' },
      convertedContent: 'fallback-xml',
    });
    const { unmount } = render(<FileConverterView {...(speci as any)} />);
    const drawer = screen.getByTestId('dissemination-drawer-mock');
    expect(drawer).toHaveAttribute('data-product', 'speci');
    expect(drawer).toHaveAttribute('data-xml', 'fallback-xml');
    unmount();

    const metar = buildProps({ convertedFiles: [{ convertedContent: '<first/>' }] });
    render(<FileConverterView {...(metar as any)} />);
    const metarDrawer = screen.getByTestId('dissemination-drawer-mock');
    expect(metarDrawer).toHaveAttribute('data-product', 'metar');
    expect(metarDrawer).toHaveAttribute('data-xml', '<first/>');
  });

  it('hides the dissemination drawer when destinations are disabled (default)', () => {
    operatorDisseminationUiConfig.destinationsEnabled = false;
    render(<FileConverterView {...(buildProps() as any)} />);
    expect(screen.queryByTestId('dissemination-drawer-mock')).not.toBeInTheDocument();
  });

  it('applies the national profile radio selection', () => {
    const props = buildProps({
      conversionParams: { ...initialConversionParams(), profile: 'annex3' },
    });
    render(<FileConverterView {...(props as any)} />);
    const radio = screen.getByRole('radio');
    expect(radio).not.toBeChecked();
    fireEvent.click(radio);
    const next = applyUpdater(props.setConversionParams, props.conversionParams) as any;
    expect(next.profile).toBe('ICAO_2025');
    expect(next.reportVariant).toBe('');
    expect(next.conversionLibraryId).toBe(
      libraryResetForProfile('ICAO_2025').libraryIds.conversionLibraryId,
    );
  });

  it('resets the profile to ICAO_2025 from the profile drawer', () => {
    const props = buildProps({
      conversionParams: { ...initialConversionParams(), profile: 'annex3' },
    });
    render(<FileConverterView {...(props as any)} />);
    fireEvent.click(screen.getByText('apply-profile'));
    fireEvent.click(screen.getByText('reset-profile'));
    const next = applyUpdater(props.setConversionParams, props.conversionParams) as any;
    expect(next.profile).toBe('ICAO_2025');
    expect(next.reportVariant).toBe('');
  });
});
