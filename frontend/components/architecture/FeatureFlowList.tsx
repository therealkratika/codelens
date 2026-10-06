"use client";

import { CheckCircle2, ChevronRight, Search } from "lucide-react";
import type { FeatureFlow } from "@/types/architecture";

interface FeatureFlowListProps {
  flows: FeatureFlow[];
  selectedFlowId: string | null;
  searchQuery: string;
  onSearchChange: (query: string) => void;
  onSelectFlow: (id: string) => void;
}

export function FeatureFlowList({
  flows,
  selectedFlowId,
  searchQuery,
  onSearchChange,
  onSelectFlow,
}: FeatureFlowListProps) {
  return (
    <div className="flow-list-container">
      <div className="flow-list-header">
        <div className="flow-search-box">
          <Search className="w-4 h-4 search-icon" />
          <input
            type="text"
            className="flow-search-input"
            placeholder="Filter feature flows..."
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
          />
        </div>
        <div className="flow-count-tag">
          {flows.length} {flows.length === 1 ? "flow" : "flows"}
        </div>
      </div>

      <div className="flow-list-items">
        {flows.length === 0 ? (
          <div className="flow-list-empty">
            <p>No feature flows matching &ldquo;{searchQuery}&rdquo;</p>
          </div>
        ) : (
          flows.map((flow) => {
            const isSelected = flow.id === selectedFlowId;
            const method = flow.frontend_api?.method || flow.route?.method || "POST";
            const methodClass =
              method === "GET"
                ? "badge-get"
                : method === "POST"
                  ? "badge-post"
                  : method === "DELETE"
                    ? "badge-delete"
                    : "badge-put";

            return (
              <button
                key={flow.id}
                type="button"
                className={`flow-list-item ${isSelected ? "is-selected" : ""}`}
                onClick={() => onSelectFlow(flow.id)}
              >
                <div className="flow-item-main">
                  <div className="flow-item-row">
                    <span className={`flow-method-tag ${methodClass}`}>{method}</span>
                    <span className="flow-item-name">{flow.name}()</span>
                  </div>
                  <div className="flow-item-sub">
                    <span className="flow-endpoint">
                      {flow.route?.path || flow.frontend_api?.endpoint || "/"}
                    </span>
                    {flow.controller && (
                      <span className="flow-controller-badge" title="Resolved Controller">
                        <CheckCircle2 className="w-3 h-3 text-emerald-500" />
                        <span>Controller</span>
                      </span>
                    )}
                  </div>
                </div>
                <ChevronRight className="w-4 h-4 flow-chevron" />
              </button>
            );
          })
        )}
      </div>
    </div>
  );
}
