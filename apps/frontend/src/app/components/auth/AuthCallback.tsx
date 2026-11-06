import { useEffect, useState } from 'react';
import { toast } from 'sonner';
import { Loader2, CheckCircle, XCircle } from 'lucide-react';
import { Card } from '../ui/card';
import { confirmEmail } from '@/utils/authService';

interface AuthCallbackProps {
  onLogin?: (email: string, needsVerification: boolean, token?: string) => void;
  onRegister?: (email: string) => void;
  onVerified?: () => void;
}

/**
 * OAuth/email callback handler.
 *
 * Supports:
 * - Supabase token_hash query links (`/auth/confirm?token_hash=…&type=email`)
 * - Legacy hash fragment access_token callbacks (`/auth/callback#access_token=…`)
 * @example
 * const _ = true;
 */
export function AuthCallback({ onLogin, onRegister, onVerified }: AuthCallbackProps) {
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState('Processing your request...');

  useEffect(() => {
    const handleCallback = async () => {
      try {
        const searchParams = new URLSearchParams(window.location.search);
        const tokenHash = searchParams.get('token_hash');
        const queryType = searchParams.get('type') || 'email';

        if (tokenHash) {
          const result = await confirmEmail({
            token_hash: tokenHash,
            type: queryType,
          });

          window.history.replaceState({}, '', '/');

          setStatus('success');
          setMessage('Email verified! Redirecting...');
          toast.success('Email verified successfully!');

          if (queryType === 'recovery') {
            const access = result.session?.access_token;
            window.location.href = access ? `/auth/reset?token=${access}` : '/';
            return;
          }

          if (onVerified) {
            onVerified();
          } else if (onLogin && result.session?.access_token) {
            onLogin(result.user.email, false, result.session.access_token);
          } else if (onRegister) {
            onRegister(result.user.email);
          } else {
            window.location.href = '/';
          }
          return;
        }

        // Legacy: extract token from URL hash (implicit / older templates)
        const hashParams = new URLSearchParams(window.location.hash.substring(1));
        const accessToken = hashParams.get('access_token');
        const type = hashParams.get('type');

        hashParams.get('refresh_token');
        hashParams.get('expires_at');

        if (!accessToken) {
          console.warn('No access token or token_hash found in callback');
          setStatus('error');
          setMessage('Invalid callback URL. Please try again.');
          toast.error('Authentication failed');
          setTimeout(() => {
            window.location.hash = '';
            window.location.href = '/';
          }, 2000);
          return;
        }

        window.location.hash = '';

        console.log('Email verified successfully through auth callback');
        setStatus('success');
        setMessage('Email verified! Redirecting...');
        toast.success('Email verified successfully!');

        if (type === 'signup' || type === 'email') {
          if (onVerified) {
            onVerified();
          } else if (onRegister) {
            onRegister('');
          }
        } else if (type === 'recovery') {
          window.location.href = `/auth/reset?token=${accessToken}`;
        } else {
          window.location.href = '/';
        }
      } catch (error) {
        console.error('Callback error:', error);
        setStatus('error');
        const detail =
          error instanceof Error && error.message
            ? error.message
            : 'An error occurred. Please try again.';
        setMessage(detail);
        toast.error('Authentication failed');
        setTimeout(() => {
          window.location.hash = '';
          window.location.href = '/';
        }, 2000);
      }
    };

    void handleCallback();
  }, [onLogin, onRegister, onVerified]);

  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-4 py-8 transition-colors">
      <Card className="w-full max-w-md p-8 bg-card border-border">
        <div className="text-center">
          {status === 'loading' && (
            <>
              <Loader2 className="w-12 h-12 mx-auto mb-4 text-primary animate-spin" />
              <h2 className="text-lg font-semibold text-foreground mb-2 uppercase tracking-tight">
                Processing
              </h2>
              <p className="text-sm text-muted-foreground font-mono">{message}</p>
            </>
          )}

          {status === 'success' && (
            <>
              <CheckCircle className="w-12 h-12 mx-auto mb-4 text-emerald-600 dark:text-emerald-400" />
              <h2 className="text-lg font-semibold text-foreground mb-2 uppercase tracking-tight">
                Success
              </h2>
              <p className="text-sm text-muted-foreground font-mono">{message}</p>
            </>
          )}

          {status === 'error' && (
            <>
              <XCircle className="w-12 h-12 mx-auto mb-4 text-destructive" />
              <h2 className="text-lg font-semibold text-foreground mb-2 uppercase tracking-tight">
                Error
              </h2>
              <p className="text-sm text-muted-foreground mb-4 font-mono">{message}</p>
              <button
                type="button"
                onClick={() => {
                  window.location.hash = '';
                  window.location.href = '/';
                }}
                className="text-xs text-primary hover:text-primary/80 font-medium focus:outline-none focus:underline uppercase tracking-wide"
              >
                Return to Login
              </button>
            </>
          )}
        </div>
      </Card>
    </div>
  );
}
