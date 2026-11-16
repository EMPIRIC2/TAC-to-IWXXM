/* eslint-disable complexity, @typescript-eslint/no-explicit-any -- FileConverter split */
/** Presentational FileConverter view composed from extracted regions. */
import type { FileConverterViewProps } from './FileConverterViewProps';
import * as S from './fileConverterViewScope';
import { FileConverterHeader } from './FileConverterHeader';
import { FileConverterIntro } from './FileConverterIntro';
import { FileConverterGuestNotice } from './FileConverterGuestNotice';
import { FileConverterActionStrip } from './FileConverterActionStrip';
import { FileConverterDropZone } from './FileConverterDropZone';
import { FileConverterFilename } from './FileConverterFilename';
import { FileConverterBody } from './FileConverterBody';
import { FileConverterChromeToolbar } from './FileConverterChromeToolbar';
import { FileConverterIwxxmPane } from './FileConverterIwxxmPane';
import { FileConverterDecodePane } from './FileConverterDecodePane';
import { FileConverterConsolePanel } from './FileConverterConsolePanel';
import { FileConverterDownloads } from './FileConverterDownloads';
import { FileConverterQueue } from './FileConverterQueue';
import { FileConverterRecentAside } from './FileConverterRecentAside';

export type { FileConverterViewProps } from './FileConverterViewProps';

/**
 * FileConverterView.
 * @example
 * const _ = true;
 */
