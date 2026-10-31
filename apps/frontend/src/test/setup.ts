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

/**
 * Node 25+ / Stryker workers can leave ``localStorage`` undefined even under
 * jsdom. Install an in-memory Storage that inherits ``Storage.prototype`` so
 * ``vi.spyOn(Storage.prototype, 'setItem')`` still intercepts writes.
 */
const memoryStorageBags = new WeakMap<object, Map<string, string>>();

function bagFor(storage: object): Map<string, string> {
  let bag = memoryStorageBags.get(storage);
  if (!bag) {
    bag = new Map<string, string>();
    memoryStorageBags.set(storage, bag);
  }
  return bag;
}

function installMemoryStoragePrototypeHooks(): void {
  if (typeof Storage === 'undefined') {
    return;
  }
  const proto = Storage.prototype as Storage & { __memoryHooks?: boolean };
  if (proto.__memoryHooks) {
    return;
  }
  proto.__memoryHooks = true;

  const originalClear = proto.clear;
  const originalGetItem = proto.getItem;
  const originalKey = proto.key;
  const originalRemoveItem = proto.removeItem;
  const originalSetItem = proto.setItem;

  proto.clear = function clear(this: object) {
    if (memoryStorageBags.has(this)) {
      bagFor(this).clear();
      return;
    }
    return originalClear.call(this as Storage);
  };

  proto.getItem = function getItem(this: object, key: string) {
    if (memoryStorageBags.has(this)) {
      const bag = bagFor(this);
      return bag.has(key) ? bag.get(key)! : null;
    }
    return originalGetItem.call(this as Storage, key);
  };

  proto.key = function key(this: object, index: number) {
    if (memoryStorageBags.has(this)) {
      return [...bagFor(this).keys()][index] ?? null;
    }
    return originalKey.call(this as Storage, index);
  };

  proto.removeItem = function removeItem(this: object, key: string) {
    if (memoryStorageBags.has(this)) {
      bagFor(this).delete(key);
      return;
    }
    return originalRemoveItem.call(this as Storage, key);
  };

  proto.setItem = function setItem(this: object, key: string, value: string) {
    if (memoryStorageBags.has(this)) {
      bagFor(this).set(String(key), String(value));
      return;
    }
    return originalSetItem.call(this as Storage, key, value);
  };
}

function ensureWebStorage(name: 'localStorage' | 'sessionStorage'): void {
  const g = globalThis as typeof globalThis & {
    localStorage?: Storage;
    sessionStorage?: Storage;
  };
  if (g[name] != null && typeof g[name]!.clear === 'function') {
    return;
  }
  installMemoryStoragePrototypeHooks();
  const storage =
    typeof Storage !== 'undefined'
      ? (Object.create(Storage.prototype) as Storage)
      : ({
          length: 0,
          clear() {},
          getItem() {
            return null;
          },
          key() {
            return null;
          },
          removeItem() {},
          setItem() {},
        } as Storage);
  if (typeof Storage !== 'undefined') {
    bagFor(storage);
  }
  Object.defineProperty(g, name, {
    configurable: true,
    writable: true,
    value: storage,
  });
  if (typeof window !== 'undefined') {
    Object.defineProperty(window, name, {
      configurable: true,
      writable: true,
      value: storage,
    });
  }
}

ensureWebStorage('localStorage');
ensureWebStorage('sessionStorage');

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
  /**
   *
   */
  disconnect() {}
  /**
   *
   */
  observe() {}
  /**
   *
   */
  takeRecords() {
    return [];
  }
  /**
   *
   */
  unobserve() {}
} as any;

// Mock ResizeObserver used by Radix and charting components
global.ResizeObserver = class ResizeObserver {
  constructor() {}
  /**
   *
   */
  disconnect() {}
  /**
   *
   */
  observe() {}
  /**
   *
   */
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
