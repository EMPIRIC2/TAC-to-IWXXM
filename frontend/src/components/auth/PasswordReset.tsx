import { useState, useEffect } from 'react'
import { supabase } from '../../utils/supabase/client'
import { useNavigate } from 'react-router-dom'

export default function PasswordReset() {
  const [email, setEmail] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [step, setStep] = useState<'request' | 'change'>('request')
  const [emailSent, setEmailSent] = useState(false)
  const [success, setSuccess] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    // Check if we're coming from a password reset link
    const hashParams = new URLSearchParams(window.location.hash.substring(1))
    const type = hashParams.get('type')
    
    if (type === 'recovery') {
      setStep('change')
    }
  }, [])

  const handleRequestReset = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const { error } = await supabase.auth.resetPasswordForEmail(email, {
        redirectTo: `${window.location.origin}/password-reset`,
      })

      if (error) throw error

      setEmailSent(true)
    } catch (err: any) {
      setError(err.message || 'Failed to send reset email')
    } finally {
      setLoading(false)
    }
  }

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (newPassword !== confirmPassword) {
      setError('Passwords do not match')
      return
    }

    if (newPassword.length < 8) {
      setError('Password must be at least 8 characters')
      return
    }

    setLoading(true)

    try {
      const { error } = await supabase.auth.updateUser({
        password: newPassword,
      })

      if (error) throw error

      setSuccess('Password updated successfully!')
      setTimeout(() => navigate('/login'), 2000)
    } catch (err: any) {
      setError(err.message || 'Failed to update password')
    } finally {
      setLoading(false)
    }
  }

  if (emailSent) {
    return (
      <div style={styles.container}>
        <div style={styles.card}>
          <h2 style={styles.title}>Check Your Email</h2>
          <p style={styles.message}>
            We've sent a password reset link to <strong>{email}</strong>.
            Click the link in the email to reset your password.
          </p>
          <button
            onClick={() => navigate('/login')}
            style={styles.button}
          >
            Back to Login
          </button>
        </div>
      </div>
    )
  }

  if (step === 'change') {
    return (
      <div style={styles.container}>
        <div style={styles.card}>
          <h2 style={styles.title}>Set New Password</h2>
          
          <form onSubmit={handleChangePassword} style={styles.form}>
            {error && <div style={styles.error}>{error}</div>}
            {success && <div style={styles.success}>{success}</div>}

            <div style={styles.formGroup}>
              <label style={styles.label}>New Password</label>
              <input
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                required
                minLength={8}
                style={styles.input}
                placeholder="••••••••"
              />
              <small style={styles.hint}>Minimum 8 characters</small>
            </div>

            <div style={styles.formGroup}>
              <label style={styles.label}>Confirm New Password</label>
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                style={styles.input}
                placeholder="••••••••"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              style={{
                ...styles.button,
                ...(loading ? styles.buttonDisabled : {}),
              }}
            >
              {loading ? 'Updating...' : 'Update Password'}
            </button>
          </form>
        </div>
      </div>
    )
  }

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h2 style={styles.title}>Reset Password</h2>
        <p style={styles.subtitle}>
          Enter your email address and we'll send you a link to reset your password.
        </p>
        
        <form onSubmit={handleRequestReset} style={styles.form}>
          {error && <div style={styles.error}>{error}</div>}

          <div style={styles.formGroup}>
            <label style={styles.label}>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              style={styles.input}
              placeholder="you@example.com"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            style={{
              ...styles.button,
              ...(loading ? styles.buttonDisabled : {}),
            }}
          >
            {loading ? 'Sending...' : 'Send Reset Link'}
          </button>

          <div style={styles.links}>
            <button
              type="button"
              onClick={() => navigate('/login')}
              style={styles.linkButton}
            >
              Back to Login
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

const styles = {
  container: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#f5f5f5',
    padding: '20px',
  },
  card: {
    backgroundColor: 'white',
    padding: '40px',
    borderRadius: '8px',
    boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
    maxWidth: '400px',
    width: '100%',
  },
  title: {
    fontSize: '24px',
    fontWeight: 'bold',
    marginBottom: '16px',
    textAlign: 'center' as const,
  },
  subtitle: {
    fontSize: '14px',
    color: '#666',
    marginBottom: '24px',
    textAlign: 'center' as const,
  },
  form: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '16px',
  },
  formGroup: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '8px',
  },
  label: {
    fontSize: '14px',
    fontWeight: '500',
  },
  input: {
    padding: '10px',
    border: '1px solid #ddd',
    borderRadius: '4px',
    fontSize: '14px',
  },
  hint: {
    fontSize: '12px',
    color: '#666',
  },
  button: {
    padding: '12px',
    backgroundColor: '#007bff',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    fontSize: '16px',
    fontWeight: '500',
    cursor: 'pointer',
    marginTop: '8px',
  },
  buttonDisabled: {
    opacity: 0.6,
    cursor: 'not-allowed',
  },
  error: {
    padding: '10px',
    backgroundColor: '#fee',
    color: '#c33',
    borderRadius: '4px',
    fontSize: '14px',
  },
  success: {
    padding: '10px',
    backgroundColor: '#d4edda',
    color: '#155724',
    borderRadius: '4px',
    fontSize: '14px',
  },
  message: {
    fontSize: '14px',
    lineHeight: '1.6',
    marginBottom: '16px',
  },
  links: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '8px',
    marginTop: '8px',
  },
  linkButton: {
    background: 'none',
    border: 'none',
    color: '#007bff',
    cursor: 'pointer',
    fontSize: '14px',
    textDecoration: 'underline',
    padding: '4px',
  },
}
