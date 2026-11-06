import { describe, expect, it } from 'vitest';
import { catalogLevelLabel, diffChangeLabel } from './readableStatus';

describe('readableStatus', () => {
  it('names diff operations', () => {
    expect(diffChangeLabel('add')).toBe('Added');
    expect(diffChangeLabel('remove')).toBe('Removed');
    expect(diffChangeLabel('empty')).toBe('');
    expect(diffChangeLabel('equal')).toBe('Same');
  });

  it('writes catalog levels', () => {
    expect(catalogLevelLabel(null)).toBe('—');
    expect(catalogLevelLabel('  ')).toBe('—');
    expect(catalogLevelLabel('error')).toBe('Error');
    expect(catalogLevelLabel('warning')).toBe('Warning');
    expect(catalogLevelLabel('warn')).toBe('Warning');
    expect(catalogLevelLabel('info')).toBe('Info');
    expect(catalogLevelLabel('critical')).toBe('Critical');
    expect(catalogLevelLabel('notice')).toBe('Notice');
  });
});
