'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Mail, Loader2, CheckCircle, ArrowRight, Lock, KeyRound } from 'lucide-react';

export default function LoginPage() {
    const { signIn, signInWithPassword } = useAuth();
    const router = useRouter();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [isSent, setIsSent] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [usePassword, setUsePassword] = useState(false);

    const handleMagicLink = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);

        if (!email || !email.includes('@')) {
            setError('Please enter a valid email address');
            return;
        }

        setIsLoading(true);
        try {
            const result = await signIn(email);
            if (result.error) {
                setError(result.error);
            } else {
                setIsSent(true);
            }
        } catch {
            setError('An unexpected error occurred. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    const handlePasswordLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);

        if (!email || !email.includes('@')) {
            setError('Please enter a valid email address');
            return;
        }
        if (!password) {
            setError('Please enter your password');
            return;
        }

        setIsLoading(true);
        try {
            const result = await signInWithPassword(email, password);
            if (result.error) {
                setError(result.error);
            } else {
                router.push('/dashboard');
            }
        } catch {
            setError('An unexpected error occurred. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="space-y-8 animate-fade-in">
            {/* Logo */}
            <div className="text-center space-y-2">
                <div className="inline-flex items-center justify-center h-16 w-16 rounded-2xl bg-gold/20 border border-gold/30 mb-4">
                    <span className="text-2xl font-bold text-gold">C</span>
                </div>
                <h1 className="text-3xl font-bold text-foreground">CMA AutoFill</h1>
                <p className="text-muted-foreground">
                    Automate your Credit Monitoring Arrangement documents
                </p>
            </div>

            {isSent ? (
                /* Success State */
                <div
                    className="rounded-xl p-8 text-center space-y-4 border border-border/20"
                    style={{ backgroundColor: 'var(--bg-card)' }}
                >
                    <div className="inline-flex items-center justify-center h-14 w-14 rounded-full bg-success/20">
                        <CheckCircle className="h-7 w-7 text-success" />
                    </div>
                    <h2 className="text-xl font-semibold text-foreground">Check your email</h2>
                    <p className="text-muted-foreground text-sm">
                        We&apos;ve sent a magic link to{' '}
                        <span className="font-medium text-foreground">{email}</span>.
                        <br />
                        Click the link in the email to sign in.
                    </p>
                    <Button
                        variant="ghost"
                        className="text-gold hover:text-gold-hover"
                        onClick={() => {
                            setIsSent(false);
                            setEmail('');
                        }}
                    >
                        Use a different email
                    </Button>
                </div>
            ) : (
                /* Login Form */
                <form
                    onSubmit={usePassword ? handlePasswordLogin : handleMagicLink}
                    className="rounded-xl p-8 space-y-6 border border-border/20"
                    style={{ backgroundColor: 'var(--bg-card)' }}
                >
                    <div className="space-y-2">
                        <h2 className="text-xl font-semibold text-foreground">Sign in</h2>
                        <p className="text-sm text-muted-foreground">
                            {usePassword
                                ? 'Enter your email and password'
                                : 'Enter your email to receive a magic link'}
                        </p>
                    </div>

                    <div className="space-y-4">
                        <div className="relative">
                            <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                            <Input
                                type="email"
                                placeholder="you@example.com"
                                value={email}
                                onChange={(e) => {
                                    setEmail(e.target.value);
                                    setError(null);
                                }}
                                className="pl-10 h-12 bg-background/50 border-border/30 focus:border-gold focus:ring-gold/30"
                                disabled={isLoading}
                                autoFocus
                            />
                        </div>

                        {usePassword && (
                            <div className="relative">
                                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                                <Input
                                    type="password"
                                    placeholder="Password"
                                    value={password}
                                    onChange={(e) => {
                                        setPassword(e.target.value);
                                        setError(null);
                                    }}
                                    className="pl-10 h-12 bg-background/50 border-border/30 focus:border-gold focus:ring-gold/30"
                                    disabled={isLoading}
                                />
                            </div>
                        )}

                        {error && (
                            <p className="text-sm text-destructive flex items-center gap-2">
                                <span className="h-1 w-1 rounded-full bg-destructive" />
                                {error}
                            </p>
                        )}

                        <Button
                            type="submit"
                            className="w-full h-12 bg-gold hover:bg-gold-hover text-primary-foreground font-semibold text-base transition-all duration-200"
                            disabled={isLoading}
                        >
                            {isLoading ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    {usePassword ? 'Signing in...' : 'Sending...'}
                                </>
                            ) : usePassword ? (
                                <>
                                    Sign In
                                    <ArrowRight className="ml-2 h-4 w-4" />
                                </>
                            ) : (
                                <>
                                    Send Magic Link
                                    <ArrowRight className="ml-2 h-4 w-4" />
                                </>
                            )}
                        </Button>
                    </div>

                    <div className="relative">
                        <div className="absolute inset-0 flex items-center">
                            <div className="w-full border-t border-border/30" />
                        </div>
                        <div className="relative flex justify-center text-xs">
                            <span className="px-2 text-muted-foreground" style={{ backgroundColor: 'var(--bg-card)' }}>
                                or
                            </span>
                        </div>
                    </div>

                    <Button
                        type="button"
                        variant="ghost"
                        className="w-full text-muted-foreground hover:text-foreground"
                        onClick={() => {
                            setUsePassword(!usePassword);
                            setError(null);
                        }}
                    >
                        <KeyRound className="mr-2 h-4 w-4" />
                        {usePassword ? 'Use magic link instead' : 'Sign in with password'}
                    </Button>
                </form>
            )}
        </div>
    );
}
