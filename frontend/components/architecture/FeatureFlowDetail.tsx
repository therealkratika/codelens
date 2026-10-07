"use client";

import {
  ArrowRight,
  Code2,
  ExternalLink,
  Layers,
  MessageSquareCode,
  Network,
  Server,
  Zap,
} from "lucide-react";
import type { FeatureFlow } from "@/types/architecture";
import {
  getFileLocationText,
  getFlowMethod,
  getMethodBadgeClass,
  getRoutePath,
} from "@/lib/architecture";

interface FeatureFlowDetailProps {
  flow: FeatureFlow | null;
  onAskAboutFlow: (flow: FeatureFlow) => void;
  onOpenFile: (file: string, line?: number) => void;
}

export function FeatureFlowDetail({
  flow,
  onAskAboutFlow,
  onOpenFile,
}: FeatureFlowDetailProps) {
  if (!flow) {
    return (
      <div className="flow-empty-detail">
        <Network className="w-10 h-10 text-muted opacity-50 mb-3" />
        <h3>Select a Feature Flow</h3>
        <p>Pick any traced endpoint on the left to inspect its end-to-end execution path.</p>
      </div>
    );
  }

  const method = getFlowMethod(flow);
  const methodColor = getMethodBadgeClass(method);

  return (
    <div className="flow-detail-container">
      {/* Header */}
      <div className="flow-detail-header">
        <div className="flow-header-left">
          <div className="flex items-center gap-2">
            <span className={`method-badge ${methodColor}`}>{method}</span>
            <h2 className="flow-title">{flow.name}()</h2>
          </div>
          <p className="flow-description">
            {flow.description || `End-to-end trace for ${flow.name} across frontend, router, controller, and models.`}
          </p>
        </div>

        <div className="flow-header-actions">
          <button
            type="button"
            className="btn-action-primary"
            onClick={() => onAskAboutFlow(flow)}
            title="Ask CodeLens AI about this feature flow"
          >
            <MessageSquareCode className="w-4 h-4" />
            <span>Ask CodeLens</span>
          </button>
        </div>
      </div>

      {/* Visual Pipeline Flow */}
      <div className="flow-pipeline-timeline">
        {/* Step 1: Frontend API */}
        <div className="flow-step-card">
          <div className="step-marker-container">
            <div className="step-icon-badge step-icon-frontend">
              <Code2 className="w-4 h-4" />
            </div>
            <div className="step-line" />
          </div>
          <div className="step-body">
            <div className="step-header">
              <span className="step-phase-tag">Phase 1 &bull; Client</span>
              <span className="step-title">Frontend API Client</span>
            </div>
            {flow.frontend_api ? (
              <div className="step-content">
                <div className="step-symbol-row">
                  <code>{flow.frontend_api.function}()</code>
                  <button
                    type="button"
                    className="step-file-link"
                    onClick={() =>
                      onOpenFile(flow.frontend_api!.file, flow.frontend_api!.line)
                    }
                  >
                    <span>{getFileLocationText(flow.frontend_api.file, flow.frontend_api.line)}</span>
                    <ExternalLink className="w-3 h-3 ml-1" />
                  </button>
                </div>
                <div className="step-code-preview">
                  <span className="code-meta">Target:</span>
                  <code className="endpoint-code">{flow.frontend_api.resolved_endpoint}</code>
                </div>
              </div>
            ) : (
              <p className="step-unresolved">Not directly invoked via frontend client.</p>
            )}
          </div>
        </div>

        {/* Step 2: HTTP Transport */}
        <div className="flow-step-card">
          <div className="step-marker-container">
            <div className="step-icon-badge step-icon-http">
              <Zap className="w-4 h-4" />
            </div>
            <div className="step-line" />
          </div>
          <div className="step-body">
            <div className="step-header">
              <span className="step-phase-tag">Phase 2 &bull; Transport</span>
              <span className="step-title">HTTP Request Protocol</span>
            </div>
            <div className="step-content">
              <div className="http-spec-box">
                <span className={`method-badge ${methodColor}`}>{method}</span>
                <span className="http-route-path">{getRoutePath(flow)}</span>
                {flow.route?.mount_file && (
                  <span className="mount-tag">
                    Mounted in <code>{flow.route.mount_file}</code>
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Step 3: Backend Router */}
        <div className="flow-step-card">
          <div className="step-marker-container">
            <div className="step-icon-badge step-icon-router">
              <Server className="w-4 h-4" />
            </div>
            <div className="step-line" />
          </div>
          <div className="step-body">
            <div className="step-header">
              <span className="step-phase-tag">Phase 3 &bull; Routing</span>
              <span className="step-title">Express Route Handler</span>
            </div>
            {flow.route ? (
              <div className="step-content">
                <div className="step-symbol-row">
                  <code>{`router.${flow.route.method.toLowerCase()}("${flow.route.path}")`}</code>
                  <button
                    type="button"
                    className="step-file-link"
                    onClick={() => onOpenFile(flow.route!.route_file, flow.route!.route_line)}
                  >
                    <span>{getFileLocationText(flow.route.route_file, flow.route.route_line)}</span>
                    <ExternalLink className="w-3 h-3 ml-1" />
                  </button>
                </div>
                <div className="step-meta-note">
                  Delegates request dispatch to controller function: <strong>{flow.route.handler}()</strong>
                </div>
              </div>
            ) : (
              <p className="step-unresolved">Route not yet analyzed in backend router.</p>
            )}
          </div>
        </div>

        {/* Step 4: Controller Execution */}
        <div className="flow-step-card">
          <div className="step-marker-container">
            <div className="step-icon-badge step-icon-controller">
              <Layers className="w-4 h-4" />
            </div>
            <div className="step-line" />
          </div>
          <div className="step-body">
            <div className="step-header">
              <span className="step-phase-tag">Phase 4 &bull; Business Logic</span>
              <span className="step-title">Controller Implementation</span>
            </div>
            {flow.controller ? (
              <div className="step-content">
                <div className="step-symbol-row">
                  <code>{flow.controller.controller_function}()</code>
                  <button
                    type="button"
                    className="step-file-link"
                    onClick={() =>
                      onOpenFile(
                        flow.controller!.controller_file,
                        flow.controller!.controller_start_line,
                      )
                    }
                  >
                    <span>
                      {getFileLocationText(
                        flow.controller.controller_file,
                        flow.controller.controller_start_line,
                      )}
                      -{flow.controller.controller_end_line}
                    </span>
                    <ExternalLink className="w-3 h-3 ml-1" />
                  </button>
                </div>
                <div className="step-meta-note">
                  Executes validation, state mutation, and produces HTTP JSON responses.
                </div>
              </div>
            ) : (
              <p className="step-unresolved">Controller handler not found in codebase.</p>
            )}
          </div>
        </div>

        {/* Step 5: Data Models & Dependencies */}
        <div className="flow-step-card last-step">
          <div className="step-marker-container">
            <div className="step-icon-badge step-icon-db">
              <Network className="w-4 h-4" />
            </div>
          </div>
          <div className="step-body">
            <div className="step-header">
              <span className="step-phase-tag">Phase 5 &bull; Persistence</span>
              <span className="step-title">Data Models &amp; Service Dependencies</span>
            </div>
            <div className="step-content">
              {flow.dependencies.length > 0 ? (
                <div className="dependencies-grid">
                  {flow.dependencies.map((dep, idx) => (
                    <div key={`${dep.symbol}-${idx}`} className="dep-pill">
                      <div className="dep-symbol">
                        <code>{dep.symbol}</code>
                        {dep.type && <span className="dep-type">{dep.type}</span>}
                      </div>
                      <ArrowRight className="w-3 h-3 text-muted" />
                      <button
                        type="button"
                        className="dep-file"
                        onClick={() => onOpenFile(dep.target_file)}
                      >
                        {dep.target_file}
                      </button>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="step-unresolved">No external service dependencies identified.</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
