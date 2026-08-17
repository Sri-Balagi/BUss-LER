/**
 * BizOS Frontend API Client
 * Provides typed API wrappers for auth, connectors, and core BizOS backend calls.
 * Method names are matched exactly to what auth-context.tsx expects.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class BizOSAPIError extends Error {
  constructor(
    public status: number,
    public detail: string,
    message?: string
  ) {
    super(message || detail);
    this.name = "BizOSAPIError";
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const token =
    typeof window !== "undefined"
      ? localStorage.getItem("bizos_session_token")
      : null;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || body.message || detail;
    } catch {}
    throw new BizOSAPIError(res.status, detail);
  }

  if (res.status === 204) return undefined as T;
  return res.json();
}

// ─── Auth API ─────────────────────────────────────────────────────────────────
// Method names must match exactly what lib/auth-context.tsx calls

export const authAPI = {
  /** Called as authAPI.register(name, email, password) */
  register: (name: string, email: string, password: string) =>
    request<{ user_id: string; token?: string; user?: any; message?: string }>(
      "/api/v1/auth/signup",
      { method: "POST", body: JSON.stringify({ name, email, password }) }
    ),

  /** Called as authAPI.login(email, password) */
  login: (email: string, password: string) =>
    request<{ user_id: string; token?: string; access_token?: string; user?: any }>(
      "/api/v1/auth/signin",
      { method: "POST", body: JSON.stringify({ email, password }) }
    ),

  /** Called as authAPI.logout() */
  logout: () =>
    request<void>("/api/v1/auth/signout", { method: "POST" }),

  /** Called as authAPI.forgotPassword(email) */
  forgotPassword: (email: string) =>
    request<{ sent?: boolean; message?: string }>("/api/v1/auth/forgot-password", {
      method: "POST",
      body: JSON.stringify({ email }),
    }),

  /** Called as authAPI.verifyEmail(code) */
  verifyEmail: (code: string) =>
    request<{ verified?: boolean; message?: string }>("/api/v1/auth/verify-email", {
      method: "POST",
      body: JSON.stringify({ code }),
    }),

  /** Called as authAPI.sendVerificationEmail(email) */
  sendVerificationEmail: (email: string) =>
    request<{ message?: string }>("/api/v1/auth/send-verification-email", {
      method: "POST",
      body: JSON.stringify({ email }),
    }),

  me: () => request<any>("/api/v1/auth/me"),

  oauthUrl: (provider: string) =>
    request<{ url: string }>(`/api/v1/auth/oauth/${provider}`),
};

// ─── Connectors API ───────────────────────────────────────────────────────────

export const connectorsAPI = {
  list: () => request<any[]>("/api/v1/connectors"),

  /** Called as connectorsAPI.authenticate(provider, { user_email, tenant_id, account_id }) */
  authenticate: (connectorId: string, config: Record<string, any>) =>
    request<{ auth_url?: string; status?: string }>(`/api/v1/connectors/${connectorId}/authenticate`, {
      method: "POST",
      body: JSON.stringify(config),
    }),

  connect: (connectorId: string, config: Record<string, any>) =>
    request<any>(`/api/v1/connectors/${connectorId}/connect`, {
      method: "POST",
      body: JSON.stringify(config),
    }),

  disconnect: (connectorId: string) =>
    request<void>(`/api/v1/connectors/${connectorId}/disconnect`, {
      method: "DELETE",
    }),

  status: (connectorId: string) =>
    request<any>(`/api/v1/connectors/${connectorId}/status`),
};

// ─── Runtime API ──────────────────────────────────────────────────────────────

export const runtimeAPI = {
  status: () => request<any>("/api/v1/runtime/status"),
  health: () => request<any>("/api/v1/runtime/health"),
};

// ─── Knowledge API ────────────────────────────────────────────────────────────

export const knowledgeAPI = {
  graph: () => request<any>("/api/v1/knowledge/graph"),
  search: (query: string) =>
    request<any>(`/api/v1/knowledge/search?q=${encodeURIComponent(query)}`),
};
