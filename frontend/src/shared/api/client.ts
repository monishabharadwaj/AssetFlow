const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000/api/v1";
const REQUEST_TIMEOUT_MS = 45_000;

async function parseErrorMessage(response: Response): Promise<string> {
  const text = await response.text();
  if (!text) {
    return `Request failed with status ${response.status}`;
  }

  try {
    const json = JSON.parse(text) as { detail?: string | Array<{ msg?: string }> };
    if (typeof json.detail === "string") {
      return json.detail;
    }
    if (Array.isArray(json.detail)) {
      return json.detail.map((item) => item.msg ?? "Validation error").join(", ");
    }
  } catch {
    // fall through to raw text
  }

  return text;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      headers: { "Content-Type": "application/json", ...init?.headers },
      ...init,
      signal: init?.signal ?? controller.signal,
    });
    if (!response.ok) {
      throw new Error(await parseErrorMessage(response));
    }
    if (response.status === 204) {
      return undefined as T;
    }
    return (await response.json()) as T;
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

export function apiGet<T>(path: string): Promise<T> {
  return request<T>(path);
}

export function apiPost<T>(path: string, body: unknown): Promise<T> {
  return request<T>(path, { method: "POST", body: JSON.stringify(body) });
}

export function apiPatch<T>(path: string, body: unknown): Promise<T> {
  return request<T>(path, { method: "PATCH", body: JSON.stringify(body) });
}

export function apiDelete<T>(path: string): Promise<T> {
  return request<T>(path, { method: "DELETE" });
}

export { API_BASE_URL };
