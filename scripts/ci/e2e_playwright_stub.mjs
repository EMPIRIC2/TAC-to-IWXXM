/**
 * Stand-in for `@playwright/test` while measuring Playwright source coverage.
 *
 * Module evaluation registers suites. Test callbacks are not executed, so this
 * does not need a browser. [Corpus: tests]
 */

function describe(name, fn) {
  if (typeof fn === 'function') {
    fn();
  }
}

describe.configure = () => {};

function test() {}

test.describe = describe;
test.skip = () => {};
test.only = test;
test.fixme = () => {};
test.beforeEach = () => {};
test.afterEach = () => {};
test.beforeAll = () => {};
test.afterAll = () => {};
test.use = () => {};
test.step = async (_title, fn) => {
  if (typeof fn === 'function') {
    return fn();
  }
  return undefined;
};
test.extend = () => test;
test.setTimeout = () => {};
test.info = () => ({ title: '' });

function chain() {
  return new Proxy(function callable() {}, {
    get(_target, property) {
      if (property === 'then') {
        return undefined;
      }
      return chain();
    },
    apply() {
      return chain();
    },
  });
}

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

export {
  APIRequestContext,
  Page,
  Request,
  defineConfig,
  devices,
  expect,
  test,
};
