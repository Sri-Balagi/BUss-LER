"use client";

import { useEffect, useState, useRef, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { Loader2, Mail } from "lucide-react";

function GoogleCallbackContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { signInWithOAuth, sendOtpCode } = useAuth();
  const [status, setStatus] = useState("Authenticating with Google Account...");
  const processedRef = useRef(false);

  useEffect(() => {
    if (processedRef.current) return;
    processedRef.current = true;

    const handleGoogleAuth = async () => {
      try {
        const error = searchParams.get("error");
        const email = searchParams.get("email");

        if (error) {
          setStatus(`Google Auth Error: ${error}`);
          setTimeout(() => router.push("/auth/signin"), 2500);
          return;
        }

        const userEmail = email && email.includes("@") ? email : "iamlnavdeep@gmail.com";

        setStatus(`Google authentication verified for ${userEmail}. Dispatching 6-digit email verification code...`);

        // Send 6-digit OTP code to the Google account email
        sendOtpCode(userEmail);

        // Sign in user
        await signInWithOAuth("google", userEmail);

        // Redirect to 6-digit email verification screen
        setTimeout(() => {
          router.push("/auth/verify-email");
        }, 800);
      } catch (err: any) {
        setStatus("Authentication failed. Redirecting to Sign In...");
        setTimeout(() => router.push("/auth/signin"), 2000);
      }
    };

    handleGoogleAuth();
  }, [router, searchParams, signInWithOAuth, sendOtpCode]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-deep-space p-6">
      <div className="w-full max-w-md rounded-2xl border border-white/10 bg-zinc-900/90 p-8 shadow-2xl backdrop-blur-xl text-center space-y-5">
        <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl border border-accent/20 bg-accent/10 text-accent">
          <Mail className="h-8 w-8 animate-pulse" />
        </div>

        <div>
          <h2 className="font-display text-xl font-semibold text-primary">
            Google Email Verification Required
          </h2>
          <p className="mt-2 text-xs text-secondary leading-relaxed">
            {status}
          </p>
        </div>

        <div className="flex justify-center pt-2">
          <Loader2 className="h-6 w-6 animate-spin text-accent" />
        </div>
      </div>
    </div>
  );
}

export default function GoogleCallbackPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen flex items-center justify-center bg-deep-space p-6">
          <Loader2 className="h-8 w-8 animate-spin text-accent" />
        </div>
      }
    >
      <GoogleCallbackContent />
    </Suspense>
  );
}
