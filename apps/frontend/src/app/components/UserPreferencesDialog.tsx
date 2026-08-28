/* eslint-disable react-refresh/only-export-components */
import { useState, useEffect, useCallback } from 'react';
import { Button } from './ui/button';
import { Label } from './ui/label';
import { Input } from './ui/input';
import { Card } from './ui/card';
import { Settings, Loader2, CheckCircle, AlertCircle, RotateCcw } from 'lucide-react';
import { toast } from 'sonner';

interface UserPreferencesDialogProps {
  isOpen: boolean;
  onClose: () => void;
  userEmail: string;
  onPreferencesSaved?: () => void;
}

/** Slim prefs (EV-040): display/output name + file extension only. */
interface UserPreferences {
  displayName: string;
  email: string;
  outputFileExtension: string;
}

const DEFAULT_PREFERENCES: UserPreferences = {
  displayName: '',
  email: '',
  outputFileExtension: '.xml',
};

const STORAGE_KEY = 'metar_converter_preferences';

const EXTENSION_OPTIONS = ['.xml', '.iwxxm', '.txt'] as const;

/** Local-part before @ (empty when missing) — exported for unit coverage. */
export function emailLocalPart(email: string): string {
  return email.split('@')[0] || '';
}

/** Loading spinner body — extracted for unit coverage without async paint races. */
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

/** Whether Reset / header actions should be disabled. */
export function prefsControlsDisabled(isLoading: boolean, isSaving: boolean): boolean {
  return isLoading || isSaving;
}

/** Saving button label — extracted for unit coverage. */
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
      };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
      setSaveStatus('success');
      toast.success('Preferences saved successfully');

      setTimeout(() => {
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
        className="bg-white dark:bg-gray-800 dark:border-gray-700 p-6 max-w-lg w-full max-h-[90vh] overflow-y-auto"
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
            className="dark:bg-gray-700 dark:text-white dark:hover:bg-gray-600"
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
              Adjust your display name and output file extension. Conversion options
              live on the workbench.
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
                className="mt-1 w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-700 dark:text-white"
              >
                {EXTENSION_OPTIONS.map((ext) => (
                  <option key={ext} value={ext}>
                    {ext}
                  </option>
                ))}
              </select>
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
