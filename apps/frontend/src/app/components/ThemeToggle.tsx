import { Moon, Sun } from "lucide-react";
import { useTheme } from "next-themes";

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();

  const isDark = theme === "dark";

  return (
    <button
      onClick={() => setTheme(isDark ? "light" : "dark")}
      className="relative inline-flex items-center h-7 w-14 rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900 bg-gray-300 dark:bg-gray-600"
      role="switch"
      aria-checked={isDark}
      aria-label={`Switch to ${isDark ? 'light' : 'dark'} mode`}
    >
      <span
        className={`${
          isDark ? 'translate-x-7' : 'translate-x-1'
        } inline-flex items-center justify-center h-6 w-6 transform rounded-full bg-white dark:bg-gray-900 transition-transform shadow-lg`}
      >
        {isDark ? (
          <Moon className="h-3.5 w-3.5 text-blue-500" aria-hidden="true" />
        ) : (
          <Sun className="h-3.5 w-3.5 text-yellow-500" aria-hidden="true" />
        )}
      </span>
    </button>
  );
}
