const API_BASE_URL = (
  import.meta.env.VITE_API_URL || ""
).replace(/\/+$/, "");

const API_TIMEOUT_MS = Number(
  import.meta.env.VITE_API_TIMEOUT_MS || 120000,
);

export async function apiRequest(endpoint, options = {}) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), API_TIMEOUT_MS);

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      signal: controller.signal,
      headers: {
        ...(options.body && !(options.body instanceof FormData)
          ? { "Content-Type": "application/json" }
          : {}),
        ...options.headers,
      },
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      const detail = data.detail || data.error || data.message;
      const error = new Error(
        typeof detail === "string"
          ? detail
          : `Request failed (${response.status})`,
      );
      error.status = response.status;
      throw error;
    }
    return data;
  } catch (error) {
    if (error.name === "AbortError") {
      throw new Error(
        "The backend took too long to respond. Check that the deployed API is running.",
      );
    }
    throw error;
  } finally {
    clearTimeout(timeout);
  }
}
