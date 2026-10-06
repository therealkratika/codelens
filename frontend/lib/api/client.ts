import { API_BASE_URL } from "@/lib/config/env";

interface RequestOptions extends RequestInit {
  timeoutMs?: number;
}

interface ErrorPayload {
  detail?: unknown;
  message?: unknown;
}

export class ApiError extends Error {
  readonly status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

export class ApiTimeoutError extends Error {
  constructor() {
    super("The request took too long to complete.");
    this.name = "ApiTimeoutError";
  }
}

async function request<T>(
  path: string,
  options: RequestOptions = {},
): Promise<T> {
  const { timeoutMs = 30_000, ...fetchOptions } = options;
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      ...fetchOptions,
      headers: {
        Accept: "application/json",
        ...fetchOptions.headers,
      },
      signal: controller.signal,
    });

    const responseText = await response.text();
    let payload: unknown = null;

    if (responseText) {
      try {
        payload = JSON.parse(responseText) as unknown;
      } catch {
        if (response.ok) {
          throw new ApiError(
            response.status,
            "The server returned an unreadable response.",
          );
        }
      }
    }

    if (!response.ok) {
      const errorPayload =
        payload && typeof payload === "object"
          ? (payload as ErrorPayload)
          : {};
      const detail =
        typeof errorPayload.detail === "string"
          ? errorPayload.detail
          : typeof errorPayload.message === "string"
            ? errorPayload.message
            : "The request could not be completed.";

      throw new ApiError(response.status, detail);
    }

    return payload as T;
  } catch (error) {
    if (controller.signal.aborted) {
      throw new ApiTimeoutError();
    }
    throw error;
  } finally {
    window.clearTimeout(timeout);
  }
}

export const apiClient = {
  get<T>(path: string, timeoutMs?: number): Promise<T> {
    return request<T>(path, { method: "GET", timeoutMs });
  },

  post<T, Body>(path: string, body: Body, timeoutMs?: number): Promise<T> {
    return request<T>(path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      timeoutMs,
    });
  },
};
