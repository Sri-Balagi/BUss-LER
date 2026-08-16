export class BizOSAPIError extends Error {
  status: number;
  detail: string;

  constructor(message: string, status = 400, detail?: string) {
    super(message);
    this.name = "BizOSAPIError";
    this.status = status;
    this.detail = detail || message;
  }
}

export const authAPI = {
  me: async () => {
    return {
      id: "usr_101",
      name: "Sri Balagi",
      email: "rsribalagi@gmail.com",
      verified: true,
    };
  },
  login: async (email: string, password?: string) => {
    return {
      user_id: "usr_101",
      token: "tok_bizos_session_secure_2026",
      user: {
        id: "usr_101",
        name: email.includes("porselvi") ? "Porselvi Uthirakumaran" : "Sri Balagi",
        email: email,
        verified: true,
      },
    };
  },
  register: async (name: string, email: string, password?: string) => {
    return {
      user_id: "usr_101",
      token: "tok_bizos_session_secure_2026",
      user: {
        id: "usr_101",
        name: name || "Sri Balagi",
        email: email || "rsribalagi@gmail.com",
        verified: true,
      },
    };
  },
  verifyEmail: async (code: string) => {
    return { verified: true };
  },
  forgotPassword: async (email: string) => {
    return { sent: true };
  },
  logout: async () => {
    return { success: true };
  },
};

export const connectorsAPI = {
  authenticate: async (provider: string, payload: any) => {
    return { auth_url: "/app/memory", redirect_url: "/app/memory" };
  },
};

export const onboardingAPI = {
  saveBusinessInfo: async (payload: any) => {
    return { success: true };
  },
  saveModules: async (modules: string[]) => {
    return { success: true };
  },
  savePreferences: async (payload: any) => {
    return { success: true };
  },
  complete: async (payload: any) => {
    return { success: true };
  },
};
