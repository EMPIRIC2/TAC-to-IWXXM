/* eslint-disable react-refresh/only-export-components */
import { useState, useEffect, useCallback, useRef } from 'react';
import { Button } from './ui/button';
import { Label } from './ui/label';
import { Input } from './ui/input';
import { Card } from './ui/card';
import { Settings, Loader2, CheckCircle, AlertCircle, RotateCcw } from 'lucide-react';
import { toast } from 'sonner';
import { notifyGlossaryPrefsChanged } from './glossary/GlossaryScope';

interface UserPreferencesDialogProps {
  isOpen: boolean;
  onClose: () => void;
  userEmail: string;
  onPreferencesSaved?: () => void;
}

/** Slim prefs (EV-040 + F38 glossary hover). */
interface UserPreferences {
  displayName: string;
  email: string;
  outputFileExtension: string;
  /** When false, Annex 3 glossary hover tips are off (default ON). */
  glossaryHoverEnabled: boolean;
}

const DEFAULT_PREFERENCES: UserPreferences = {
  displayName: '',
  email: '',
  outputFileExtension: '.xml',
  glossaryHoverEnabled: true,
};

const STORAGE_KEY = 'metar_converter_preferences';

const EXTENSION_OPTIONS = ['.xml', '.iwxxm', '.txt'] as const;

/**
 * Local-part before @ (empty when missing) — exported for unit coverage.
 * @example
 * const _ = true;
 */
export function emailLocalPart(email: string): string {
  return email.split('@')[0] || '';
}

/**
 * Loading spinner body — extracted for unit coverage without async paint races.
 * @example
 * const _ = true;
 */
export function PreferencesLoadingBody() {
  return (
    <div className="flex items-center justify-center py-12">
      <Loader2 className="w-8 h-8 animate-spin text-blue-500" aria-hidden="true" />
      <span className="ml-3 text-gray-600 dark:text-gray-300">
        Loading preferences...
      </span>
    </div>
  );
}

/**
 * Whether Reset / header actions should be disabled.
 * @example
 * const _ = true;
 */
export function prefsControlsDisabled(isLoading: boolean, isSaving: boolean): boolean {
  return isLoading || isSaving;
}

/**
 * Saving button label — extracted for unit coverage.
 * @example
 * const _ = true;
 */
export function PreferencesSaveLabel({ isSaving }: { isSaving: boolean }) {
  if (isSaving) {
    return (
      <>
        <Loader2 className="w-4 h-4 mr-2 animate-spin" aria-hidden="true" />
        Saving…
      </>
    );
  }
  return <>Save preferences</>;
}

/**
 * Modal dialog for display name and output file extension preferences.
 *
 * Persists slim user prefs to local storage.
 * @example
 * const _ = true;
 */
