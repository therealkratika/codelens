import type { FeatureFlow } from "@/types/architecture";

export function getMethodBadgeClass(method?: string | null): string {
  switch (method) {
    case "GET":
      return "badge-get";
    case "POST":
      return "badge-post";
    case "DELETE":
      return "badge-delete";
    case "PUT":
      return "badge-put";
    default:
      return "badge-post";
  }
}

export function getFlowMethod(flow: Pick<FeatureFlow, "route" | "frontend_api">): string {
  return flow.route?.method || flow.frontend_api?.method || "POST";
}

export function getRoutePath(flow: Pick<FeatureFlow, "route" | "frontend_api">): string {
  return flow.route?.path || flow.frontend_api?.endpoint || "/";
}

export function getHandlerName(flow: Pick<FeatureFlow, "route" | "name">): string {
  return flow.route?.handler || flow.name;
}

export function getFileLocationText(file?: string, line?: number): string {
  if (!file) return "Unknown";
  if (typeof line !== "number") return file;
  return `${file}:${line}`;
}
