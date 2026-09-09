/**
 * Workbench chrome viewport helpers (EV staging UX / F21).
 *
 * Narrow viewports default Recent work collapsed and Profile glance closed
 * so the convert surface stays usable without horizontal chrome fights.
 */

/** Tailwind ``sm`` breakpoint — match ``max-width: 767px``. */
export const WORKBENCH_NARROW_MQ = '(max-width: 767px)';

/**
 * Whether the workbench should prefer collapsed side chrome.
 *
 * @returns ``true`` when ``window`` matches the narrow media query
 */
export function preferCollapsedWorkbenchChrome(): boolean {
  if (typeof window === 'undefined' || typeof window.matchMedia !== 'function') {
    return false;
  }
  return window.matchMedia(WORKBENCH_NARROW_MQ).matches;
}

/**
 * Subscribe to narrow-viewport transitions.
 *
 * Only invokes ``onEnterNarrow`` when crossing from wide → narrow so a manual
 * expand is not snapped shut on every matching change event.
 *
 * @param onEnterNarrow - Collapse chrome when entering narrow
 * @returns Unsubscribe callback (no-op when ``matchMedia`` is unavailable)
 */
export function subscribeNarrowWorkbenchChrome(onEnterNarrow: () => void): () => void {
  if (typeof window === 'undefined' || typeof window.matchMedia !== 'function') {
    return () => undefined;
  }
  const mq = window.matchMedia(WORKBENCH_NARROW_MQ);
  let wasNarrow = mq.matches;
  const onChange = () => {
    const nowNarrow = mq.matches;
    if (nowNarrow && !wasNarrow) {
      onEnterNarrow();
    }
    wasNarrow = nowNarrow;
  };
  mq.addEventListener('change', onChange);
  return () => mq.removeEventListener('change', onChange);
}
