/**
 * Small DOM helpers for hidden file inputs (mass ingest / directory pickers).
 */

/** Mark a file input as a directory picker when the host exists. */
export function applyWebkitDirectoryAttrs(el: HTMLInputElement | null): void {
  if (!el) {
    return;
  }
  el.setAttribute('webkitdirectory', '');
  el.setAttribute('directory', '');
}

/** Clear a file input value when the host exists. */
export function clearFileInputValue(el: HTMLInputElement | null): void {
  if (el) {
    el.value = '';
  }
}

/** Iterate a FileList, skipping sparse/undefined slots. */
export function forEachFileInList(
  files: FileList,
  visit: (file: File, index: number) => void | Promise<void>,
): Array<void | Promise<void>> {
  const tasks: Array<void | Promise<void>> = [];
  for (let i = 0; i < files.length; i++) {
    const file = files[i];
    if (!file) continue;
    tasks.push(visit(file, i));
  }
  return tasks;
}

/** First file in a drop FileList, or null when the slot is empty. */
export function firstDropFile(files: FileList): File | null {
  return files[0] ?? null;
}

/** Prefer candidate product, else drawer/session product. */
export function resolveDisseminationProduct(
  candidateProduct: string | undefined,
  fallbackProduct: string,
): string {
  return candidateProduct ?? fallbackProduct;
}

/** CA ECCC extension bundle pin → boolean or null when absent. */
export function caExtensionBundleAvailableFromStatus(status: {
  profile_pins?: {
    ca_eccc?: { extension_bundle_available?: boolean | null };
  };
}): boolean | null {
  return status.profile_pins?.ca_eccc?.extension_bundle_available ?? null;
}

/** aria-invalid only when a field error string is present. */
export function ariaInvalidFromError(
  error: string | null | undefined,
): true | undefined {
  return error ? true : undefined;
}

/** Hydrated convert result display name. */
export function hydratedResultName(name: string | undefined, index: number): string {
  return name ?? `result-${index + 1}`;
}

/** Queue/file convert result original name with unknown fallback. */
export function queueResultOriginalName(
  pendingName: string | undefined,
  resultName: string | undefined,
): string {
  return pendingName ?? resultName ?? 'unknown';
}

/** Soft-preview XML content with empty fallback. */
export function coalescePreviewXml(content: string | undefined): string {
  return content ?? '';
}

/** Validate-only catch message. */
export function iwxxmValidationErrorMessage(error: unknown): string {
  return error instanceof Error ? error.message : 'IWXXM validation failed';
}

/** Focused lint failure issue count. */
export function lintIssueCount(issues: { length: number } | null | undefined): number {
  return issues?.length ?? 0;
}

/** ZIP stem TAC: prefer first accumulated, else first converted card. */
export function firstTacForArchive(
  firstAccumulated: string | null,
  firstConverted: string | undefined,
): string | undefined {
  return firstAccumulated ?? firstConverted;
}

/** Compact drop-zone activation keys. */
export function isDropZoneActivateKey(key: string): boolean {
  return key === 'Enter' || key === ' ';
}

/** Work-queue key handler should no-op when empty. */
export function shouldIgnoreWorkQueueKey(pendingCount: number): boolean {
  return pendingCount === 0;
}

/** Apply focused queue item content, or no-op when missing. */
export function applyFocusedQueueContent(
  item: { content: string } | undefined,
  setContent: (content: string) => void,
): void {
  if (!item) {
    return;
  }
  setContent(item.content);
}

/** Focused queue validate catch message. */
export function focusedValidateErrorMessage(error: unknown, fileName: string): string {
  return error instanceof Error ? error.message : `Validate failed for ${fileName}`;
}
