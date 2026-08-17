"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { Loader2 } from "lucide-react";

interface OAuthButtonsProps {
  redirectOnSuccess?: string;
}

export function OAuthButtons({ redirectOnSuccess = "/onboarding" }: OAuthButtonsProps) {
  const { signInWithOAuth } = useAuth();
  const router = useRouter();
  const [loadingProvider, setLoadingProvider] = useState<string | null>(null);

  const handleOAuth = async (provider: "google" | "microsoft" | "github") => {
    setLoadingProvider(provider);
    try {
      await signInWithOAuth(provider);
      router.push(redirectOnSuccess);
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingProvider(null);
    }
  };

  return (
    <div className="flex flex-col gap-2.5 w-full">
      {/* Google */}
      <button
        type="button"
        onClick={() => handleOAuth("google")}
        disabled={!!loadingProvider}
        className="flex h-11 w-full items-center justify-center gap-3 rounded-xl border border-white/10 bg-white/[0.04] px-4 text-sm font-medium text-primary transition-all hover:bg-white/[0.08] hover:border-white/20 active:scale-[0.99] disabled:opacity-50"
      >
        {loadingProvider === "google" ? (
          <Loader2 className="h-4 w-4 animate-spin text-accent" />
        ) : (
          <svg className="h-4 w-4" viewBox="0 0 24 24">
            <path
              fill="#EA4335"
              d="M12 5c1.6 0 3 .6 4.1 1.6l3.1-3.1C17.3 1.8 14.8 1 12 1 7.4 1 3.5 3.6 1.6 7.4l3.7 2.9C6.2 7.5 8.9 5 12 5z"
            />
            <path
              fill="#4285F4"
              d="M23.5 12.3c0-.8-.1-1.6-.2-2.3H12v4.5h6.5c-.3 1.5-1.1 2.8-2.4 3.7l3.7 2.9c2.2-2 3.7-5 3.7-8.8z"
            />
            <path
              fill="#FBBC05"
              d="M5.3 14.8c-.2-.7-.4-1.5-.4-2.3s.2-1.6.4-2.3L1.6 7.4C.6 9.4 0 11.6 0 14s.6 4.6 1.6 6.6l3.7-2.9c-.8-1.2-1.3-2.6-1.3-4.1z"
            />
            <path
              fill="#34A853"
              d="M12 23c3.2 0 6-1.1 8-3l-3.7-2.9c-1.1.7-2.5 1.2-4.3 1.2-3.1 0-5.8-2.5-6.7-5.3L1.6 16C3.5 19.8 7.4 23 12 23z"
            />
          </svg>
        )}
        <span>Continue with Google</span>
      </button>

      {/* Microsoft */}
      <button
        type="button"
        onClick={() => handleOAuth("microsoft")}
        disabled={!!loadingProvider}
        className="flex h-11 w-full items-center justify-center gap-3 rounded-xl border border-white/10 bg-white/[0.04] px-4 text-sm font-medium text-primary transition-all hover:bg-white/[0.08] hover:border-white/20 active:scale-[0.99] disabled:opacity-50"
      >
        {loadingProvider === "microsoft" ? (
          <Loader2 className="h-4 w-4 animate-spin text-accent" />
        ) : (
          <svg className="h-4 w-4" viewBox="0 0 23 23">
            <path fill="#f35325" d="M1 1h10v10H1z" />
            <path fill="#81bc06" d="M12 1h10v10H12z" />
            <path fill="#05a6f0" d="M1 12h10v10H1z" />
            <path fill="#ffba08" d="M12 12h10v10H12z" />
          </svg>
        )}
        <span>Continue with Microsoft</span>
      </button>

      {/* GitHub */}
      <button
        type="button"
        onClick={() => handleOAuth("github")}
        disabled={!!loadingProvider}
        className="flex h-11 w-full items-center justify-center gap-3 rounded-xl border border-white/10 bg-white/[0.04] px-4 text-sm font-medium text-primary transition-all hover:bg-white/[0.08] hover:border-white/20 active:scale-[0.99] disabled:opacity-50"
      >
        {loadingProvider === "github" ? (
          <Loader2 className="h-4 w-4 animate-spin text-accent" />
        ) : (
          <svg className="h-4 w-4 fill-current text-primary" viewBox="0 0 24 24">
            <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" />
          </svg>
        )}
        <span>Continue with GitHub</span>
      </button>
    </div>
  );
}
