"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { OAuthButtons } from "@/components/auth/OAuthButtons";
import { Eye, EyeOff, Loader2, Lock, Mail, User as UserIcon, ArrowRight } from "lucide-react";

export default function SignUpPage() {
  const router = useRouter();
  const { signUp } = useAuth();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [acceptTerms, setAcceptTerms] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !email || !password) {
      setError("Please fill in all required fields.");
      return;
    }
    if (!acceptTerms) {
      setError("Please accept the terms of service to continue.");
      return;
    }
    setError("");
    setLoading(true);
    try {
      await signUp(name, email, password);
      // Navigate to email verification screen as required by auth specs
      router.push("/auth/verify-email");
    } catch (err: any) {
      setError(err?.message || "Failed to create account. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="font-display text-2xl font-semibold tracking-tight text-primary">
          Create your account
        </h1>
        <p className="mt-1 text-sm text-secondary">
          Initialize your organization&apos;s AI Digital Twin in seconds
        </p>
      </div>

      {error && (
        <div className="rounded-xl border border-red-500/20 bg-red-500/10 p-3.5 text-xs text-red-400">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        {/* Full Name */}
        <div className="flex flex-col gap-1.5">
          <label className="text-xs font-medium text-secondary">Full Name</label>
          <div className="relative">
            <UserIcon className="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-tertiary" />
            <input
              type="text"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Alex Morgan"
              className="h-11 w-full rounded-xl border border-white/10 bg-white/[0.04] pl-10 pr-4 text-sm text-primary placeholder:text-tertiary focus:border-accent focus:bg-white/[0.06] focus:outline-none transition-all"
            />
          </div>
        </div>

        {/* Email */}
        <div className="flex flex-col gap-1.5">
          <label className="text-xs font-medium text-secondary">Work Email</label>
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

        {/* Password */}
        <div className="flex flex-col gap-1.5">
          <label className="text-xs font-medium text-secondary">Password</label>
          <div className="relative">
            <Lock className="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-tertiary" />
            <input
              type={showPassword ? "text" : "password"}
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Min. 8 characters"
              className="h-11 w-full rounded-xl border border-white/10 bg-white/[0.04] pl-10 pr-12 text-sm text-primary placeholder:text-tertiary focus:border-accent focus:bg-white/[0.06] focus:outline-none transition-all"
            />
            <button
              type="button"
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                setShowPassword((prev) => !prev);
              }}
              className="absolute right-3.5 top-1/2 -translate-y-1/2 text-tertiary hover:text-primary transition-colors z-10 cursor-pointer p-1.5 focus:outline-none"
              aria-label={showPassword ? "Hide password" : "Show password"}
            >
              {showPassword ? <EyeOff className="h-4 w-4 text-accent" /> : <Eye className="h-4 w-4 text-tertiary" />}
            </button>
          </div>
        </div>

        {/* Terms */}
        <div className="flex items-start gap-2.5 pt-1">
          <input
            type="checkbox"
            id="terms"
            checked={acceptTerms}
            onChange={(e) => setAcceptTerms(e.target.checked)}
            className="mt-0.5 h-4 w-4 rounded border-white/20 bg-white/5 text-accent focus:ring-0 accent-accent cursor-pointer"
          />
          <label htmlFor="terms" className="text-xs text-secondary leading-normal cursor-pointer">
            I agree to the{" "}
            <span className="text-primary underline">Terms of Service</span> and{" "}
            <span className="text-primary underline">Privacy Policy</span>.
          </label>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading}
          className="mt-2 flex h-11 w-full items-center justify-center gap-2 rounded-xl bg-accent text-sm font-medium text-white shadow-lg shadow-accent/20 transition-all hover:bg-accent-hover active:scale-[0.99] disabled:opacity-50"
        >
          {loading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <>
              Create Account
              <ArrowRight className="h-4 w-4" />
            </>
          )}
        </button>
      </form>

      {/* Divider */}
      <div className="relative flex items-center justify-center">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-white/10" />
        </div>
        <span className="relative bg-[#E0F2FE] px-3.5 py-1 rounded-full font-mono text-[11px] font-semibold uppercase tracking-wider text-[#171717]">
          OR SIGN UP WITH
        </span>
      </div>

      {/* Social Logins */}
      <OAuthButtons redirectOnSuccess="/onboarding" />

      {/* Sign in prompt */}
      <p className="text-center text-xs text-secondary">
        Already have an account?{" "}
        <Link href="/auth/signin" className="font-medium text-accent hover:underline">
          Sign in
        </Link>
      </p>
    </div>
  );
}
