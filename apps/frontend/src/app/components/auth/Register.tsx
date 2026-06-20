import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Card } from '../ui/card';
import { Mail, Lock, Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import { ThemeToggle } from '../ThemeToggle';
import { register as registerUser } from '@/utils/authService';

interface RegisterFormData {
  email: string;
  password: string;
  confirmPassword: string;
}

interface RegisterProps {
  onRegister: (email: string) => void;
  onSwitchToLogin: () => void;
}

export function Register({ onRegister, onSwitchToLogin }: RegisterProps) {
  const [isLoading, setIsLoading] = useState(false);
  const { register, handleSubmit, watch, formState: { errors } } = useForm<RegisterFormData>();
  
  // eslint-disable-next-line react-hooks/incompatible-library
  const password = watch('password');

  const onSubmit = async (data: RegisterFormData) => {
    setIsLoading(true);
    
    try {
      const response = await registerUser({
        email: data.email,
        password: data.password,
      });

      if (!response.user) {
        toast.error('Registration failed. Please try again.');
        setIsLoading(false);
        return;
      }

      toast.success('Account created! Please check your email to verify your account.');
      onRegister(data.email);
      
    } catch (error) {
      console.error('Registration error:', error);
      const errorMessage = error instanceof Error ? error.message : 'An error occurred during registration. Please try again.';
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
              Create Account
            </h1>
            <p className="text-sm text-muted-foreground font-mono">
              METAR Converter Registration
            </p>
          </div>

          {/* Register Form */}
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
                  className={`pl-10 h-10 text-sm font-mono bg-background border-border focus:border-primary ${errors.confirmPassword ? 'border-destructive' : ''}`}
                  {...register('confirmPassword', {
                    required: 'Please confirm your password',
                    validate: value => value === password || 'Passwords do not match'
                  })}
                  aria-invalid={errors.confirmPassword ? 'true' : 'false'}
                  aria-describedby={errors.confirmPassword ? 'confirmPassword-error' : undefined}
                />
              </div>
              {errors.confirmPassword && (
                <p id="confirmPassword-error" className="text-xs text-destructive mt-1 font-mono" role="alert">
                  {errors.confirmPassword.message}
                </p>
              )}
            </div>

            <div className="flex items-center pt-2">
              <input
                type="checkbox"
                id="terms"
                className="w-4 h-4 text-primary border-border focus:ring-2 focus:ring-primary"
                required
                aria-label="Accept terms and conditions"
              />
              <label htmlFor="terms" className="ml-2 text-xs text-muted-foreground uppercase tracking-wide">
                I agree to the Terms of Service
              </label>
            </div>

            <Button
              type="submit"
              disabled={isLoading}
              className="w-full h-10 text-xs"
              aria-label={isLoading ? 'Creating account, please wait' : 'Create account'}
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" aria-hidden="true" />
                  Creating Account...
                </>
              ) : (
                'Create Account'
              )}
            </Button>
          </form>

          {/* Login Link */}
          <div className="mt-6 pt-6 border-t border-border">
            <p className="text-xs text-center text-muted-foreground">
              Already have an account?{' '}
              <button
                type="button"
                onClick={onSwitchToLogin}
                className="text-primary hover:text-primary/80 font-medium focus:outline-none focus:underline uppercase tracking-wide"
                aria-label="Go to login page"
              >
                Sign In
              </button>
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