import { useState, useEffect, useCallback } from 'react';
import { Button } from './ui/button';
import { Label } from './ui/label';
import { Input } from './ui/input';
import { Card } from './ui/card';
import { Settings, Loader2, CheckCircle, AlertCircle, RotateCcw } from 'lucide-react';
import { toast } from 'sonner';
import { IcaoAutocomplete } from './IcaoAutocomplete';

interface UserPreferencesDialogProps {
  isOpen: boolean;
  onClose: () => void;
  userEmail: string;
  onPreferencesSaved?: () => void;
}

type IWXXMVersion = "2025-2" | "2023-1";
type OnErrorBehavior = "skip" | "fail" | "warn";
type LogLevel = "DEBUG" | "INFO" | "WARNING" | "ERROR" | "CRITICAL";

interface UserPreferences {
  // Account Settings
  displayName: string;
  email: string;
  
  // File Settings
  inputFileExtensions: string[];
  inputFileEncoding: string;
  inputFileMaxSize: string;
  outputFileExtension: string;
  outputFileEncoding: string;
  
  // Bulletin Settings
  bulletinIdExample: string;
  issuingCenter: string;
  
  // IWXXM Settings
  iwxxmVersion: IWXXMVersion;
  strictValidation: boolean;
  includeNilReasons: boolean;
  
  // Error Handling
  onError: OnErrorBehavior;
  logLevel: LogLevel;
  
  // METAR Format Settings
  metarMaxLength: number;
  metarEncoding: string;
}

const DEFAULT_PREFERENCES: UserPreferences = {
  // Account Settings
  displayName: '',
  email: '',
  
  // File Settings
  inputFileExtensions: ['.txt', '.tac', '.metar'],
  inputFileEncoding: 'UTF-8',
  inputFileMaxSize: '10MB',
  outputFileExtension: '.xml',
  outputFileEncoding: 'UTF-8',
  
  // Bulletin Settings
  bulletinIdExample: 'SAAA00',
  issuingCenter: 'KWBC',
  
  // IWXXM Settings
  iwxxmVersion: '2025-2',
  strictValidation: true,
  includeNilReasons: true,
  
  // Error Handling
  onError: 'warn',
  logLevel: 'INFO',
  
  // METAR Format Settings
  metarMaxLength: 1000,
  metarEncoding: 'ASCII/UTF-8',
};

const STORAGE_KEY = 'metar_converter_preferences';

