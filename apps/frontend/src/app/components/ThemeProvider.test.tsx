/* eslint-disable @typescript-eslint/no-unused-vars */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render } from '@testing-library/react'
import { ThemeProvider } from './ThemeProvider'

describe('ThemeProvider Component', () => {
  it('should render with children', () => {
    const { container } = render(
      <ThemeProvider>
        <div>Test Child</div>
      </ThemeProvider>
    )
    
    expect(container.querySelector('div')).toBeTruthy()
  })

  it('should apply theme context', () => {
    const { container } = render(
      <ThemeProvider>
        <div className="test-element">Content</div>
      </ThemeProvider>
    )
    
    expect(container.querySelector('.test-element')).toBeTruthy()
  })
})
