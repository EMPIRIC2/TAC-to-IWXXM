import { useState, useCallback, useEffect } from 'react'
import { useDropzone } from 'react-dropzone'
import { supabase } from '../utils/supabase/client'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'

interface ConversionResult {
  name: string
  content: string
  source?: string
  size_bytes?: number
}

interface ConversionResponse {
  results: ConversionResult[]
  errors: string[]
  total_processed: number
  successful: number
  failed: number
}

export default function FileConverter() {
  const [files, setFiles] = useState<File[]>([])
  const [manualText, setManualText] = useState('')
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState<ConversionResult[]>([])
  const [errors, setErrors] = useState<string[]>([])
  const [user, setUser] = useState<any>(null)
  const [notification, setNotification] = useState<string>('')
  const navigate = useNavigate()

  const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8001'

  // Get user info on mount
  useEffect(() => {
    supabase.auth.getUser().then(({ data: { user } }) => {
      setUser(user)
    })
  }, [])

  // Show notification with auto-hide
  const showNotification = (message: string) => {
    setNotification(message)
    setTimeout(() => setNotification(''), 3000)
  }

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setFiles((prev) => [...prev, ...acceptedFiles])
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/plain': ['.txt', '.tac'],
    },
  })

  const handleLogout = async () => {
    await supabase.auth.signOut()
    navigate('/login')
  }

  const handleConvert = async () => {
    setLoading(true)
    setResults([])
    setErrors([])

    try {
      const { data: { session } } = await supabase.auth.getSession()
      
      if (!session) {
        throw new Error('No active session')
      }

      const formData = new FormData()
      
      if (manualText.trim()) {
        formData.append('manual_text', manualText.trim())
      }

      files.forEach((file) => {
        formData.append('files', file)
      })

      const response = await axios.post<ConversionResponse>(
        `${backendUrl}/api/convert`,
        formData,
        {
          headers: {
            'Authorization': `Bearer ${session.access_token}`,
            'Content-Type': 'multipart/form-data',
          },
        }
      )

      setResults(response.data.results)
      setErrors(response.data.errors)
    } catch (err: any) {
      console.error('Conversion error:', err)
      if (err.response?.data?.detail) {
        if (typeof err.response.data.detail === 'object') {
          setErrors(err.response.data.detail.errors || [err.response.data.detail.message])
        } else {
          setErrors([err.response.data.detail])
        }
      } else {
        setErrors([err.message || 'Failed to convert files'])
      }
    } finally {
      setLoading(false)
    }
  }

  const handleDownloadZip = async () => {
    try {
      const { data: { session } } = await supabase.auth.getSession()
      
      if (!session) {
        throw new Error('No active session')
      }

      const formData = new FormData()
      
      if (manualText.trim()) {
        formData.append('manual_text', manualText.trim())
      }

      files.forEach((file) => {
        formData.append('files', file)
      })

      const response = await axios.post(
        `${backendUrl}/api/convert-zip`,
        formData,
        {
          headers: {
            'Authorization': `Bearer ${session.access_token}`,
          },
          responseType: 'blob',
        }
      )

      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', 'iwxxm_batch.zip')
      document.body.appendChild(link)
      link.click()
      link.remove()
      showNotification('ZIP file downloaded successfully!')
    } catch (err: any) {
      console.error('Download error:', err)
      showNotification('Failed to download ZIP file')
    }
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    showNotification('Copied to clipboard!')
  }

  const downloadResult = (result: ConversionResult) => {
    const blob = new Blob([result.content], { type: 'text/xml' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', result.name.replace('.txt', '.xml'))
    document.body.appendChild(link)
    link.click()
    link.remove()
  }

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index))
  }

  const clearAll = () => {
    setFiles([])
    setManualText('')
    setResults([])
    setErrors([])
  }

  return (
    <div style={styles.container}>
      {notification && (
        <div style={styles.notification}>
          {notification}
        </div>
      )}
      
      <div style={styles.header}>
        <h1 style={styles.title}>METAR to IWXXM Converter</h1>
        <div style={styles.userInfo}>
          <span style={styles.email}>{user?.email}</span>
          <button onClick={handleLogout} style={styles.logoutButton}>
            Logout
          </button>
        </div>
      </div>

      <div style={styles.content}>
        <div style={styles.card}>
          <h2 style={styles.cardTitle}>Input</h2>

          <div
            {...getRootProps()}
            style={{
              ...styles.dropzone,
              ...(isDragActive ? styles.dropzoneActive : {}),
            }}
          >
            <input {...getInputProps()} />
            <p style={styles.dropzoneText}>
              {isDragActive
                ? 'Drop files here...'
                : 'Drag & drop METAR files here, or click to select'}
            </p>
            <p style={styles.dropzoneHint}>Accepts .txt and .tac files</p>
          </div>

          {files.length > 0 && (
            <div style={styles.fileList}>
              <h3 style={styles.fileListTitle}>Selected Files ({files.length})</h3>
              {files.map((file, index) => (
                <div key={index} style={styles.fileItem}>
                  <span>{file.name}</span>
                  <button
                    onClick={() => removeFile(index)}
                    style={styles.removeButton}
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          )}

          <div style={styles.manualInput}>
            <label style={styles.label}>Manual METAR Input:</label>
            <textarea
              value={manualText}
              onChange={(e) => setManualText(e.target.value)}
              placeholder="Enter METAR text here, e.g., METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005"
              style={styles.textarea}
              rows={4}
            />
          </div>

          <div style={styles.actions}>
            <button
              onClick={handleConvert}
              disabled={loading || (files.length === 0 && !manualText.trim())}
              style={{
                ...styles.button,
                ...styles.primaryButton,
                ...(loading || (files.length === 0 && !manualText.trim())
                  ? styles.buttonDisabled
                  : {}),
              }}
            >
              {loading ? 'Converting...' : 'Convert to IWXXM'}
            </button>

            {results.length > 0 && (
              <button onClick={handleDownloadZip} style={styles.button}>
                Download All as ZIP
              </button>
            )}

            {(files.length > 0 || manualText.trim()) && (
              <button onClick={clearAll} style={styles.clearButton}>
                Clear All
              </button>
            )}
          </div>
        </div>

        {errors.length > 0 && (
          <div style={styles.card}>
            <h2 style={styles.cardTitle}>Errors</h2>
            {errors.map((error, index) => (
              <div key={index} style={styles.error}>
                {error}
              </div>
            ))}
          </div>
        )}

        {results.length > 0 && (
          <div style={styles.card}>
            <h2 style={styles.cardTitle}>Results ({results.length})</h2>
            {results.map((result, index) => (
              <div key={index} style={styles.resultItem}>
                <div style={styles.resultHeader}>
                  <h3 style={styles.resultTitle}>{result.name}</h3>
                  <div style={styles.resultActions}>
                    <button
                      onClick={() => copyToClipboard(result.content)}
                      style={styles.actionButton}
                    >
                      Copy
                    </button>
                    <button
                      onClick={() => downloadResult(result)}
                      style={styles.actionButton}
                    >
                      Download
                    </button>
                  </div>
                </div>
                <pre style={styles.resultContent}>{result.content}</pre>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

const styles = {
  container: {
    minHeight: '100vh',
    backgroundColor: '#f5f5f5',
    position: 'relative' as const,
  },
  notification: {
    position: 'fixed' as const,
    top: '20px',
    right: '20px',
    backgroundColor: '#28a745',
    color: 'white',
    padding: '12px 24px',
    borderRadius: '4px',
    boxShadow: '0 4px 8px rgba(0,0,0,0.2)',
    zIndex: 1000,
    animation: 'slideIn 0.3s ease-out',
  },
  header: {
    backgroundColor: 'white',
    padding: '20px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  title: {
    fontSize: '24px',
    fontWeight: 'bold',
    margin: 0,
  },
  userInfo: {
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
  },
  email: {
    fontSize: '14px',
    color: '#666',
  },
  logoutButton: {
    padding: '8px 16px',
    backgroundColor: '#dc3545',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '14px',
  },
  content: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '20px',
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '20px',
  },
  card: {
    backgroundColor: 'white',
    padding: '24px',
    borderRadius: '8px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
  },
  cardTitle: {
    fontSize: '20px',
    fontWeight: 'bold',
    marginBottom: '16px',
    marginTop: 0,
  },
  dropzone: {
    border: '2px dashed #ccc',
    borderRadius: '8px',
    padding: '40px',
    textAlign: 'center' as const,
    cursor: 'pointer',
    transition: 'border-color 0.2s',
    marginBottom: '16px',
  },
  dropzoneActive: {
    borderColor: '#007bff',
    backgroundColor: '#f0f8ff',
  },
  dropzoneText: {
    fontSize: '16px',
    margin: '0 0 8px 0',
  },
  dropzoneHint: {
    fontSize: '14px',
    color: '#666',
    margin: 0,
  },
  fileList: {
    marginBottom: '16px',
  },
  fileListTitle: {
    fontSize: '16px',
    fontWeight: '500',
    marginBottom: '8px',
  },
  fileItem: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '8px 12px',
    backgroundColor: '#f8f9fa',
    borderRadius: '4px',
    marginBottom: '4px',
  },
  removeButton: {
    background: 'none',
    border: 'none',
    color: '#dc3545',
    cursor: 'pointer',
    fontSize: '24px',
    lineHeight: '1',
    padding: '0 8px',
  },
  manualInput: {
    marginBottom: '16px',
  },
  label: {
    display: 'block',
    fontSize: '14px',
    fontWeight: '500',
    marginBottom: '8px',
  },
  textarea: {
    width: '100%',
    padding: '10px',
    border: '1px solid #ddd',
    borderRadius: '4px',
    fontSize: '14px',
    fontFamily: 'monospace',
    resize: 'vertical' as const,
  },
  actions: {
    display: 'flex',
    gap: '12px',
    flexWrap: 'wrap' as const,
  },
  button: {
    padding: '12px 24px',
    backgroundColor: '#6c757d',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    fontSize: '16px',
    fontWeight: '500',
    cursor: 'pointer',
  },
  primaryButton: {
    backgroundColor: '#007bff',
  },
  buttonDisabled: {
    opacity: 0.6,
    cursor: 'not-allowed',
  },
  clearButton: {
    padding: '12px 24px',
    backgroundColor: 'white',
    color: '#dc3545',
    border: '1px solid #dc3545',
    borderRadius: '4px',
    fontSize: '16px',
    fontWeight: '500',
    cursor: 'pointer',
  },
  error: {
    padding: '12px',
    backgroundColor: '#fee',
    color: '#c33',
    borderRadius: '4px',
    fontSize: '14px',
    marginBottom: '8px',
  },
  resultItem: {
    marginBottom: '24px',
    border: '1px solid #ddd',
    borderRadius: '4px',
    padding: '16px',
  },
  resultHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '12px',
  },
  resultTitle: {
    fontSize: '16px',
    fontWeight: '500',
    margin: 0,
  },
  resultActions: {
    display: 'flex',
    gap: '8px',
  },
  actionButton: {
    padding: '6px 12px',
    backgroundColor: '#007bff',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    fontSize: '14px',
    cursor: 'pointer',
  },
  resultContent: {
    backgroundColor: '#f8f9fa',
    padding: '12px',
    borderRadius: '4px',
    overflow: 'auto',
    fontSize: '12px',
    maxHeight: '400px',
    margin: 0,
  },
}
