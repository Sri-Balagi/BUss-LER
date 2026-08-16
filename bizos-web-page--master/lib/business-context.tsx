"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { useAuth } from "./auth-context";

export interface AccountProfile {
  email: string;
  businessName: string;
  isPrimaryHardcoded: boolean;
  contactEmail: string;
  contactPhone: string;
  statusMessage: string;
}

const PRIMARY_EMAIL = "rsribalagi@gmail.com";

export const ACCOUNT_PROFILES: Record<string, AccountProfile> = {
  [PRIMARY_EMAIL]: {
    email: PRIMARY_EMAIL,
    businessName: "Hotel Balagi Bhavan",
    isPrimaryHardcoded: true,
    contactEmail: "rsribalagi@gmail.com",
    contactPhone: "+91 98765 43210",
    statusMessage: "Active Enterprise Knowledge Graph & Digital Twin",
  },
};

const DEFAULT_NEW_ACCOUNT_PROFILE: AccountProfile = {
  email: "",
  businessName: "Custom Business (Pending Setup)",
  isPrimaryHardcoded: false,
  contactEmail: "rsribalagi@gmail.com",
  contactPhone: "+91 98765 43210",
  statusMessage: "Enterprise Knowledge Graph Setup Pending",
};

interface BusinessContextType {
  profile: AccountProfile;
  isPrimaryAccount: boolean;
  requestOnboardingCall: () => void;
  callRequested: boolean;
}

const BusinessContext = createContext<BusinessContextType | undefined>(undefined);

export function BusinessProvider({ children }: { children: React.ReactNode }) {
  const { user } = useAuth();
  const [callRequested, setCallRequested] = useState(false);

  const email = user?.email || "";
  const isPrimaryAccount = email.toLowerCase().trim() === PRIMARY_EMAIL.toLowerCase().trim();

  const profile: AccountProfile = isPrimaryAccount
    ? ACCOUNT_PROFILES[PRIMARY_EMAIL]
    : {
        ...DEFAULT_NEW_ACCOUNT_PROFILE,
        email: email,
        businessName: user?.name ? `${user.name}'s Business` : "Your Business",
      };

  const requestOnboardingCall = () => {
    setCallRequested(true);
  };

  return (
    <BusinessContext.Provider
      value={{
        profile,
        isPrimaryAccount,
        requestOnboardingCall,
        callRequested,
      }}
    >
      {children}
    </BusinessContext.Provider>
  );
}

export function useBusiness() {
  const ctx = useContext(BusinessContext);
  if (!ctx) {
    return {
      profile: {
        email: "rsribalagi@gmail.com",
        businessName: "Hotel Balagi Bhavan",
        isPrimaryHardcoded: true,
        contactEmail: "rsribalagi@gmail.com",
        contactPhone: "+91 98765 43210",
        statusMessage: "Active Enterprise Knowledge Graph & Digital Twin",
      },
      isPrimaryAccount: true,
      requestOnboardingCall: () => {},
      callRequested: false,
    };
  }
  return ctx;
}
