// API client for the AssetFlow FastAPI backend.

export const API_BASE_URL =
  (import.meta.env.VITE_API_BASE_URL as string | undefined) ??
  "http://127.0.0.1:8000/api/v1";

export const TOKEN_KEY = "assetflow_auth_token";
const DEFAULT_TIMEOUT_MS = 45_000;
/** Assistant chat may call Ollama after SQL tools — allow headroom beyond default. */
export const ASSISTANT_CHAT_TIMEOUT_MS = 90_000;

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string | null) {
  if (typeof window === "undefined") return;
  if (token) window.localStorage.setItem(TOKEN_KEY, token);
  else window.localStorage.removeItem(TOKEN_KEY);
}

export class ApiError extends Error {
  status: number;
  data: unknown;
  constructor(message: string, status: number, data: unknown) {
    super(message);
    this.status = status;
    this.data = data;
  }
}

type Options = {
  method?: string;
  body?: unknown;
  query?: Record<string, string | number | boolean | undefined | null>;
  headers?: Record<string, string>;
  signal?: AbortSignal;
  timeoutMs?: number;
};

export function buildQueryString(params: Record<string, unknown>): string {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== "") {
      search.set(key, String(value));
    }
  }
  const qs = search.toString();
  return qs ? `?${qs}` : "";
}

function buildRequestUrl(path: string): URL {
  const target = path.startsWith("http")
    ? path
    : `${API_BASE_URL}${path.startsWith("/") ? "" : "/"}${path}`;
  if (target.startsWith("http")) return new URL(target);
  const base = typeof window !== "undefined" ? window.location.origin : "http://localhost";
  return new URL(target, base);
}

async function request<T>(path: string, opts: Options = {}): Promise<T> {
  const timeoutMs = opts.timeoutMs ?? DEFAULT_TIMEOUT_MS;
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs);

  const url = buildRequestUrl(path);
  if (opts.query) {
    for (const [k, v] of Object.entries(opts.query)) {
      if (v !== undefined && v !== null && v !== "") url.searchParams.set(k, String(v));
    }
  }

  const headers: Record<string, string> = {
    Accept: "application/json",
    ...(opts.headers ?? {}),
  };
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;

  let body: BodyInit | undefined;
  if (opts.body !== undefined) {
    if (opts.body instanceof FormData) {
      body = opts.body;
    } else {
      headers["Content-Type"] = "application/json";
      body = JSON.stringify(opts.body);
    }
  }

  try {
    const res = await fetch(url.toString(), {
      method: opts.method ?? (opts.body ? "POST" : "GET"),
      headers,
      body,
      signal: opts.signal ?? controller.signal,
    });
    const text = await res.text();
    let data: unknown = null;
    if (text) {
      try {
        data = JSON.parse(text);
      } catch {
        data = text;
      }
    }
    if (!res.ok) {
      const detail =
        (data && typeof data === "object" && "detail" in data
          ? formatDetail((data as { detail?: unknown }).detail)
          : "") || res.statusText;
      throw new ApiError(detail || `Request failed (${res.status})`, res.status, data);
    }
    if (res.status === 204) return undefined as T;
    return data as T;
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new Error("Request timed out. The server may be busy — please try again.");
    }
    if (error instanceof TypeError) {
      throw new Error("Unable to reach the API. Check that the backend is running.");
    }
    throw error;
  } finally {
    clearTimeout(timeout);
  }
}

function formatDetail(detail: unknown): string {
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((item) =>
        item && typeof item === "object" && "msg" in item
          ? String((item as { msg?: string }).msg ?? "Validation error")
          : "Validation error",
      )
      .join(", ");
  }
  return "";
}

export function api<T = unknown>(path: string, opts: Options = {}): Promise<T> {
  return request<T>(path, opts);
}

export function apiGet<T>(path: string, timeoutMs?: number): Promise<T> {
  return request<T>(path, { timeoutMs });
}

export function apiPost<T>(path: string, body: unknown, timeoutMs?: number): Promise<T> {
  return request<T>(path, { method: "POST", body, timeoutMs });
}

export function apiPatch<T>(path: string, body: unknown): Promise<T> {
  return request<T>(path, { method: "PATCH", body });
}

export function apiDelete<T>(path: string): Promise<T> {
  return request<T>(path, { method: "DELETE" });
}
