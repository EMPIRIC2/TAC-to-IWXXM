/**
 * Redirect `@playwright/test` to the local coverage stub. [Corpus: tests]
 */
import { register } from 'node:module';

register(new URL('./e2e_playwright_hooks.mjs', import.meta.url), import.meta.url);