export function FileConverterView(props: FileConverterViewProps) {
  const {
    liveLayout,
    showGuestLossNotice,
    showPrivacyNotice,
    setShowPrivacyNotice,
    setIsPrivacySettingsOpen,
    setIsSiteTermsOpen,
    onLoadWorkSession,
    isDisseminationOpen,
    handleDisseminationOpenChange,
    convertedContent,
    convertedFiles,
    conversionParams,
    packagingExchangeProfile,
    setPackagingExchangeProfile,
    setConversionParams,
    isPreferencesDialogOpen,
    setIsPreferencesDialogOpen,
    isPrivacySettingsOpen,
    isSiteTermsOpen,
    userEmail,
    accessToken,
    manualInput,
    helpChecklistOpen,
    setHelpChecklistOpen,
    profileDrawerOpen,
    setProfileDrawerOpen,
  } = props;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors">
      <FileConverterHeader {...props} />
      <div
        data-testid="workbench-frame"
        className={`mx-auto w-full px-4 py-4 pb-28 ${S.shellFrameClass(liveLayout?.span ?? 'tight')}`}
      >
        <div className="mb-4">
          <FileConverterIntro {...props} />
          {showGuestLossNotice ? <FileConverterGuestNotice {...props} /> : null}
          <S.PrivacyNotice
            open={showPrivacyNotice}
            onDismiss={() => {
              S.acknowledgePrivacyNotice();
              setShowPrivacyNotice(false);
            }}
            onOpenSettings={() => {
              S.acknowledgePrivacyNotice();
              setShowPrivacyNotice(false);
              setIsPrivacySettingsOpen(true);
            }}
          />
        </div>
        <FileConverterActionStrip {...props} />
        <div
          className={
            onLoadWorkSession
              ? props.recentWorkCollapsed
                ? 'grid grid-cols-[minmax(0,1fr)_3rem] gap-6'
                : 'grid grid-cols-[minmax(0,1fr)_280px] gap-6'
              : 'grid grid-cols-1 gap-6'
          }
          data-testid="workbench-layout-grid"
          data-recent-work={
            onLoadWorkSession
              ? props.recentWorkCollapsed
                ? 'collapsed'
                : 'expanded'
              : 'absent'
          }
        >
          <div className="min-w-0 space-y-4" data-testid="workbench-main-column">
            {props.isReadOnly ? (
              <S.StatusBanner tone="caution" className="mb-2">
                This session is finished and read-only. Use <strong>New TAC</strong> to
                start fresh.
              </S.StatusBanner>
            ) : null}
            <FileConverterDropZone {...props} />
            <div data-testid="live-convert-stage" className="flex flex-col gap-1">
              <div
                className="rounded-lg border border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-900"
                data-testid="convert-shell"
              >
                <FileConverterChromeToolbar {...props} />
                <FileConverterFilename {...props} />
                <FileConverterBody {...props} />
              </div>
            </div>
            <S.ConvertResultsDrawer
              open={props.resultsDrawerOpen}
              onOpenChange={props.setResultsDrawerOpen}
              tab={props.resultsTab}
              onTabChange={props.setResultsTab}
              height={liveLayout?.resultsDrawerHeight}
              onHeightChange={(next: number) =>
                props.updateLiveLayout({ resultsDrawerHeight: next })
              }
              iwxxm={<FileConverterIwxxmPane {...props} />}
              console={<FileConverterConsolePanel {...props} />}
              decoder={<FileConverterDecodePane {...props} />}
              downloads={<FileConverterDownloads {...props} />}
            />
            {props.conversionStatus?.type !== 'idle' ? (
              <div
                className={`mb-8 p-4 rounded-lg border-2 flex items-start gap-3 ${
                  props.conversionStatus.type === 'loading'
                    ? 'bg-blue-50 dark:bg-blue-900/20 border-blue-300 dark:border-blue-700'
                    : props.conversionStatus.type === 'timeout'
                      ? 'bg-red-50 dark:bg-red-900/20 border-red-300 dark:border-red-700'
                      : 'bg-red-50 dark:bg-red-900/20 border-red-300 dark:border-red-700'
                }`}
              >
                <div className="pt-1">
                  {props.conversionStatus.type === 'loading' ? (
                    <S.Loader2
                      className="w-5 h-5 text-blue-600 dark:text-blue-400 animate-spin flex-shrink-0"
                      aria-hidden="true"
                    />
                  ) : props.conversionStatus.type === 'timeout' ? (
                    <S.AlertCircle
                      className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0"
                      aria-hidden="true"
                    />
                  ) : (
                    <S.XCircle
                      className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0"
                      aria-hidden="true"
                    />
                  )}
                </div>
                <div className="flex-1">
                  <p
                    className={`font-semibold ${
                      props.conversionStatus.type === 'loading'
                        ? 'text-blue-900 dark:text-blue-100'
                        : 'text-red-900 dark:text-red-100'
                    }`}
                  >
                    {props.conversionStatus.type === 'loading'
                      ? 'Converting...'
                      : props.conversionStatus.type === 'timeout'
                        ? 'Conversion Timeout'
                        : props.conversionStatus.type === 'send_error'
                          ? 'Send Error'
                          : 'Conversion Error'}
                  </p>
                  {props.conversionStatus.message ? (
                    <p
                      className={`text-sm mt-1 ${
                        props.conversionStatus.type === 'loading'
                          ? 'text-blue-800 dark:text-blue-200'
                          : 'text-red-800 dark:text-red-200'
                      }`}
                    >
                      {props.conversionStatus.message}
                    </p>
                  ) : null}
                </div>
              </div>
            ) : null}
            <FileConverterQueue {...props} />
          </div>
          {onLoadWorkSession ? <FileConverterRecentAside {...props} /> : null}
        </div>
        <S.OperatorFooter
          onOpenPrivacy={() => setIsPrivacySettingsOpen(true)}
          onOpenTerms={() => setIsSiteTermsOpen(true)}
        />
      </div>
      {S.isOperatorDisseminationDestinationsEnabled() ? (
        <S.DisseminationDrawer
          key={
            isDisseminationOpen ? `open-${conversionParams.exchangeProfile}` : 'closed'
          }
          open={isDisseminationOpen}
          onOpenChange={handleDisseminationOpenChange}
          iwxxmXml={convertedFiles?.[0]?.convertedContent ?? convertedContent}
          tacText={manualInput || undefined}
          product={conversionParams.product === 'SPECI' ? 'speci' : 'metar'}
          accessToken={accessToken}
          disseminationTemplateId={conversionParams.disseminationTemplateId}
          onDisseminationTemplateChange={(templateId) =>
            setConversionParams((prev: any) =>
              prev.disseminationTemplateId === templateId
                ? prev
                : { ...prev, disseminationTemplateId: templateId },
            )
          }
          exchangeProfile={packagingExchangeProfile ?? conversionParams.exchangeProfile}
          onExchangeProfileChange={setPackagingExchangeProfile}
        />
      ) : null}
      <S.UserPreferencesDialog
        isOpen={isPreferencesDialogOpen}
        onClose={() => setIsPreferencesDialogOpen(false)}
        userEmail={userEmail}
        onPreferencesSaved={props.handlePreferencesSaved}
      />
      <S.ConvertHelpChecklist
        open={helpChecklistOpen}
        onOpenChange={setHelpChecklistOpen}
      />
      <S.ConvertProfileDrawer
        open={profileDrawerOpen}
        onOpenChange={setProfileDrawerOpen}
        nationalSection={
          <div className="space-y-2">
            {S.SEMANTIC_PROFILE_OPTIONS.filter((option: { value: string }) =>
              (S.COUNTRY_PRESET_LINES as readonly string[]).includes(option.value),
            ).map((option: { value: string; label: string }) => (
              <label
                key={option.value}
                className="flex cursor-pointer items-center gap-2 text-sm text-gray-800 dark:text-gray-200"
              >
                <input
                  type="radio"
                  name="calm-national-profile"
                  checked={conversionParams.profile === option.value}
                  onChange={() => {
                    const { profile, libraryIds } = S.libraryResetForProfile(
                      option.value,
                    );
                    setConversionParams((prev: Record<string, unknown>) => ({
                      ...prev,
                      ...libraryIds,
                      profile,
                      reportVariant: '',
                      iwxxmVersion: S.coerceIwxxmVersionForProfile(
                        profile,
                        prev.iwxxmVersion as string,
                      ),
                    }));
                  }}
                />
                {option.label}
              </label>
            ))}
          </div>
        }
        customizeSection={
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Only needed when one step must follow a different rule set. Open{' '}
            <span className="font-medium text-gray-800 dark:text-gray-200">
              Settings
            </span>{' '}
            and expand Customize each step to override Decoding, TAC checks, IWXXM
            mapping, or IWXXM checks.
          </p>
        }
        outputSection={
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Bulletin ID, issuing centre, file name, conversion metadata, soft preview,
            and leftover TAC in remarks.
          </p>
        }
        onApply={() => {
          /* profile radios already update state live */
        }}
        onReset={() => {
          const { profile, libraryIds } = S.libraryResetForProfile('ICAO_2025');
          setConversionParams((prev: Record<string, unknown>) => ({
            ...prev,
            ...libraryIds,
            profile,
            reportVariant: '',
            iwxxmVersion: S.coerceIwxxmVersionForProfile(
              profile,
              prev.iwxxmVersion as string,
            ),
          }));
        }}
      />
      <S.PrivacySettingsDialog
        isOpen={isPrivacySettingsOpen}
        onClose={() => setIsPrivacySettingsOpen(false)}
      />
      <S.SiteTermsDialog
        isOpen={isSiteTermsOpen}
        onClose={() => setIsSiteTermsOpen(false)}
      />
    </div>
  );
}
