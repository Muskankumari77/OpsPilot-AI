import { getActiveOrgId, getToken } from "./auth";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

interface RequestOptions extends RequestInit {
  auth?: boolean; // attach Authorization + X-Organization-Id headers (default true)
}

export async function apiFetch<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { auth = true, headers, ...rest } = options;

  const isFormData = rest.body instanceof FormData;

  const finalHeaders: HeadersInit = {
    // FormData sets its own multipart boundary header — letting the browser
    // do that (by omitting Content-Type here) is required for file uploads.
    ...(isFormData ? {} : { "Content-Type": "application/json" }),
    ...headers,
  };

  if (auth) {
    const token = getToken();
    if (token) {
      (finalHeaders as Record<string, string>).Authorization = `Bearer ${token}`;
    }
    const orgId = getActiveOrgId();
    if (orgId) {
      (finalHeaders as Record<string, string>)["X-Organization-Id"] = String(orgId);
    }
  }

  const res = await fetch(`${API_URL}${path}`, { ...rest, headers: finalHeaders });

  if (!res.ok) {
    let message = `Request failed with status ${res.status}`;
    try {
      const body = await res.json();
      message = body?.error?.message ?? body?.detail ?? message;
    } catch {
      // response wasn't JSON — keep the default message
    }
    throw new ApiError(message, res.status);
  }

  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}