export function UserPreferencesDialog({ isOpen, onClose, userEmail, onPreferencesSaved }: UserPreferencesDialogProps) {
  const [preferences, setPreferences] = useState<UserPreferences | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [saveStatus, setSaveStatus] = useState<'idle' | 'success' | 'error'>('idle');

  const loadPreferences = useCallback(() => {
    setIsLoading(true);
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        setPreferences({
          ...DEFAULT_PREFERENCES,
          ...parsed,
          email: userEmail, // Always use current email
        });
      } else {
        // First time - use defaults
        setPreferences({
          ...DEFAULT_PREFERENCES,
          email: userEmail,
          displayName: userEmail.split('@')[0], // Use email prefix as default name
        });
      }
    } catch (error) {
      console.error('Load preferences error:', error);
      toast.error('Failed to load preferences');
      setPreferences({
        ...DEFAULT_PREFERENCES,
        email: userEmail,
      });
    } finally {
      setIsLoading(false);
    }
  }, [userEmail]);

  useEffect(() => {
    if (isOpen) {
      loadPreferences();
    }
  }, [isOpen, loadPreferences]);

  const handleSave = () => {
    if (!preferences) return;

    setIsSaving(true);
    setSaveStatus('idle');

    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(preferences));
      setSaveStatus('success');
      toast.success('Preferences saved successfully');
      
      setTimeout(() => {
        setSaveStatus('idle');
      }, 2000);

      if (onPreferencesSaved) {
        onPreferencesSaved();
      }
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
        displayName: userEmail.split('@')[0],
      };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(resetPrefs));
      setPreferences(resetPrefs);
      toast.success('Preferences reset to defaults');
      
      if (onPreferencesSaved) {
        onPreferencesSaved();
      }
    } catch (error) {
      console.error('Reset preferences error:', error);
      toast.error('Failed to reset preferences');
    }
  };

  const updatePreference = <K extends keyof UserPreferences>(
    key: K,
    value: UserPreferences[K]
  ) => {
    if (!preferences) return;
    setPreferences({
      ...preferences,
      [key]: value,
    });
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
        className="bg-white dark:bg-gray-800 dark:border-gray-700 p-6 max-w-4xl w-full max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <Settings className="w-6 h-6 text-blue-500 dark:text-blue-400" aria-hidden="true" />
            <h2 id="preferences-dialog-title" className="text-2xl font-semibold text-gray-900 dark:text-white">
              User Preferences
            </h2>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={handleReset}
            disabled={isLoading || isSaving}
            className="dark:bg-gray-700 dark:text-white dark:hover:bg-gray-600"
            aria-label="Reset preferences to defaults"
          >
            <RotateCcw className="w-4 h-4 mr-2" aria-hidden="true" />
            Reset to Defaults
          </Button>
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-blue-500" aria-hidden="true" />
            <span className="ml-3 text-gray-600 dark:text-gray-300">Loading preferences...</span>
          </div>
        ) : preferences ? (
          <div className="space-y-6">
            {/* Account Settings */}
            <div>
              <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Account Settings</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="display-name" className="dark:text-white">Display Name</Label>
                  <Input
                    id="display-name"
                    value={preferences.displayName}
                    onChange={(e) => updatePreference('displayName', e.target.value)}
                    className="dark:bg-gray-700 dark:text-white dark:border-gray-600"
                  />
                </div>
                <div>
                  <Label htmlFor="email" className="dark:text-white">Email</Label>
                  <Input
                    id="email"
                    value={preferences.email}
                    onChange={(e) => updatePreference('email', e.target.value)}
                    className="dark:bg-gray-700 dark:text-white dark:border-gray-600"
                    disabled
                  />
                </div>
              </div>
            </div>

            {/* File Settings */}
            <div>
              <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">File Settings</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="input-encoding" className="dark:text-white">Input File Encoding</Label>
                  <select
                    id="input-encoding"
                    value={preferences.inputFileEncoding}
                    onChange={(e) => updatePreference('inputFileEncoding', e.target.value)}
                    className="w-full h-10 px-3 rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="UTF-8">UTF-8</option>
                    <option value="ASCII">ASCII</option>
                    <option value="ISO-8859-1">ISO-8859-1</option>
                    <option value="UTF-16">UTF-16</option>
                    <option value="Windows-1252">Windows-1252</option>
                  </select>
                </div>
                <div>
                  <Label htmlFor="input-max-size" className="dark:text-white">Max Input File Size</Label>
                  <select
                    id="input-max-size"
                    value={preferences.inputFileMaxSize}
                    onChange={(e) => updatePreference('inputFileMaxSize', e.target.value)}
                    className="w-full h-10 px-3 rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="1MB">1 MB</option>
                    <option value="5MB">5 MB</option>
                    <option value="10MB">10 MB</option>
                    <option value="25MB">25 MB</option>
                    <option value="50MB">50 MB</option>
                    <option value="100MB">100 MB</option>
                  </select>
                </div>
                <div>
                  <Label htmlFor="output-extension" className="dark:text-white">Output File Extension</Label>
                  <select
                    id="output-extension"
                    value={preferences.outputFileExtension}
                    onChange={(e) => updatePreference('outputFileExtension', e.target.value)}
                    className="w-full h-10 px-3 rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value=".xml">.xml</option>
                    <option value=".iwxxm">.iwxxm</option>
                    <option value=".txt">.txt</option>
                  </select>
                </div>
                <div>
                  <Label htmlFor="output-encoding" className="dark:text-white">Output File Encoding</Label>
                  <select
                    id="output-encoding"
                    value={preferences.outputFileEncoding}
                    onChange={(e) => updatePreference('outputFileEncoding', e.target.value)}
                    className="w-full h-10 px-3 rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="UTF-8">UTF-8</option>
                    <option value="ASCII">ASCII</option>
                    <option value="ISO-8859-1">ISO-8859-1</option>
                    <option value="UTF-16">UTF-16</option>
                    <option value="Windows-1252">Windows-1252</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Bulletin Settings */}
            <div>
              <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Bulletin Settings</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="bulletin-id" className="dark:text-white">Bulletin ID (e.g., SAAA00)</Label>
                  <Input
                    id="bulletin-id"
                    value={preferences.bulletinIdExample}
                    onChange={(e) => updatePreference('bulletinIdExample', e.target.value.toUpperCase())}
                    placeholder="SAAA00"
                    maxLength={6}
                    className="dark:bg-gray-700 dark:text-white dark:border-gray-600"
                  />
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    Format: 4 letters + 2 digits (e.g., SAAA00, SAUS70)
                  </p>
                </div>
                <div>
                  <IcaoAutocomplete
                    label="Issuing Center (ICAO Code)"
                    id="issuing-center"
                    value={preferences.issuingCenter}
                    onChange={(value) => updatePreference('issuingCenter', value)}
                    placeholder="KWBC"
                    maxLength={4}
                    helperText="4-letter ICAO location indicator (e.g., KWBC, LFPW)"
                  />
                </div>
              </div>
            </div>

            {/* IWXXM Settings */}
            <div>
              <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">IWXXM Settings</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="iwxxm-version" className="dark:text-white">IWXXM Schema Version</Label>
                  <select
                    id="iwxxm-version"
                    value={preferences.iwxxmVersion}
                    onChange={(e) => updatePreference('iwxxmVersion', e.target.value as IWXXMVersion)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="2025-2">2025-2 (Latest)</option>
                    <option value="2023-1">2023-1 (Previous)</option>
                  </select>
                </div>
                <div>
                  <Label className="dark:text-white">Validation Options</Label>
                  <div className="space-y-2 mt-2">
                    <label className="flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={preferences.strictValidation}
                        onChange={(e) => updatePreference('strictValidation', e.target.checked)}
                        className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                      />
                      <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
                        Strict Validation
                      </span>
                    </label>
                    <label className="flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={preferences.includeNilReasons}
                        onChange={(e) => updatePreference('includeNilReasons', e.target.checked)}
                        className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                      />
                      <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
                        Include Nil Reasons
                      </span>
                    </label>
                  </div>
                </div>
              </div>
            </div>

            {/* Error Handling */}
            <div>
              <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Error Handling</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="on-error" className="dark:text-white">On Error Behavior</Label>
                  <select
                    id="on-error"
                    value={preferences.onError}
                    onChange={(e) => updatePreference('onError', e.target.value as OnErrorBehavior)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="skip">Skip - Continue processing, skip invalid</option>
                    <option value="fail">Fail - Stop on first error</option>
                    <option value="warn">Warn - Continue with warnings</option>
                  </select>
                </div>
                <div>
                  <Label htmlFor="log-level" className="dark:text-white">Log Level</Label>
                  <select
                    id="log-level"
                    value={preferences.logLevel}
                    onChange={(e) => updatePreference('logLevel', e.target.value as LogLevel)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="DEBUG">DEBUG</option>
                    <option value="INFO">INFO</option>
                    <option value="WARNING">WARNING</option>
                    <option value="ERROR">ERROR</option>
                    <option value="CRITICAL">CRITICAL</option>
                  </select>
                </div>
              </div>
            </div>

            {/* METAR Format Settings */}
            <div>
              <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">METAR Format Settings</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="metar-max-length" className="dark:text-white">Max METAR Length (characters)</Label>
                  <Input
                    id="metar-max-length"
                    type="number"
                    value={preferences.metarMaxLength}
                    onChange={(e) => updatePreference('metarMaxLength', parseInt(e.target.value) || 1000)}
                    min={100}
                    max={5000}
                    className="dark:bg-gray-700 dark:text-white dark:border-gray-600"
                  />
                </div>
                <div>
                  <Label htmlFor="metar-encoding" className="dark:text-white">METAR Encoding</Label>
                  <Input
                    id="metar-encoding"
                    value={preferences.metarEncoding}
                    onChange={(e) => updatePreference('metarEncoding', e.target.value)}
                    className="dark:bg-gray-700 dark:text-white dark:border-gray-600"
                  />
                </div>
              </div>
            </div>

            {/* Status Messages */}
            {saveStatus === 'success' && (
              <div className="p-4 bg-green-50 dark:bg-green-950 border border-green-200 dark:border-green-800 rounded-lg flex items-center gap-3">
                <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400 flex-shrink-0" aria-hidden="true" />
                <p className="text-sm text-green-700 dark:text-green-300">
                  Preferences saved successfully!
                </p>
              </div>
            )}

            {saveStatus === 'error' && (
              <div className="p-4 bg-red-50 dark:bg-red-950 border border-red-200 dark:border-red-800 rounded-lg flex items-center gap-3">
                <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0" aria-hidden="true" />
                <p className="text-sm text-red-700 dark:text-red-300">
                  Failed to save preferences. Please try again.
                </p>
              </div>
            )}

            {/* Actions */}
            <div className="flex gap-3 justify-end pt-4 border-t dark:border-gray-700">
              <Button
                variant="outline"
                onClick={onClose}
                disabled={isSaving}
                className="dark:bg-gray-700 dark:text-white dark:hover:bg-gray-600"
              >
                Cancel
              </Button>
              <Button
                onClick={handleSave}
                disabled={isSaving}
                className="bg-blue-500 hover:bg-blue-600 dark:bg-blue-600 dark:hover:bg-blue-700 text-white"
              >
                {isSaving ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" aria-hidden="true" />
                    Saving...
                  </>
                ) : (
                  'Save Preferences'
                )}
              </Button>
            </div>
          </div>
        ) : null}
      </Card>
    </div>
  );
}