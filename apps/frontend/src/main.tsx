import { createRoot } from 'react-dom/client';

import { initRuntimeConfig } from './utils/runtime-config';
import { initSentry } from './utils/sentry';
import './styles/index.css';

/**
 * Function `bootstrap`.
 */
async function bootstrap() {
  await initRuntimeConfig();
  initSentry();
  const { default: App } = await import('./app/App.tsx');
  const { AppErrorBoundary } = await import('./app/components/AppErrorBoundary.tsx');
  createRoot(document.getElementById('root')!).render(
    <AppErrorBoundary>
      <App />
    </AppErrorBoundary>,
  );
}

void bootstrap();
