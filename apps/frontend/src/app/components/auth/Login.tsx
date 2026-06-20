import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Card } from '../ui/card';
import { Mail, Lock, Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import { ThemeToggle } from '../ThemeToggle';
import { login } from '@/utils/authService';

interface LoginFormData {
  email: string;
  password: string;
}

interface LoginProps {
  onLogin: (email: string, needsVerification: boolean, token?: string, adminStatus?: boolean) => void;
  onSwitchToRegister: () => void;
  onForgotPassword: () => void;
}

export function Login({ onLogin, onSwitchToRegister, onForgotPassword: _onForgotPassword }: LoginProps) {
  const [isLoading, setIsLoading] = useState(false);
  const { register, handleSubmit, formState: { errors } } = useForm<LoginFormData>();

  const onSubmit = async (data: LoginFormData) => {
    setIsLoading(true);
    
    try {
      const response = await login({
        email: data.email,
        password: data.password,
      });

      if (!response.user || !response.session) {
        toast.error('Login failed. Please try again.');
        setIsLoading(false);
        return;
      }

      const isAdminUser =
        response.user.metadata?.role === 'admin' ||
        response.user.metadata?.username === 'admin' ||
        response.user.email === 'admin@metar.local';

      toast.success(`Welcome back, ${response.user.metadata?.name || response.user.email}!`);
      
      // Call parent handler with user info
      onLogin(
        response.user.email,
        false, // needsVerification - auth service handles this
        response.session.access_token,
        isAdminUser
      );
      
    } catch (error) {
      console.error('Login error:', error);
      const errorMessage = error instanceof Error ? error.message : 'An error occurred during login. Please try again.';
      toast.error(errorMessage);
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
              METAR Converter
            </h1>
            <p className="text-sm text-muted-foreground font-mono">
              Authentication System v1.0
            </p>
          </div>

          {/* Auth Method Toggle */}
          <div className="flex gap-2 mb-6">
            <button
              type="button"
              disabled
              className="flex-1 px-4 py-2 rounded-md text-sm font-medium transition-colors bg-blue-600 text-white"
            >
              Password Login
            </button>
          </div>

          {/* Login Form */}
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
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
                  className={`pl-10 h-10 text-sm font-mono bg-background border-border focus:border-primary ${errors.email ? 'border-destructive' : ''}`}
                  {...register('email', {
                    required: 'Email is required',
                    pattern: {
                      value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                      message: 'Please enter a valid email address'
                    }
                  })}
                  aria-invalid={errors.email ? 'true' : 'false'}
                  aria-describedby={errors.email ? 'email-error' : undefined}
                />
              </div>
              {errors.email && (
                <p id="email-error" className="text-xs text-destructive mt-1 font-mono" role="alert">
                  {errors.email.message}
                </p>
              )}
            </div>

            <div>
              <Label htmlFor="password" className="text-xs uppercase tracking-wider text-muted-foreground mb-2 block">
                Password
              </Label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" aria-hidden="true" />
                <Input
                  id="password"
                  type="password"
                  placeholder="••••••••"
                  className={`pl-10 h-10 text-sm font-mono bg-background border-border focus:border-primary ${errors.password ? 'border-destructive' : ''}`}
                  {...register('password', {
                    required: 'Password is required',
                    minLength: {
                      value: 6,
                      message: 'Password must be at least 6 characters'
                    }
                  })}
                  aria-invalid={errors.password ? 'true' : 'false'}
                  aria-describedby={errors.password ? 'password-error' : undefined}
                />
              </div>
              {errors.password && (
                <p id="password-error" className="text-xs text-destructive mt-1 font-mono" role="alert">
                  {errors.password.message}
                </p>
              )}
            </div>

            <div className="flex items-center justify-between pt-2">
              <label className="flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  className="w-4 h-4 text-primary border-border focus:ring-2 focus:ring-primary"
                  aria-label="Remember me"
                />
                <span className="ml-2 text-xs text-muted-foreground uppercase tracking-wide">Remember</span>
              </label>
              <button
                type="button"
                className="text-xs text-primary hover:text-primary/80 focus:outline-none focus:underline uppercase tracking-wide"
                aria-label="Forgot password"
              >
                Reset Password
              </button>
            </div>

            <Button
              type="submit"
              disabled={isLoading}
              className="w-full h-10 text-xs"
              aria-label={isLoading ? 'Signing in, please wait' : 'Sign in to account'}
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" aria-hidden="true" />
                  Authenticating...
                </>
              ) : (
                'Authenticate'
              )}
            </Button>
          </form>

          {/* Register Link */}
          <div className="mt-6 pt-6 border-t border-border">
            <p className="text-xs text-center text-muted-foreground">
              No account?{' '}
              <button
                type="button"
                onClick={onSwitchToRegister}
                className="text-primary hover:text-primary/80 font-medium focus:outline-none focus:underline uppercase tracking-wide"
                aria-label="Go to registration page"
              >
                Register
              </button>
            </p>
          </div>

          {/* Admin Access Link */}
          <div className="mt-2 text-center">
            <p className="text-xs text-muted-foreground font-mono">
              <span className="text-secondary">ADMIN:</span> Login to access dashboard
            </p>
          </div>
        </Card>

        {/* Footer */}
        <p className="text-center text-xs text-muted-foreground mt-6 font-mono">
          Terms of Service • Privacy Policy
        </p>
      </div>
    </div>
  );
}