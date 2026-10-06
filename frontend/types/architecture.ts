export interface FrontendApiReference {
  function: string;
  method: string;
  endpoint: string;
  resolved_endpoint: string;
  endpoint_variable?: string | null;
  line: number;
  file: string;
}

export interface BackendRouteReference {
  method: string;
  path: string;
  handler: string;
  route_file: string;
  route_line: number;
  mount_file?: string;
  mount_line?: number;
}

export interface ControllerReference {
  handler: string;
  controller_file: string;
  controller_function: string;
  controller_start_line: number;
  controller_end_line: number;
}

export interface DependencyReference {
  symbol: string;
  target_file: string;
  import_source?: string;
  type?: string;
}

export interface FeatureFlow {
  id: string;
  name: string;
  frontend_api?: FrontendApiReference;
  route?: BackendRouteReference | null;
  controller?: ControllerReference | null;
  dependencies: DependencyReference[];
  description?: string;
}

export interface GraphNode {
  id: string;
  file: string;
  imports: Array<{ source: string; names: string[] }>;
  functions: Array<{ name: string; start_line: number; end_line: number }>;
  calls: Array<{ name: string; start_line: number }>;
  imports_count: number;
  functions_count: number;
  calls_count: number;
}

export interface GraphEdge {
  source: string;
  target: string;
  relation: string;
}

export interface CodeGraphData {
  summary: {
    nodes: number;
    edges: number;
  };
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface ArchitectureFlowsResponse {
  repository: string;
  flows: FeatureFlow[];
  total: number;
}
