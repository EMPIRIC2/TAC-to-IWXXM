import { useEffect, useState } from 'react';
import { toast } from 'sonner';
import { Loader2, CheckCircle, XCircle } from 'lucide-react';
import { Card } from '../ui/card';

interface AuthCallbackProps {
  onLogin?: (email: string, needsVerification: boolean, token?: string) => void;
  onRegister?: (email: string) => void;
  onVerified?: () => void;
}

export function AuthCallback({ onLogin, onRegister, onVerified }: AuthCallbackProps) {
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState('Processing your request...');

  useEffect(() => {
    const handleCallback = async () => {
      try {
        // Extract token from URL hash (Supabase or custom auth service format)
        const hashParams = new URLSearchParams(window.location.hash.substring(1));
        const accessToken = hashParams.get('access_token');
        const type = hashParams.get('type');
        
        // Also check for refresh token and expires_at
        hashParams.get('refresh_token');
        hashParams.get('expires_at');

        if (!accessToken) {
          console.warn('No access token found in callback');
          setStatus('error');
          setMessage('Invalid callback URL. Please try again.');
          toast.error('Authentication failed');
          setTimeout(() => {
            window.location.hash = '';
            window.location.href = '/';
          }, 2000);
          return;
        }

        // Clear the hash from URL
        window.location.hash = '';

        console.log('Email verified successfully through auth callback');
        setStatus('success');
        setMessage('Email verified! Redirecting...');
        toast.success('Email verified successfully!');

        // Redirect based on callback type
        if (type === 'signup') {
          if (onVerified) {
            onVerified();
          } else if (onRegister) {
            onRegister('');
          }
        } else if (type === 'recovery') {
          // Password reset callback
          // In this case, the token can be used for password reset
          window.location.href = `/auth/reset?token=${accessToken}`;
        } else {
          // Default: redirect to home
          window.location.href = '/';
        }
      } catch (error) {
        console.error('Callback error:', error);
        setStatus('error');
        setMessage('An error occurred. Please try again.');
        toast.error('Authentication failed');
        setTimeout(() => {
          window.location.hash = '';
          window.location.href = '/';
        }, 2000);
      }
    };

    handleCallback();
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
              <p className="text-sm text-muted-foreground font-mono">
                {message}
              </p>
            </>
          )}

          {status === 'success' && (
            <>
              <CheckCircle className="w-12 h-12 mx-auto mb-4 text-emerald-600 dark:text-emerald-400" />
              <h2 className="text-lg font-semibold text-foreground mb-2 uppercase tracking-tight">
                Success
              </h2>
              <p className="text-sm text-muted-foreground font-mono">
                {message}
              </p>
            </>
          )}

          {status === 'error' && (
            <>
              <XCircle className="w-12 h-12 mx-auto mb-4 text-destructive" />
              <h2 className="text-lg font-semibold text-foreground mb-2 uppercase tracking-tight">
                Error
              </h2>
              <p className="text-sm text-muted-foreground mb-4 font-mono">
                {message}
              </p>
              <button
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
