import { useState, useEffect, useCallback } from 'react';
import { Button } from '../ui/button';
import { Card } from '../ui/card';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Loader2, Save, RotateCcw } from 'lucide-react';
import { toast } from 'sonner';
import { IcaoAutocomplete } from '../IcaoAutocomplete';
import { projectId } from '/utils/supabase/info';

type IWXXMVersion = "2025-2" | "2023-1";
type OnErrorBehavior = "skip" | "fail" | "warn";
type LogLevel = "DEBUG" | "INFO" | "WARNING" | "ERROR" | "CRITICAL";

interface SystemSettings {
  defaultBulletinId: string;
  defaultIssuingCenter: string;
  defaultIwxxmVersion: IWXXMVersion;
  defaultStrictValidation: boolean;
  defaultIncludeNilReasons: boolean;
  defaultOnError: OnErrorBehavior;
  defaultLogLevel: LogLevel;
  allowedIcaoCodes: string[];
}

interface SystemSettingsPanelProps {
  accessToken: string;
}

export function SystemSettingsPanel({ accessToken }: SystemSettingsPanelProps) {
  const [settings, setSettings] = useState<SystemSettings>({
    defaultBulletinId: 'SAAA00',
    defaultIssuingCenter: 'KWBC',
    defaultIwxxmVersion: '2025-2',
    defaultStrictValidation: true,
    defaultIncludeNilReasons: true,
    defaultOnError: 'warn',
    defaultLogLevel: 'INFO',
    allowedIcaoCodes: [],
  });
  const [originalSettings, setOriginalSettings] = useState<SystemSettings | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [newIcaoCode, setNewIcaoCode] = useState('');

  const loadSettings = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await fetch(
        `https://${projectId}.supabase.co/functions/v1/make-server-2e3cda33/admin/settings`,
        {
          headers: {
            'Authorization': `Bearer ${accessToken}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error('Failed to load settings');
      }

      const data = await response.json();
      setSettings(data.settings);
      setOriginalSettings(data.settings);
    } catch (error) {
      console.error('Error loading settings:', error);
      toast.error('Failed to load system settings');
    } finally {
      setIsLoading(false);
    }
  }, [accessToken]);

  useEffect(() => {
    loadSettings();
  }, [loadSettings]);

  const handleSave = async () => {
    setIsSaving(true);
    try {
      const response = await fetch(
        `https://${projectId}.supabase.co/functions/v1/make-server-2e3cda33/admin/settings`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ settings }),
        }
      );

      if (!response.ok) {
        throw new Error('Failed to save settings');
      }

      setOriginalSettings(settings);
      toast.success('System settings saved successfully');
    } catch (error) {
      console.error('Error saving settings:', error);
      toast.error('Failed to save system settings');
    } finally {
      setIsSaving(false);
    }
  };

  const handleReset = () => {
    if (originalSettings) {
      setSettings(originalSettings);
      toast.info('Settings reset to last saved values');
    }
  };

  const addIcaoCode = () => {
    const code = newIcaoCode.trim().toUpperCase();
    if (code && code.length === 4 && !settings.allowedIcaoCodes.includes(code)) {
      setSettings(prev => ({
        ...prev,
        allowedIcaoCodes: [...prev.allowedIcaoCodes, code].sort(),
      }));
      setNewIcaoCode('');
      toast.success(`ICAO code ${code} added`);
    } else if (settings.allowedIcaoCodes.includes(code)) {
      toast.error('ICAO code already exists');
    } else {
      toast.error('Invalid ICAO code (must be 4 letters)');
    }
  };

  const removeIcaoCode = (code: string) => {
    setSettings(prev => ({
      ...prev,
      allowedIcaoCodes: prev.allowedIcaoCodes.filter(c => c !== code),
    }));
    toast.info(`ICAO code ${code} removed`);
  };

  const hasChanges = JSON.stringify(settings) !== JSON.stringify(originalSettings);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-semibold text-gray-900 dark:text-white">
          System Settings
        </h2>
        <div className="flex gap-2">
          {hasChanges && (
            <Button
              onClick={handleReset}
              variant="outline"
              className="dark:bg-gray-700 dark:text-white"
            >
              <RotateCcw className="w-4 h-4 mr-2" />
              Reset
            </Button>
          )}
          <Button
            onClick={handleSave}
            disabled={isSaving || !hasChanges}
            className="bg-blue-500 hover:bg-blue-600 text-white dark:bg-blue-600 dark:hover:bg-blue-700"
          >
            {isSaving ? (
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            ) : (
              <Save className="w-4 h-4 mr-2" />
            )}
            Save Settings
          </Button>
        </div>
      </div>

      <div className="space-y-6">
        {/* Default Conversion Parameters */}
        <Card className="p-6 dark:bg-gray-750 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Default Conversion Parameters
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="default-bulletin-id" className="dark:text-white">
                Default Bulletin ID
              </Label>
              <Input
                id="default-bulletin-id"
                value={settings.defaultBulletinId}
                onChange={(e) => setSettings(prev => ({ ...prev, defaultBulletinId: e.target.value.toUpperCase() }))}
                maxLength={6}
                className="dark:bg-gray-700 dark:text-white dark:border-gray-600"
              />
            </div>

            <IcaoAutocomplete
              label="Default Issuing Center"
              id="default-issuing-center"
              value={settings.defaultIssuingCenter}
              onChange={(value) => setSettings(prev => ({ ...prev, defaultIssuingCenter: value }))}
              maxLength={4}
              helperText="4-letter ICAO code"
            />

            <div>
              <Label htmlFor="default-iwxxm-version" className="dark:text-white">
                Default IWXXM Version
              </Label>
              <select
                id="default-iwxxm-version"
                value={settings.defaultIwxxmVersion}
                onChange={(e) => setSettings(prev => ({ ...prev, defaultIwxxmVersion: e.target.value as IWXXMVersion }))}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="2025-2">2025-2 (Latest)</option>
                <option value="2023-1">2023-1 (Previous)</option>
              </select>
            </div>

            <div>
              <Label htmlFor="default-on-error" className="dark:text-white">
                Default On Error Behavior
              </Label>
              <select
                id="default-on-error"
                value={settings.defaultOnError}
                onChange={(e) => setSettings(prev => ({ ...prev, defaultOnError: e.target.value as OnErrorBehavior }))}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="skip">Skip</option>
                <option value="fail">Fail</option>
                <option value="warn">Warn</option>
              </select>
            </div>

            <div>
              <Label htmlFor="default-log-level" className="dark:text-white">
                Default Log Level
              </Label>
              <select
                id="default-log-level"
                value={settings.defaultLogLevel}
                onChange={(e) => setSettings(prev => ({ ...prev, defaultLogLevel: e.target.value as LogLevel }))}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="DEBUG">DEBUG</option>
                <option value="INFO">INFO</option>
                <option value="WARNING">WARNING</option>
                <option value="ERROR">ERROR</option>
                <option value="CRITICAL">CRITICAL</option>
              </select>
            </div>

            <div className="flex flex-col gap-3">
              <Label className="dark:text-white">Default Validation Options</Label>
              <label className="flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.defaultStrictValidation}
                  onChange={(e) => setSettings(prev => ({ ...prev, defaultStrictValidation: e.target.checked }))}
                  className="w-4 h-4 text-blue-600 rounded"
                />
                <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
                  Strict Validation
                </span>
              </label>
              <label className="flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.defaultIncludeNilReasons}
                  onChange={(e) => setSettings(prev => ({ ...prev, defaultIncludeNilReasons: e.target.checked }))}
                  className="w-4 h-4 text-blue-600 rounded"
                />
                <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
                  Include Nil Reasons
                </span>
              </label>
            </div>
          </div>
        </Card>

        {/* Allowed ICAO Codes */}
        <Card className="p-6 dark:bg-gray-750 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Allowed ICAO Codes
          </h3>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
            Manage the list of ICAO codes that can be used across the system. Leave empty to allow all codes.
          </p>
          
          <div className="flex gap-2 mb-4">
            <Input
              value={newIcaoCode}
              onChange={(e) => setNewIcaoCode(e.target.value.toUpperCase())}
              placeholder="Enter ICAO code (e.g., KJFK)"
              maxLength={4}
              className="dark:bg-gray-700 dark:text-white dark:border-gray-600"
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault();
                  addIcaoCode();
                }
              }}
            />
            <Button onClick={addIcaoCode} className="bg-blue-500 hover:bg-blue-600 text-white">
              Add Code
            </Button>
          </div>

          {settings.allowedIcaoCodes.length === 0 ? (
            <p className="text-sm text-gray-500 dark:text-gray-400 italic">
              No restrictions - all ICAO codes allowed
            </p>
          ) : (
            <div className="flex flex-wrap gap-2">
              {settings.allowedIcaoCodes.map((code) => (
                <div
                  key={code}
                  className="flex items-center gap-2 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 px-3 py-1 rounded-full"
                >
                  <span className="font-mono font-semibold">{code}</span>
                  <button
                    onClick={() => removeIcaoCode(code)}
                    className="text-blue-600 dark:text-blue-300 hover:text-blue-800 dark:hover:text-blue-100"
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
