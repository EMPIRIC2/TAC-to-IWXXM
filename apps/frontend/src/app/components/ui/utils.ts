import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Merge Tailwind class names with conflict resolution via `tailwind-merge`.
 *
 * @param inputs - Class values accepted by `clsx`.
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
