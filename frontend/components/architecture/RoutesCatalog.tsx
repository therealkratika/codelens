"use client";

import { useState, useMemo } from "react";
import {
  ExternalLink,
  MessageSquareCode,
  Search,
} from "lucide-react";
import type { FeatureFlow } from "@/types/architecture";
import {
  getFileLocationText,
  getFlowMethod,
  getHandlerName,
  getMethodBadgeClass,
  getRoutePath,
} from "@/lib/architecture";

interface RoutesCatalogProps {
  flows: FeatureFlow[];
  onAskAboutRoute: (flow: FeatureFlow) => void;
  onOpenFile: (file: string, line?: number) => void;
}

export function RoutesCatalog({
  flows,
  onAskAboutRoute,
  onOpenFile,
}: RoutesCatalogProps) {
  const [methodFilter, setMethodFilter] = useState<string>("ALL");
  const [searchQuery, setSearchQuery] = useState("");

  const filteredRoutes = useMemo(() => {
    return flows.filter((flow) => {
      const method = getFlowMethod(flow);
      const path = getRoutePath(flow);
      const handler = getHandlerName(flow);

      if (methodFilter !== "ALL" && method !== methodFilter) {
        return false;
      }

      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        return (
          path.toLowerCase().includes(q) ||
          handler.toLowerCase().includes(q) ||
          (flow.controller?.controller_file || "").toLowerCase().includes(q) ||
          (flow.route?.route_file || "").toLowerCase().includes(q)
        );
      }

      return true;
    });
  }, [flows, methodFilter, searchQuery]);

  return (
    <div className="routes-catalog-container">
      {/* Search & Filter Toolbar */}
      <div className="routes-toolbar">
        <div className="routes-filter-methods">
          {["ALL", "GET", "POST", "PUT", "DELETE"].map((m) => (
            <button
              key={m}
              type="button"
              className={`method-filter-btn ${methodFilter === m ? "is-active" : ""}`}
              onClick={() => setMethodFilter(m)}
            >
              {m}
            </button>
          ))}
        </div>

        <div className="routes-search">
          <Search className="w-4 h-4 search-icon" />
          <input
            type="text"
            className="routes-search-input"
            placeholder="Search route path, handler, controller..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        <div className="routes-count-badge">
          {filteredRoutes.length} {filteredRoutes.length === 1 ? "route" : "routes"} found
        </div>
      </div>

      {/* Routes Table */}
      <div className="routes-table-wrapper">
        <table className="routes-table">
          <thead>
            <tr>
              <th>Method</th>
              <th>Endpoint Path</th>
              <th>Handler</th>
              <th>Route Definition</th>
              <th>Controller</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredRoutes.length === 0 ? (
              <tr>
                <td colSpan={6} className="routes-empty-td">
                  No API endpoints matching criteria.
                </td>
              </tr>
            ) : (
              filteredRoutes.map((flow) => {
                const method = getFlowMethod(flow);
                const methodClass = getMethodBadgeClass(method);
                const routeLocation = flow.route
                  ? getFileLocationText(flow.route.route_file, flow.route.route_line)
                  : null;
                const controllerLocation = flow.controller
                  ? getFileLocationText(
                      flow.controller.controller_file,
                      flow.controller.controller_start_line,
                    )
                  : null;

                return (
                  <tr key={flow.id} className="route-row">
                    <td>
                      <span className={`method-badge ${methodClass}`}>
                        {method}
                      </span>
                    </td>
                    <td>
                      <code className="route-path-cell">{getRoutePath(flow)}</code>
                    </td>
                    <td>
                      <span className="handler-name">{getHandlerName(flow)}()</span>
                    </td>
                    <td>
                      {flow.route ? (
                        <button
                          type="button"
                          className="table-link-btn"
                          onClick={() =>
                            onOpenFile(flow.route!.route_file, flow.route!.route_line)
                          }
                          title="Open route file"
                        >
                          <span>{flow.route.route_file.split("/").pop()}</span>
                          <span className="line-tag">:{routeLocation?.split(":").at(-1)}</span>
                          <ExternalLink className="w-3 h-3 ml-1" />
                        </button>
                      ) : (
                        <span className="text-muted text-xs">&mdash;</span>
                      )}
                    </td>
                    <td>
                      {flow.controller ? (
                        <button
                          type="button"
                          className="table-link-btn"
                          onClick={() =>
                            onOpenFile(
                              flow.controller!.controller_file,
                              flow.controller!.controller_start_line,
                            )
                          }
                          title="Open controller file"
                        >
                          <span>
                            {flow.controller.controller_file.split("/").pop()}
                          </span>
                          <span className="line-tag">:{controllerLocation?.split(":").at(-1)}</span>
                          <ExternalLink className="w-3 h-3 ml-1" />
                        </button>
                      ) : (
                        <span className="text-muted text-xs">Unresolved</span>
                      )}
                    </td>
                    <td>
                      <div className="route-row-actions">
                        <button
                          type="button"
                          className="btn-icon-ask"
                          onClick={() => onAskAboutRoute(flow)}
                          title={`Ask CodeLens about ${flow.name}`}
                        >
                          <MessageSquareCode className="w-4 h-4" />
                          <span>Ask AI</span>
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
