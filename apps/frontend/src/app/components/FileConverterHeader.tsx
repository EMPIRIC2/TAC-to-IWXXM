/** FileConverterHeader */
import type { FileConverterViewProps } from './FileConverterViewProps';
import * as S from './fileConverterViewScope';

/**
 * FileConverterHeader.
 * @example
 * const _ = true;
 */
export function FileConverterHeader(props: FileConverterViewProps) {
  const {
    liveLayout,
    inputMode,
    isGuest,
    isLogoutMenuOpen,
    onRequestLogin,
    setHelpChecklistOpen,
    setIsLogoutMenuOpen,
    setIsPreferencesDialogOpen,
    handleLogoutWithScope,
  } = props;
  return (
    <header
      className="sticky top-0 z-30 w-full border-b border-gray-300 bg-white py-3 shadow-sm dark:border-gray-600 dark:bg-gray-950"
      data-testid="workbench-top-bar"
    >
      <div
        className={`mx-auto flex w-full flex-wrap items-center justify-between gap-3 px-4 ${S.shellFrameClass(liveLayout.span)}`}
      >
        <h1 className="text-2xl font-semibold text-gray-900 dark:text-white sm:text-3xl">
          {inputMode === 'validate_iwxxm' ? S.VALIDATE_IWXXM_HEADING : S.PAGE_TITLE}
        </h1>
        <div
          className="flex flex-wrap items-center gap-2 sm:gap-3"
          data-testid="workbench-header-actions"
        >
          <S.Button
            type="button"
            variant="outline"
            size="sm"
            className="bg-transparent dark:bg-transparent dark:text-white focus-visible:ring-primary/40"
            aria-label="Open convert help checklist"
            data-testid="convert-help-open"
            onClick={() => setHelpChecklistOpen(true)}
          >
            <S.CircleHelp className="mr-0 h-4 w-4 sm:mr-2" aria-hidden="true" />
            <span className="hidden sm:inline">Help</span>
          </S.Button>
          <S.Button
            onClick={() => setIsPreferencesDialogOpen(true)}
            variant="outline"
            size="sm"
            className="bg-transparent dark:bg-transparent dark:text-white focus-visible:ring-primary/40"
            aria-label="Open user preferences"
          >
            <S.Settings className="mr-0 h-4 w-4 sm:mr-2" aria-hidden="true" />
            <span className="hidden sm:inline">Preferences</span>
          </S.Button>
          <div className="flex items-center gap-2">
            <span className="hidden text-sm text-gray-600 dark:text-gray-400 sm:inline">
              Theme
            </span>
            <S.ThemeToggle />
          </div>
          <div className="relative">
            <S.Button
              variant={isGuest ? 'default' : 'outline'}
              className={
                isGuest
                  ? undefined
                  : 'border-gray-300 text-gray-800 hover:bg-gray-100 dark:border-gray-600 dark:text-gray-100 dark:hover:bg-gray-700'
              }
              aria-label={isGuest ? 'Sign in to save work' : 'Logout options'}
              data-testid={isGuest ? 'sign-in-button' : 'logout-button'}
              onClick={() => {
                if (isGuest) {
                  onRequestLogin?.();
                  return;
                }
                setIsLogoutMenuOpen(!isLogoutMenuOpen);
              }}
            >
              <S.LogOut className="w-4 h-4 mr-2" aria-hidden="true" />
              {isGuest ? 'Sign in' : 'Logout'}
              {!isGuest && (
                <S.ChevronDown className="w-4 h-4 ml-1" aria-hidden="true" />
              )}
            </S.Button>

            {isLogoutMenuOpen && !isGuest && (
              <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-md shadow-lg z-10">
                <div className="p-3 space-y-2">
                  <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 px-2 py-1">
                    Sign out scope:
                  </p>
                  <button
                    type="button"
                    onClick={() => void handleLogoutWithScope('local')}
                    className="w-full text-left px-3 py-2 rounded-md text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                    aria-label="Sign out from this device only"
                  >
                    <div className="font-medium">This Device</div>
                    <div className="text-xs text-gray-500 dark:text-gray-400">
                      Only this session
                    </div>
                  </button>
                  <button
                    type="button"
                    onClick={() => void handleLogoutWithScope('global')}
                    className="w-full text-left px-3 py-2 rounded-md text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                    aria-label="Sign out from all devices"
                  >
                    <div className="font-medium">All Devices</div>
                    <div className="text-xs text-gray-500 dark:text-gray-400">
                      Every signed-in session
                    </div>
                  </button>
                  <button
                    type="button"
                    onClick={() => void handleLogoutWithScope('others')}
                    className="w-full text-left px-3 py-2 rounded-md text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                    aria-label="Sign out other devices"
                  >
                    <div className="font-medium">Other Devices</div>
                    <div className="text-xs text-gray-500 dark:text-gray-400">
                      Keep this device signed in
                    </div>
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
