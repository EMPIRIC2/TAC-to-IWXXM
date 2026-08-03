/**
 * Privacy settings preference center (F22 / UJ-033 / Solution A; F31 deepen).
 *
 * Discloses client storage in use; gates guest IndexedDB work history;
 * discloses Auth cookies; necessary categories always on; no CMP.
 */

import { useState } from 'react';
import { Button } from './ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from './ui/dialog';
import { clearLocalWorkSessions } from '@/utils/localWorkSessionStore';
import {
  STORAGE_INVENTORY,
  detectGlobalPrivacyControl,
  loadPrivacyPreferences,
  savePrivacyPreferences,
  type PrivacyPreferences,
  type StorageInventoryItem,
} from '@/utils/privacyPreferences';

export interface PrivacySettingsDialogProps {
  isOpen: boolean;
  onClose: () => void;
}

function inventoryTestId(item: StorageInventoryItem): string | undefined {
  if (item.kind === 'cookie' && /auth/i.test(item.purpose)) {
    return 'privacy-inventory-auth-cookie';
  }
  if (item.kind === 'indexedDB') {
    return 'privacy-inventory-work-history';
  }
  return undefined;
}

function PrivacySettingsForm({ onClose }: { onClose: () => void }) {
  const [prefs, setPrefs] = useState<PrivacyPreferences>(() =>
    loadPrivacyPreferences(),
  );
  const gpcEnabled = detectGlobalPrivacyControl();

  const handleSave = () => {
    const saved = savePrivacyPreferences({
      workHistoryLocal: prefs.workHistoryLocal,
      saleOrSharingOptOut: prefs.saleOrSharingOptOut,
      targetedAdvertisingOptOut: prefs.targetedAdvertisingOptOut,
      analytics: false,
      marketing: false,
    });
    setPrefs(saved);
    if (!saved.workHistoryLocal) {
      void clearLocalWorkSessions();
    }
    onClose();
  };

  return (
    <>
      <DialogHeader>
        <DialogTitle>Privacy settings</DialogTitle>
        <DialogDescription>
          Solution A — no non-essential analytics or marketing. Preferences stay in this
          browser only. Clearing site data resets them.
        </DialogDescription>
      </DialogHeader>

      {gpcEnabled ? (
        <p
          role="status"
          data-testid="privacy-gpc-active"
          className="rounded border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-900 dark:border-emerald-800 dark:bg-emerald-950 dark:text-emerald-100"
        >
          Global Privacy Control (GPC) detected — sale/sharing and targeted advertising
          opt-outs are enforced.
        </p>
      ) : null}

      <div className="space-y-4 text-sm text-gray-700 dark:text-gray-200">
        <section aria-labelledby="privacy-storage-heading">
          <h3
            id="privacy-storage-heading"
            className="mb-2 font-medium text-gray-900 dark:text-white"
          >
            Storage in use
          </h3>
          <ul className="space-y-2">
            {STORAGE_INVENTORY.map((item) => (
              <li
                key={`${item.kind}-${item.purpose}`}
                data-testid={inventoryTestId(item)}
                className="rounded border border-gray-200 p-3 dark:border-gray-700"
              >
                <div className="font-medium capitalize">{item.kind}</div>
                <p className="mt-1 text-gray-600 dark:text-gray-300">{item.purpose}</p>
                <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                  {item.necessary ? 'Necessary — always on' : 'Optional'}
                </p>
              </li>
            ))}
          </ul>
        </section>

        <section aria-labelledby="privacy-categories-heading">
          <h3
            id="privacy-categories-heading"
            className="mb-2 font-medium text-gray-900 dark:text-white"
          >
            Categories
          </h3>
          <label className="flex items-start gap-2 rounded border border-gray-200 p-3 dark:border-gray-700">
            <input
              type="checkbox"
              checked
              disabled
              aria-label="Necessary storage always enabled"
              className="mt-1"
            />
            <span>
              <span className="font-medium">Necessary</span>
              <span className="mt-1 block text-gray-600 dark:text-gray-300">
                Required for conversion and these privacy preferences.
              </span>
            </span>
          </label>

          <label className="mt-2 flex items-start gap-2 rounded border border-gray-200 p-3 dark:border-gray-700">
            <input
              type="checkbox"
              checked={prefs.workHistoryLocal}
              onChange={(event) =>
                setPrefs((current) => ({
                  ...current,
                  workHistoryLocal: event.target.checked,
                }))
              }
              aria-label="Store guest work history in this browser"
              data-testid="privacy-work-history-local"
              className="mt-1"
            />
            <span>
              <span className="font-medium">Guest work history (IndexedDB)</span>
              <span className="mt-1 block text-gray-600 dark:text-gray-300">
                When off, this browser will not save guest converter sessions. Sign in
                for long-term server storage. Turning off clears local work history.
              </span>
            </span>
          </label>

          <label className="mt-2 flex items-start gap-2 rounded border border-gray-200 p-3 dark:border-gray-700">
            <input
              type="checkbox"
              checked={prefs.saleOrSharingOptOut}
              onChange={(event) =>
                setPrefs((current) => ({
                  ...current,
                  saleOrSharingOptOut: event.target.checked,
                }))
              }
              aria-label="Opt out of sale or sharing of personal information"
              className="mt-1"
            />
            <span>
              <span className="font-medium">Do not sell or share</span>
              <span className="mt-1 block text-gray-600 dark:text-gray-300">
                This product does not sell personal information. The preference is still
                available and is forced on when Global Privacy Control (GPC) is
                detected.
              </span>
            </span>
          </label>

          <label className="mt-2 flex items-start gap-2 rounded border border-gray-200 p-3 dark:border-gray-700">
            <input
              type="checkbox"
              checked={prefs.targetedAdvertisingOptOut}
              onChange={(event) =>
                setPrefs((current) => ({
                  ...current,
                  targetedAdvertisingOptOut: event.target.checked,
                }))
              }
              aria-label="Opt out of targeted advertising"
              className="mt-1"
            />
            <span>
              <span className="font-medium">Limit targeted advertising</span>
              <span className="mt-1 block text-gray-600 dark:text-gray-300">
                No advertising scripts ship in v1. Forced on when GPC is detected.
              </span>
            </span>
          </label>
        </section>
      </div>

      <DialogFooter>
        <Button type="button" variant="outline" onClick={onClose}>
          Cancel
        </Button>
        <Button type="button" onClick={handleSave}>
          Save preferences
        </Button>
      </DialogFooter>
    </>
  );
}

export function PrivacySettingsDialog({ isOpen, onClose }: PrivacySettingsDialogProps) {
  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="sm:max-w-lg" data-testid="privacy-settings-dialog">
        {isOpen ? <PrivacySettingsForm onClose={onClose} /> : null}
      </DialogContent>
    </Dialog>
  );
}
