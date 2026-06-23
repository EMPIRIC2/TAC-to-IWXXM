import { createRoot } from 'react-dom/client';

import { initRuntimeConfig } from './utils/runtime-config';
import './styles/index.css';

async function bootstrap() {
  await initRuntimeConfig();
  const { default: App } = await import('./app/App.tsx');
  createRoot(document.getElementById('root')!).render(<App />);
}

void bootstrap();
