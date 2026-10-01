/* eslint-disable @typescript-eslint/no-explicit-any, @typescript-eslint/no-unused-vars */
import 'fake-indexeddb/auto';
import '@testing-library/jest-dom';
import { expect, afterEach, vi } from 'vitest';
import { cleanup } from '@testing-library/react';

const liveAssistClock = globalThis as { __LIVE_ASSIST_FAST__?: boolean };
const useFakeTimers = vi.useFakeTimers.bind(vi);
const useRealTimers = vi.useRealTimers.bind(vi);

vi.useFakeTimers = ((...args: Parameters<typeof vi.useFakeTimers>) => {
  liveAssistClock.__LIVE_ASSIST_FAST__ = true;
  return useFakeTimers(...args);
}) as typeof vi.useFakeTimers;

vi.useRealTimers = ((...args: Parameters<typeof vi.useRealTimers>) => {
  liveAssistClock.__LIVE_ASSIST_FAST__ = false;
  return useRealTimers(...args);
}) as typeof vi.useRealTimers;

// Cleanup after each test
afterEach(() => {
  cleanup();
  liveAssistClock.__LIVE_ASSIST_FAST__ = false;
});

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => true,
  }),
});

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  takeRecords() {
    return [];
  }
  unobserve() {}
} as any;

// Mock ResizeObserver used by Radix and charting components
global.ResizeObserver = class ResizeObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
} as any;

// jsdom does not implement scroll APIs that some UI wrappers call.
Object.defineProperty(window, 'scrollTo', {
  writable: true,
  value: () => {},
});

// Radix Select expects pointer capture APIs that jsdom does not implement.
if (!HTMLElement.prototype.hasPointerCapture) {
  HTMLElement.prototype.hasPointerCapture = () => false;
}

if (!HTMLElement.prototype.setPointerCapture) {
  HTMLElement.prototype.setPointerCapture = () => {};
}

if (!HTMLElement.prototype.releasePointerCapture) {
  HTMLElement.prototype.releasePointerCapture = () => {};
}

if (!HTMLElement.prototype.scrollIntoView) {
  HTMLElement.prototype.scrollIntoView = () => {};
}