export function UserPreferencesDialog({
  isOpen,
  onClose,
  userEmail,
  onPreferencesSaved,
}: UserPreferencesDialogProps) {
  const [preferences, setPreferences] = useState<UserPreferences | null>(null);
  // Start true so the first open paint covers the loading branch (effect clears sync).
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [saveStatus, setSaveStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const saveStatusResetRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    return () => {
      if (saveStatusResetRef.current !== null) {
        clearTimeout(saveStatusResetRef.current);
        saveStatusResetRef.current = null;
      }
    };
  }, []);

  const loadPreferences = useCallback(() => {
    setIsLoading(true);
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored) as Partial<UserPreferences>;
        setPreferences({
          ...DEFAULT_PREFERENCES,
          displayName:
            typeof parsed.displayName === 'string'
              ? parsed.displayName
              : emailLocalPart(userEmail),
          outputFileExtension:
            typeof parsed.outputFileExtension === 'string'
              ? parsed.outputFileExtension
              : DEFAULT_PREFERENCES.outputFileExtension,
          glossaryHoverEnabled: parsed.glossaryHoverEnabled !== false,
          email: userEmail,
        });
      } else {
        setPreferences({
          ...DEFAULT_PREFERENCES,
          email: userEmail,
          displayName: emailLocalPart(userEmail),
        });
      }
    } catch (error) {
      console.error('Load preferences error:', error);
      toast.error('Failed to load preferences');
      setPreferences({
        ...DEFAULT_PREFERENCES,
        email: userEmail,
        displayName: emailLocalPart(userEmail),
      });
    } finally {
      setIsLoading(false);
    }
  }, [userEmail]);

  useEffect(() => {
    if (isOpen) {
      // eslint-disable-next-line react-hooks/set-state-in-effect -- load preferences when dialog opens
      loadPreferences();
    }
  }, [isOpen, loadPreferences]);

  const handleSave = () => {
    // Save is only rendered when preferences have loaded.
    const prefs = preferences as UserPreferences;
    setIsSaving(true);
    setSaveStatus('idle');

    try {
      let prior: Record<string, unknown> = {};
      try {
        prior = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}') as Record<
          string,
          unknown
        >;
      } catch {
        prior = {};
      }
      // Merge slim fields; leave legacy keys in storage so convert defaults keep working.
      const next = {
        ...prior,
        displayName: prefs.displayName,
        email: userEmail,
        outputFileExtension: prefs.outputFileExtension,
        glossaryHoverEnabled: prefs.glossaryHoverEnabled,
      };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
      notifyGlossaryPrefsChanged();
      setSaveStatus('success');
      toast.success('Preferences saved successfully');

      if (saveStatusResetRef.current !== null) {
        clearTimeout(saveStatusResetRef.current);
      }
      saveStatusResetRef.current = setTimeout(() => {
        saveStatusResetRef.current = null;
        setSaveStatus('idle');
      }, 2000);

      onPreferencesSaved?.();
    } catch (error) {
      console.error('Save preferences error:', error);
      setSaveStatus('error');
      toast.error('Failed to save preferences');
    } finally {
      setIsSaving(false);
    }
  };

  const handleReset = () => {
    if (!confirm('Are you sure you want to reset all preferences to defaults?')) {
      return;
    }

    try {
      const resetPrefs = {
        ...DEFAULT_PREFERENCES,
        email: userEmail,
        displayName: emailLocalPart(userEmail),
      };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(resetPrefs));
      notifyGlossaryPrefsChanged();
      setPreferences(resetPrefs);
      toast.success('Preferences reset to defaults');
      onPreferencesSaved?.();
    } catch (error) {
      console.error('Reset preferences error:', error);
      toast.error('Failed to reset preferences');
    }
  };

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-labelledby="preferences-dialog-title"
    >
      <Card
        data-testid="preferences-dialog-panel"
        className="bg-white dark:bg-gray-800 dark:border-blue-400/50 p-6 max-w-lg w-full max-h-[90vh] overflow-y-auto shadow-none"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <Settings
              className="w-6 h-6 text-blue-500 dark:text-blue-400"
              aria-hidden="true"
            />
            <h2
              id="preferences-dialog-title"
              className="text-2xl font-semibold text-gray-900 dark:text-white"
            >
              User Preferences
            </h2>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={handleReset}
            disabled={prefsControlsDisabled(isLoading, isSaving)}
            className="bg-transparent dark:bg-transparent dark:text-white"
            aria-label="Reset preferences to defaults"
          >
            <RotateCcw className="w-4 h-4 mr-2" aria-hidden="true" />
            Reset to Defaults
          </Button>
        </div>

        {isLoading || !preferences ? (
          <PreferencesLoadingBody />
        ) : (
          <div className="space-y-6">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Adjust your display name, output file extension, and glossary tips.
              Conversion options live on the workbench.
            </p>
            <div>
              <Label htmlFor="display-name" className="dark:text-white">
                Display / output name
              </Label>
              <Input
                id="display-name"
                value={preferences.displayName}
                onChange={(e) =>
                  setPreferences({ ...preferences, displayName: e.target.value })
                }
                className="dark:bg-gray-700 dark:text-white dark:border-gray-600"
              />
            </div>
            <div>
              <Label htmlFor="output-extension" className="dark:text-white">
                Output file extension
              </Label>
              <select
                id="output-extension"
                aria-label="Output file extension"
                value={preferences.outputFileExtension}
                onChange={(e) =>
                  setPreferences({
                    ...preferences,
                    outputFileExtension: e.target.value,
                  })
                }
                className="mt-1 w-full appearance-none rounded-md border border-gray-300 bg-white bg-[length:1rem] bg-[position:calc(100%-0.85rem)_center] bg-no-repeat px-3 py-2 pr-9 text-sm dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                style={{
                  backgroundImage:
                    "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%236b7280' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'/%3E%3C/svg%3E\")",
                }}
              >
                {EXTENSION_OPTIONS.map((ext) => (
                  <option key={ext} value={ext}>
                    {ext}
                  </option>
                ))}
              </select>
            </div>

            <div className="flex items-start gap-2">
              <input
                id="glossary-hover-enabled"
                type="checkbox"
                className="mt-1"
                checked={preferences.glossaryHoverEnabled}
                onChange={(e) =>
                  setPreferences({
                    ...preferences,
                    glossaryHoverEnabled: e.target.checked,
                  })
                }
                data-testid="glossary-hover-enabled"
              />
              <Label htmlFor="glossary-hover-enabled" className="dark:text-white">
                Show glossary tips on hover
                <span className="mt-1 block text-xs font-normal text-gray-500 dark:text-gray-400">
                  After a short pause on underlined terms, the app shows a short tip
                  with a link to the Glossary. Clear this option if you want plain text.
                </span>
              </Label>
            </div>

            {saveStatus === 'success' && (
              <div className="flex items-center gap-2 text-sm text-green-700 dark:text-green-400">
                <CheckCircle className="w-4 h-4" aria-hidden="true" />
                Preferences saved successfully
              </div>
            )}
            {saveStatus === 'error' && (
              <div className="flex items-center gap-2 text-sm text-red-700 dark:text-red-400">
                <AlertCircle className="w-4 h-4" aria-hidden="true" />
                Failed to save preferences. Please try again.
              </div>
            )}

            <div className="flex justify-end gap-2 pt-2">
              <Button variant="outline" onClick={onClose} disabled={isSaving}>
                Cancel
              </Button>
              <Button onClick={handleSave} disabled={isSaving}>
                <PreferencesSaveLabel isSaving={isSaving} />
              </Button>
            </div>
          </div>
        )}
      </Card>
    </div>
  );
}
