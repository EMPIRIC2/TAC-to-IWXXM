/* eslint-disable @typescript-eslint/no-explicit-any */
/**
 * FileConverterView: profile radios and profile reset.
 * Children and dialogs are stubbed so only the view's own handlers run.
 * FR-052..056 / DI-008: dissemination drawer unmounted.
 */
import { afterEach, describe, expect, it, vi } from 'vitest';
import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { FileConverterView } from './FileConverterView';
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
  afterEach(() => {
    cleanup();
  });

  it('does not mount a dissemination drawer (DI-008)', () => {
    render(<FileConverterView {...(buildProps() as any)} />);
    expect(screen.queryByTestId('dissemination-drawer')).not.toBeInTheDocument();
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
    const props = buildProps();
    render(<FileConverterView {...(props as any)} />);
    fireEvent.click(screen.getByText('reset-profile'));
    const next = applyUpdater(props.setConversionParams, props.conversionParams) as any;
    expect(next.profile).toBe('ICAO_2025');
  });
});
