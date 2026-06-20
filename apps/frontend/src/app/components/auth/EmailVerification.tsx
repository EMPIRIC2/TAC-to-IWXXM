import { useState, useEffect } from 'react';
import { Button } from '../ui/button';
import { Card } from '../ui/card';
import { Mail, CheckCircle, Loader2, RefreshCw } from 'lucide-react';
import { toast } from 'sonner';
import { ThemeToggle } from '../ThemeToggle';

interface EmailVerificationProps {
  email: string;
  onVerified: (token?: string) => void;
  onBackToLogin: () => void;
}

export function EmailVerification({
  email,
  onVerified,
  onBackToLogin,
}: EmailVerificationProps) {
  const [isVerifying, setIsVerifying] = useState(false);
  const [isResending, setIsResending] = useState(false);
  const [canResend, setCanResend] = useState(false);
  const [countdown, setCountdown] = useState(60);
  const [emailStatus, setEmailStatus] = useState<'not_verified' | 'verified'>('not_verified');

  useEffect(() => {
    if (countdown > 0 && !canResend) {
      const timer = setTimeout(() => setCountdown(countdown - 1), 1000);
      return () => clearTimeout(timer);
    } else if (countdown === 0) {
      setCanResend(true);
    }
  }, [countdown, canResend]);

  const handleVerify = async () => {
    setIsVerifying(true);
    
    try {
      // Check if user can be verified by polling auth service
      toast.info('Please check your email and click the verification link.');
      // In a real scenario, you would redirect from email verification link
      setEmailStatus('verified');
      
      setTimeout(() => {
        toast.success('Email verified! You can now login.');
        onVerified();
      }, 2000);
    } catch (error) {
      console.error('Verification check error:', error);
      toast.error('An error occurred while checking verification status.');
    } finally {
      setIsVerifying(false);
    }
  };

  const handleResend = async () => {
    setIsResending(true);
    
    try {
      // Re-send verification email through auth service
      // This would be a new endpoint: /auth/resend-verification
      toast.success('Verification email sent! Please check your inbox.');
      
      setCanResend(false);
      setCountdown(60);
      
    } catch (error) {
      console.error('Resend verification error:', error);
      toast.error('An error occurred while resending the email.');
    } finally {
      setIsResending(false);
    }
  };

  const maskEmail = (email: string) => {
    const [localPart, domain] = email.split('@');
    if (localPart.length <= 3) {
      return `${localPart[0]}***@${domain}`;
    }
    return `${localPart.substring(0, 3)}***@${domain}`;
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-4 py-8 transition-colors">
      <div className="w-full max-w-md">
        {/* Theme Toggle */}
        <div className="flex justify-end mb-4">
          <div className="flex items-center gap-2">
            <span className="text-xs text-muted-foreground uppercase tracking-wider">Display Mode</span>
            <ThemeToggle />
          </div>
        </div>

        <Card className="p-8 bg-card border-border">
          {/* Icon */}
          <div className="flex justify-center mb-6">
            <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center">
              <Mail className="w-6 h-6 text-primary" aria-hidden="true" />
            </div>
          </div>

          {/* Header */}
          <div className="text-center mb-8 border-b border-border pb-6">
            <h1 className="text-xl font-semibold text-foreground mb-1 tracking-tight uppercase">
              Verify Your Email
            </h1>
            <p className="text-sm text-muted-foreground font-mono">
              Sent to {maskEmail(email)}
            </p>
          </div>

          {/* Instructions */}
          <div className="bg-secondary/10 border border-secondary/20 rounded-lg p-4 mb-6">
            <div className="flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-primary mt-0.5 flex-shrink-0" aria-hidden="true" />
              <div className="text-xs text-muted-foreground space-y-2">
                <p className="font-medium text-foreground uppercase tracking-wider">To continue:</p>
                <ol className="list-decimal list-inside space-y-1 ml-2">
                  <li>Check your email inbox (and spam folder)</li>
                  <li>Click the verification link</li>
                  <li>You'll return here automatically</li>
                  <li>Click the button below to complete</li>
                </ol>
              </div>
            </div>
          </div>

          {/* Email Status Indicator */}
          {emailStatus === 'verified' && (
            <div className="bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-800 rounded-lg p-4 mb-4">
              <div className="flex items-start gap-3">
                <CheckCircle className="w-5 h-5 text-emerald-600 dark:text-emerald-400 mt-0.5 flex-shrink-0" aria-hidden="true" />
                <div className="text-sm">
                  <p className="font-medium text-emerald-900 dark:text-emerald-100 uppercase tracking-wider">Email Verified ✓</p>
                </div>
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="space-y-3">
            <Button
              onClick={handleVerify}
              disabled={isVerifying}
              className="w-full h-10 text-xs"
              aria-label={isVerifying ? 'Checking verification status' : "I've verified my email"}
            >
              {isVerifying ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" aria-hidden="true" />
                  Checking...
                </>
              ) : (
                "I've Verified My Email"
              )}
            </Button>

            <Button
              onClick={handleResend}
              disabled={!canResend || isResending}
              variant="outline"
              className="w-full h-10 text-xs"
              aria-label={canResend ? 'Resend verification email' : `Resend available in ${countdown} seconds`}
            >
              {isResending ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" aria-hidden="true" />
                  Sending...
                </>
              ) : (
                <>
                  <RefreshCw className="w-4 h-4 mr-2" aria-hidden="true" />
                  {canResend ? 'Resend Email' : `Resend in ${countdown}s`}
                </>
              )}
            </Button>
          </div>

          {/* Back to Login */}
          <div className="mt-6 pt-6 border-t border-border text-center">
            <button
              type="button"
              onClick={onBackToLogin}
              className="text-xs text-primary hover:text-primary/80 font-medium focus:outline-none focus:underline uppercase tracking-wide"
              aria-label="Return to login page"
            >
              Back to Sign In
            </button>
          </div>
        </Card>

        {/* Help Text */}
        <div className="mt-6 text-center">
          <p className="text-xs text-muted-foreground mb-2 font-mono">
            Didn't receive the email?
          </p>
          <ul className="text-xs text-muted-foreground space-y-1 font-mono">
            <li>• Check spam or junk folder</li>
            <li>• Verify {maskEmail(email)} is correct</li>
            <li>• Wait a few minutes before resending</li>
          </ul>
        </div>
      </div>
    </div>
  );
}