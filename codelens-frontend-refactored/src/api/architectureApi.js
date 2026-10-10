import { apiRequest } from "./api";

export const getArchitectureFlows = () =>
  apiRequest("/api/architecture/flows");

export const getArchitectureGraph = () =>
  apiRequest("/api/architecture/graph");
