import { ThemeProvider as NextThemesProvider } from 'next-themes';
import { type ReactNode } from 'react';

/**
 * App-wide theme context provider (class-based light/dark).
 *
 * @param children - React tree to wrap.
 */
export function ThemeProvider({ children }: { children: ReactNode }) {
  return (
    <NextThemesProvider attribute="class" defaultTheme="light" enableSystem={false}>
      {children}
    </NextThemesProvider>
  );
}
