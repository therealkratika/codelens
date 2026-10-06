import { ApiError, ApiTimeoutError } from "@/lib/api/client";

export type ErrorContext = "status" | "import" | "activate" | "chat";

export function getUserError(
  error: unknown,
  context: ErrorContext,
): string {
  if (error instanceof ApiTimeoutError) {
    return context === "import"
      ? "Repository indexing is taking longer than expected. Check the server status and try again."
      : "The request took too long. Please try again.";
  }

  if (error instanceof ApiError) {
    if (context === "status") {
      return "Unable to connect to CodeLens. Make sure the backend is running, then try again.";
    }

    if (context === "import") {
      if (error.status === 400 || error.status === 422) {
        return error.message;
      }
      return error.message || "Unable to import this repository.";
    }

    if (context === "activate") {
      return "Unable to switch to that repository. It may have been removed; try importing it again.";
    }

    if (error.status === 400 || error.status === 404) {
      return "No repository is ready for chat. Import a repository and try again.";
    }
    return "CodeLens could not answer that question. Please try again.";
  }

  return context === "status"
    ? "Unable to connect to CodeLens. Make sure the backend is running, then try again."
    : context === "import"
      ? "Unable to import this repository. Check the GitHub URL and try again."
      : context === "activate"
        ? "Unable to switch repositories. Please try again."
      : "CodeLens could not answer that question. Check your connection and try again.";
}

export function isGitHubRepositoryUrl(value: string): boolean {
  try {
    const url = new URL(value);
    const segments = url.pathname.split("/").filter(Boolean);

    return (
      (url.protocol === "https:" || url.protocol === "http:") &&
      url.hostname.toLowerCase() === "github.com" &&
      segments.length === 2 &&
      segments.every((segment) => segment !== "." && segment !== "..")
    );
  } catch {
    return false;
  }
}
