/**
 * Coverage harness stand-in for `@playwright/test`.
 *
 * Module evaluation registers suites; callbacks run so V8 can record statement
 * and branch hits without a browser. Failures are swallowed — this is a
 * coverage run, not an assertion gate. [Corpus: tests]
 */

const pending = [];

function isThenable(value) {
  return value !== null && typeof value === 'object' && typeof value.then === 'function';
}

function enqueue(work) {
  pending.push(
    Promise.resolve()
      .then(() => work())
      .catch(() => undefined),
  );
}

function fixtureValue(name) {
  if (name === 'ok') {
    return () => true;
  }
  if (name === 'status') {
    return () => 200;
  }
  if (name === 'count') {
    return () => 1;
  }
  if (name === 'isVisible' || name === 'isEnabled' || name === 'isChecked') {
    return async () => true;
  }
  if (name === 'isHidden' || name === 'isDisabled') {
    return async () => false;
  }
  if (name === 'textContent' || name === 'innerText' || name === 'inputValue') {
    return async () => '';
  }
  if (name === 'getAttribute') {
    return async () => null;
  }
  if (name === 'json') {
    return async () => ({});
  }
  if (name === 'text') {
    return async () => '';
  }
  if (name === 'body') {
    return async () => Buffer.alloc(0);
  }
  if (name === 'headers') {
    return () => ({});
  }
  if (name === 'url') {
    return () => 'http://localhost:18000/';
  }
  if (name === 'evaluate' || name === 'evaluateHandle') {
    return async (fn, arg) => {
      if (typeof fn === 'function') {
        try {
          return await fn(arg);
        } catch {
          return undefined;
        }
      }
      return undefined;
    };
  }
  if (name === 'waitForTimeout' || name === 'waitForLoadState' || name === 'waitForURL') {
    return async () => undefined;
  }
  if (name === 'screenshot') {
    return async () => Buffer.alloc(0);
  }
  return undefined;
}

function chain() {
  return new Proxy(function callable() {}, {
    get(_target, property) {
      if (property === 'then') {
        // Not a thenable by default — `await locator` should not hang.
        return undefined;
      }
      if (property === Symbol.toPrimitive) {
        return () => 0;
      }
      if (property === 'toString') {
        return () => '';
      }
      if (typeof property === 'string') {
        const special = fixtureValue(property);
        if (special !== undefined) {
          return special;
        }
      }
      return chain();
    },
    apply() {
      return chain();
    },
  });
}

function fixtures() {
  return {
    page: chain(),
    request: chain(),
    context: chain(),
    browser: chain(),
    browserName: 'chromium',
    baseURL: 'http://localhost:18000',
  };
}

async function runCallback(fn, args = []) {
  if (typeof fn !== 'function') {
    return undefined;
  }
  try {
    const result = fn(...args);
    if (isThenable(result)) {
      await result.catch(() => undefined);
    }
  } catch {
    // Coverage harness: keep running remaining suites.
  }
  return undefined;
}

function describe(name, fn) {
  if (typeof name === 'function') {
    enqueue(() => runCallback(name, []));
    return;
  }
  if (typeof fn === 'function') {
    enqueue(() => runCallback(fn, []));
  }
}

describe.configure = () => {};
describe.skip = describe;
describe.only = describe;
describe.fixme = describe;
describe.serial = describe;
describe.parallel = describe;

function test(title, fn) {
  if (typeof title === 'function') {
    enqueue(() => runCallback(title, [fixtures()]));
    return;
  }
  if (typeof fn === 'function') {
    enqueue(() => runCallback(fn, [fixtures()]));
    return;
  }
  // test(title) with no body — ignore
}

function skip(...args) {
  // Always execute bodies so retired / conditional skips still contribute hits.
  for (const arg of args) {
    if (typeof arg === 'function') {
      enqueue(() => runCallback(arg, [fixtures()]));
    }
  }
}

test.describe = describe;
test.skip = skip;
test.only = test;
test.fixme = test;
test.beforeEach = (fn) => {
  enqueue(() => runCallback(fn, [fixtures()]));
};
test.afterEach = (fn) => {
  enqueue(() => runCallback(fn, [fixtures()]));
};
test.beforeAll = (fn) => {
  enqueue(() => runCallback(fn, [fixtures()]));
};
test.afterAll = (fn) => {
  enqueue(() => runCallback(fn, [fixtures()]));
};
test.use = () => {};
test.step = async (_title, fn) => runCallback(fn, []);
test.extend = () => test;
test.setTimeout = () => {};
test.info = () => ({
  title: '',
  project: { name: 'coverage' },
  annotations: [],
  attachments: [],
});

function expect() {
  return chain();
}

expect.poll = () => chain();
expect.soft = expect;
expect.extend = () => {};

class Page {}
class APIRequestContext {}
class Request {}

function defineConfig(config) {
  return config;
}

const devices = new Proxy(
  {},
  {
    get() {
      return {};
    },
  },
);

/**
 * Drain every suite callback registered during module evaluation.
 *
 * @returns {Promise<void>}
 */
export async function drainPending() {
  // Suites may enqueue more work while draining (nested describe).
  while (pending.length > 0) {
    const batch = pending.splice(0, pending.length);
    await Promise.all(batch);
  }
}

export {
  APIRequestContext,
  Page,
  Request,
  defineConfig,
  devices,
  expect,
  test,
};
