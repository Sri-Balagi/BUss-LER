"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { ArrowLeft, CheckCircle2, Loader2, Mail } from "lucide-react";

export default function ForgotPasswordPage() {
  const { forgotPassword } = useAuth();
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;
    setLoading(true);
    try {
      await forgotPassword(email);
      setSubmitted(true);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-6">
      <Link
        href="/auth/signin"
        className="inline-flex items-center gap-1.5 text-xs text-secondary hover:text-primary transition-colors"
      >
        <ArrowLeft className="h-3.5 w-3.5" />
        <span>Back to Sign In</span>
      </Link>

      <div>
        <h1 className="font-display text-2xl font-semibold tracking-tight text-primary">
          Reset password
        </h1>
        <p className="mt-1 text-sm text-secondary">
          Enter your registered email address to receive password reset instructions.
        </p>
      </div>

      {submitted ? (
        <div className="flex flex-col items-center justify-center text-center p-6 rounded-2xl border border-emerald-500/20 bg-emerald-500/10 gap-3">
          <CheckCircle2 className="h-10 w-10 text-emerald-400 animate-bounce" />
          <h3 className="text-base font-medium text-emerald-300">Instructions Sent</h3>
          <p className="text-xs text-secondary leading-relaxed">
            We sent a password reset link to <strong className="text-primary">{email}</strong>.
            Please check your inbox.
          </p>
          <button
            onClick={() => setSubmitted(false)}
            className="mt-2 text-xs text-accent hover:underline font-medium"
          >
            Resend email
          </button>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-medium text-secondary">Work Email Address</label>
            <div className="relative">
              <Mail className="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-tertiary" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="alex@company.com"
                className="h-11 w-full rounded-xl border border-white/10 bg-white/[0.04] pl-10 pr-4 text-sm text-primary placeholder:text-tertiary focus:border-accent focus:bg-white/[0.06] focus:outline-none transition-all"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="mt-2 flex h-11 w-full items-center justify-center gap-2 rounded-xl bg-accent text-sm font-medium text-white shadow-lg shadow-accent/20 transition-all hover:bg-accent-hover active:scale-[0.99] disabled:opacity-50"
          >
            {loading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              "Send Reset Link"
            )}
          </button>
        </form>
      )}
    </div>
  );
}
