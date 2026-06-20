/* eslint-disable @typescript-eslint/no-explicit-any */
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { DatabaseUploadDialog } from './DatabaseUploadDialog'

const mockToast = vi.hoisted(() => ({
  success: vi.fn(),
  error: vi.fn(),
}))

vi.mock('sonner', () => ({
  toast: mockToast,
}))

vi.mock('/utils/supabase/info', () => ({
  projectId: 'test-project',
}))

const sampleFiles = [
  {
    id: 'file-1',
    originalName: 'kjfk.txt',
    originalContent: 'METAR KJFK',
    convertedContent: '<iwxxm:METAR />',
    timestamp: 1_700_000_000_000,
  },
]

const defaultProps = {
  convertedFiles: sampleFiles,
  isOpen: true,
  onClose: vi.fn(),
  accessToken: 'upload-token',
}

describe('DatabaseUploadDialog', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.useRealTimers()
    vi.spyOn(console, 'error').mockImplementation(() => undefined)
    vi.spyOn(global, 'fetch')
  })

  it('renders nothing when closed', () => {
    const { container } = render(<DatabaseUploadDialog {...defaultProps} isOpen={false} />)
    expect(container).toBeEmptyDOMElement()
  })

  it('shows upload options and file count when open', () => {
    render(<DatabaseUploadDialog {...defaultProps} />)

    expect(screen.getByRole('dialog')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: /upload to database/i })).toBeInTheDocument()
    expect(screen.getByText('1')).toBeInTheDocument()
    expect(screen.getByLabelText(/store as iwxxm xml only/i)).toBeChecked()
    expect(screen.getByLabelText(/upload to primary database/i)).toBeChecked()
  })

  it('closes when backdrop is clicked', async () => {
    const onClose = vi.fn()
    const user = userEvent.setup()
    render(<DatabaseUploadDialog {...defaultProps} onClose={onClose} />)

    await user.click(screen.getByRole('dialog'))
    expect(onClose).toHaveBeenCalledTimes(1)
  })

  it('requires authentication before upload', async () => {
    const user = userEvent.setup()
    render(<DatabaseUploadDialog {...defaultProps} accessToken={undefined} />)

    await user.click(screen.getByRole('button', { name: /upload files to database/i }))

    expect(mockToast.error).toHaveBeenCalledWith('Authentication required. Please log in again.')
    expect(global.fetch).not.toHaveBeenCalled()
  })

  it('uploads selected options successfully and auto-closes', async () => {
    const onClose = vi.fn()
    const user = userEvent.setup()
    vi.mocked(global.fetch).mockResolvedValue({
      ok: true,
      json: async () => ({ message: 'Uploaded 1 file' }),
    } as Response)

    render(<DatabaseUploadDialog {...defaultProps} onClose={onClose} />)

    await user.click(screen.getByLabelText(/store as parsed json only/i))
    await user.click(screen.getByLabelText(/upload to archive database/i))
    await user.click(screen.getByLabelText(/include original metar content in upload/i))
    await user.click(screen.getByRole('button', { name: /upload files to database/i }))

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        'https://test-project.supabase.co/functions/v1/make-server-2e3cda33/database/upload',
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            Authorization: 'Bearer upload-token',
          }),
        }),
      )
    })

    const requestBody = JSON.parse((global.fetch as any).mock.calls[0][1].body)
    expect(requestBody.options).toEqual({
      format: 'json',
      destination: 'archive',
      includeOriginal: true,
    })

    expect(mockToast.success).toHaveBeenCalledWith('Uploaded 1 file')
    expect(screen.getByText(/files uploaded successfully/i)).toBeInTheDocument()

    await waitFor(() => expect(onClose).toHaveBeenCalledTimes(1), { timeout: 3000 })
  })

  it('shows error state when upload fails', async () => {
    const user = userEvent.setup()
    vi.mocked(global.fetch).mockResolvedValue({
      ok: false,
      json: async () => ({ error: 'Database unavailable' }),
    } as Response)

    render(<DatabaseUploadDialog {...defaultProps} />)

    await user.click(screen.getByRole('button', { name: /upload files to database/i }))

    await waitFor(() => {
      expect(mockToast.error).toHaveBeenCalledWith('Database unavailable')
      expect(screen.getByText(/upload failed/i)).toBeInTheDocument()
    })
  })

  it('handles network errors during upload', async () => {
    const user = userEvent.setup()
    vi.mocked(global.fetch).mockRejectedValue(new Error('Network down'))

    render(<DatabaseUploadDialog {...defaultProps} />)

    await user.click(screen.getByRole('button', { name: /upload files to database/i }))

    await waitFor(() => {
      expect(mockToast.error).toHaveBeenCalledWith('Network down')
      expect(screen.getByText(/upload failed/i)).toBeInTheDocument()
    })
  })
})
