import { useState } from 'react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Card } from '../ui/card';
import { Mail, ArrowLeft, Loader2, Lock } from 'lucide-react';
import { toast } from 'sonner';
import { ThemeToggle } from '../ThemeToggle';
import { requestPasswordReset, confirmPasswordReset } from '@/utils/authService';

interface PasswordResetProps {
  onBackToLogin: () => void;
  resetToken?: string; // Token from URL callback
}

export function PasswordReset({ onBackToLogin, resetToken }: PasswordResetProps) {
  const [step, _setStep] = useState<'request' | 'reset'>(!resetToken ? 'request' : 'reset');
  const [email, setEmail] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // Step 1: Request password reset email
  const handleResetRequest = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!email) {
      toast.error('Please enter your email address');
      return;
    }

    setIsLoading(true);

    try {
      await requestPasswordReset(email);
      toast.success('Password reset email sent! Check your inbox.');
      setEmail('');
    } catch (error) {
      console.error('Password reset error:', error);
      const errorMessage = error instanceof Error ? error.message : 'Failed to send password reset email';
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  // Step 2: Update password (called after user clicks reset link)
  const handlePasswordUpdate = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!newPassword) {
      toast.error('Please enter a new password');
      return;
    }

    if (newPassword !== confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }

    if (newPassword.length < 6) {
      toast.error('Password must be at least 6 characters');
      return;
    }

    if (!resetToken) {
      toast.error('Reset token not found');
      return;
    }

    setIsLoading(true);

    try {
      await confirmPasswordReset(resetToken, newPassword);
      toast.success('✓ Password updated successfully! Redirecting to login...');
      setTimeout(() => {
        onBackToLogin();
      }, 2000);
    } catch (error) {
      console.error('Password update error:', error);
      const errorMessage = error instanceof Error ? error.message : 'Failed to update password';
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
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
          {/* Header */}
          <div className="mb-8 border-b border-border pb-6">
            <h1 className="text-xl font-semibold text-foreground mb-1 tracking-tight uppercase">
              Reset Password
            </h1>
            <p className="text-sm text-muted-foreground font-mono">
              {step === 'request'
                ? 'Recover your account access'
                : 'Create a new password'}
            </p>
          </div>

          {/* Step 1: Request Reset Email */}
          {step === 'request' && (
            <form onSubmit={handleResetRequest} className="space-y-4">
              <div>
                <Label htmlFor="email" className="text-xs uppercase tracking-wider text-muted-foreground mb-2 block">
                  Email Address
                </Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" aria-hidden="true" />
                  <Input
                    id="email"
                    type="email"
                    placeholder="user@domain.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="pl-10 h-10 text-sm font-mono bg-background border-border focus:border-primary"
                    aria-label="Email address"
                    required
                  />
                </div>
              </div>

              <p className="text-xs text-muted-foreground font-mono">
                We'll send a recovery link to your email address.
              </p>

              <Button
                type="submit"
                disabled={isLoading}
                className="w-full h-10 text-xs"
                aria-label={isLoading ? 'Sending reset email' : 'Send reset email'}
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" aria-hidden="true" />
                    Sending...
                  </>
                ) : (
                  'Send Reset Email'
                )}
              </Button>
            </form>
          )}

          {/* Step 2: Update Password (After clicking reset link) */}
          {step === 'reset' && (
            <form onSubmit={handlePasswordUpdate} className="space-y-4">
              <div>
                <Label htmlFor="newPassword" className="text-xs uppercase tracking-wider text-muted-foreground mb-2 block">
                  New Password
                </Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" aria-hidden="true" />
                  <Input
                    id="newPassword"
                    type="password"
                    placeholder="••••••••"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    className="pl-10 h-10 text-sm font-mono bg-background border-border focus:border-primary"
                    aria-label="New password"
                    required
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="confirmPassword" className="text-xs uppercase tracking-wider text-muted-foreground mb-2 block">
                  Confirm Password
                </Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" aria-hidden="true" />
                  <Input
                    id="confirmPassword"
                    type="password"
                    placeholder="••••••••"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    className="pl-10 h-10 text-sm font-mono bg-background border-border focus:border-primary"
                    aria-label="Confirm password"
                    required
                  />
                </div>
              </div>

              <Button
                type="submit"
                disabled={isLoading || !newPassword || !confirmPassword}
                className="w-full h-10 text-xs"
                aria-label={isLoading ? 'Updating password' : 'Update password'}
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" aria-hidden="true" />
                    Updating...
                  </>
                ) : (
                  '✓ Update Password'
                )}
              </Button>
            </form>
          )}

          {/* Back to Login */}
          <button
            type="button"
            onClick={onBackToLogin}
            className="w-full mt-6 flex items-center justify-center text-xs text-primary hover:text-primary/80 font-medium focus:outline-none focus:underline uppercase tracking-wide"
            aria-label="Back to login"
          >
            <ArrowLeft className="w-4 h-4 mr-2" aria-hidden="true" />
            Back to Sign In
          </button>
        </Card>

        {/* Footer */}
        <p className="text-center text-xs text-muted-foreground mt-6 font-mono">
          Terms of Service • Privacy Policy
        </p>
      </div>
    </div>
  );
}
