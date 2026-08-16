"use client";

import React, { useState, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { ArrowRight, CheckCircle2, Loader2, Mail, RefreshCw, KeyRound, Sparkles } from "lucide-react";

export default function VerifyEmailPage() {
  const router = useRouter();
  const { user, pendingEmail, activeOtpCode, verifyEmail, sendOtpCode } = useAuth();

  const [otp, setOtp] = useState(["", "", "", "", "", ""]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [successMsg, setSuccessMsg] = useState("");
  const [resendTimer, setResendTimer] = useState(30);

  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

  const targetEmail = pendingEmail || user?.email || "rsribalagi@gmail.com";
  const displayCode = activeOtpCode || "849201";

  useEffect(() => {
    if (resendTimer > 0) {
      const timer = setTimeout(() => setResendTimer((t) => t - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [resendTimer]);

  const handleChange = (index: number, value: string) => {
    if (!/^\d*$/.test(value)) return;

    const newOtp = [...otp];
    newOtp[index] = value.slice(-1);
    setOtp(newOtp);

    if (value && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handleKeyDown = (index: number, e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Backspace" && !otp[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  };

  const handlePaste = (e: React.ClipboardEvent) => {
    e.preventDefault();
    const pasteData = e.clipboardData.getData("text").trim();
    if (/^\d{6}$/.test(pasteData)) {
      const digits = pasteData.split("");
      setOtp(digits);
      inputRefs.current[5]?.focus();
    }
  };

  const handleQuickFill = () => {
    setOtp(displayCode.split(""));
    inputRefs.current[5]?.focus();
  };

  const handleVerify = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const code = otp.join("");
    if (code.length < 6) {
      setError("Please enter the complete 6-digit verification code.");
      return;
    }
    setError("");
    setLoading(true);
    try {
      const success = await verifyEmail(code);
      if (success) {
        const isBalagi = targetEmail.toLowerCase().trim() === "rsribalagi@gmail.com";
        setSuccessMsg(
          isBalagi
            ? "Verification Successful! Accessing Hotel Balagi Bhavan Workspace..."
            : "Verification Successful! Redirecting to Business Details Setup..."
        );
        setTimeout(() => {
          router.push(isBalagi ? "/dashboard" : "/onboarding");
        }, 800);
      } else {
        setError(`Invalid verification code. Use code ${displayCode} or click Quick Fill.`);
      }
    } catch (err: any) {
      setError(err?.message || "Verification failed.");
    } finally {
      setLoading(false);
    }
  };

  const handleResend = () => {
    if (resendTimer > 0) return;
    sendOtpCode(targetEmail);
    setResendTimer(30);
    setOtp(["", "", "", "", "", ""]);
    setError("");
    setSuccessMsg("A new verification code has been dispatched to your email!");
    setTimeout(() => setSuccessMsg(""), 3000);
  };

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col items-center text-center">
        <div className="mb-3 flex h-14 w-14 items-center justify-center rounded-2xl border border-accent/20 bg-accent/10 text-accent shadow-lg shadow-accent/10">
          <Mail className="h-7 w-7" />
        </div>
        <h1 className="font-display text-2xl font-semibold tracking-tight text-primary">
          Check your email
        </h1>
        <p className="mt-1.5 text-xs text-secondary max-w-xs leading-relaxed">
          We sent a 6-digit verification code to{" "}
          <strong className="text-primary font-medium">{targetEmail}</strong>
        </p>
      </div>

      {/* Live Verification Code Banner */}
      <div className="rounded-xl border border-accent/30 bg-accent/10 p-3.5 flex items-center justify-between text-xs text-primary shadow-sm">
        <div className="flex items-center gap-2.5">
          <KeyRound className="h-4 w-4 text-accent shrink-0" />
          <div>
            <span className="text-tertiary block text-[10px]">Verification Code Sent:</span>
            <span className="font-mono text-sm font-bold text-accent tracking-widest">{displayCode}</span>
          </div>
        </div>
        <button
          type="button"
          onClick={handleQuickFill}
          className="flex items-center gap-1 px-2.5 py-1 rounded-lg bg-accent/20 hover:bg-accent/30 text-accent text-[11px] font-medium transition-colors border border-accent/30"
        >
          <Sparkles className="h-3 w-3" />
          <span>Auto Fill</span>
        </button>
      </div>

      {error && (
        <div className="rounded-xl border border-red-500/20 bg-red-500/10 p-3 text-xs text-red-400 text-center">
          {error}
        </div>
      )}

      {successMsg && (
        <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/10 p-3 text-xs text-emerald-400 text-center flex items-center justify-center gap-2">
          <CheckCircle2 className="h-4 w-4 shrink-0" />
          <span>{successMsg}</span>
        </div>
      )}

      <form onSubmit={handleVerify} className="flex flex-col gap-6">
        {/* OTP Input Fields */}
        <div className="flex justify-center gap-2" onPaste={handlePaste}>
          {otp.map((digit, idx) => (
            <input
              key={idx}
              ref={(el) => {
                inputRefs.current[idx] = el;
              }}
              type="text"
              inputMode="numeric"
              maxLength={1}
              value={digit}
              onChange={(e) => handleChange(idx, e.target.value)}
              onKeyDown={(e) => handleKeyDown(idx, e)}
              className="h-12 w-11 rounded-xl border border-white/10 bg-white/[0.04] text-center font-mono text-lg font-bold text-primary focus:border-accent focus:bg-white/[0.08] focus:outline-none transition-all shadow-inner"
            />
          ))}
        </div>

        {/* Submit */}
        <button
          type="submit"
          disabled={loading || otp.join("").length < 6}
          className="flex h-11 w-full items-center justify-center gap-2 rounded-xl bg-accent text-sm font-semibold text-white transition-all hover:bg-accent-hover active:scale-[0.99] disabled:opacity-50 shadow-md shadow-accent/20"
        >
          {loading ? (
            <Loader2 className="h-4 w-4 animate-spin text-white" />
          ) : (
            <>
              <span>Verify & Continue</span>
              <ArrowRight className="h-4 w-4" />
            </>
          )}
        </button>
      </form>

      {/* Resend Code */}
      <div className="flex items-center justify-between text-xs text-secondary pt-2 border-t border-white/10">
        <span>Didn&apos;t receive code?</span>
        <button
          type="button"
          onClick={handleResend}
          disabled={resendTimer > 0}
          className="flex items-center gap-1.5 font-medium text-accent hover:underline disabled:opacity-50 disabled:no-underline"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${resendTimer > 0 ? "animate-spin" : ""}`} />
          <span>{resendTimer > 0 ? `Resend in ${resendTimer}s` : "Resend Code"}</span>
        </button>
      </div>
    </div>
  );
}
