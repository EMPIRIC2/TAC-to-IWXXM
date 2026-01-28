import { useState } from 'react'
import { supabase } from '../../utils/supabase/client'
import { useNavigate } from 'react-router-dom'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [authMethod, setAuthMethod] = useState<'password' | 'magic-link'>('password')
  const [magicLinkSent, setMagicLinkSent] = useState(false)
  const navigate = useNavigate()

  const handlePasswordLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password,
      })

      if (error) throw error

      if (data.session) {
        navigate('/converter')
      }
    } catch (err: any) {
      setError(err.message || 'Failed to login')
    } finally {
      setLoading(false)
    }
  }

  const handleMagicLink = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const { error } = await supabase.auth.signInWithOtp({
        email,
        options: {
          emailRedirectTo: `${window.location.origin}/converter`,
        },
      })

      if (error) throw error

      setMagicLinkSent(true)
    } catch (err: any) {
      setError(err.message || 'Failed to send magic link')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = authMethod === 'password' ? handlePasswordLogin : handleMagicLink

  if (magicLinkSent) {
    return (
      <div style={styles.container}>
        <div style={styles.card}>
          <h2 style={styles.title}>Check Your Email</h2>
          <p style={styles.message}>
            We've sent a magic link to <strong>{email}</strong>.
            Click the link in the email to sign in.
          </p>
          <button
            onClick={() => {
              setMagicLinkSent(false)
              setEmail('')
            }}
            style={styles.linkButton}
          >
            Back to Login
          </button>
        </div>
      </div>
    )
  }

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h2 style={styles.title}>Sign In</h2>
        
        <div style={styles.authMethodToggle}>
          <button
            onClick={() => setAuthMethod('password')}
            style={{
              ...styles.toggleButton,
              ...(authMethod === 'password' ? styles.toggleButtonActive : {}),
            }}
          >
            Password
          </button>
          <button
            onClick={() => setAuthMethod('magic-link')}
            style={{
              ...styles.toggleButton,
              ...(authMethod === 'magic-link' ? styles.toggleButtonActive : {}),
            }}
          >
            Magic Link
          </button>
        </div>

        <form onSubmit={handleSubmit} style={styles.form}>
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

          {authMethod === 'password' && (
            <div style={styles.formGroup}>
              <label style={styles.label}>Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                style={styles.input}
                placeholder="••••••••"
              />
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            style={{
              ...styles.button,
              ...(loading ? styles.buttonDisabled : {}),
            }}
          >
            {loading ? 'Please wait...' : authMethod === 'password' ? 'Sign In' : 'Send Magic Link'}
          </button>

          <div style={styles.links}>
            <button
              type="button"
              onClick={() => navigate('/register')}
              style={styles.linkButton}
            >
              Don't have an account? Register
            </button>
            {authMethod === 'password' && (
              <button
                type="button"
                onClick={() => navigate('/password-reset')}
                style={styles.linkButton}
              >
                Forgot password?
              </button>
            )}
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
    marginBottom: '24px',
    textAlign: 'center' as const,
  },
  authMethodToggle: {
    display: 'flex',
    gap: '8px',
    marginBottom: '24px',
  },
  toggleButton: {
    flex: 1,
    padding: '10px',
    border: '1px solid #ddd',
    backgroundColor: 'white',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '14px',
  },
  toggleButtonActive: {
    backgroundColor: '#007bff',
    color: 'white',
    borderColor: '#007bff',
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
