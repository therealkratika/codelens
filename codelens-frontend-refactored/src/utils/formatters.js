export const formatCount = value => (Number(value) || 0).toLocaleString();
export const repositoryDisplayName = repo => repo?.repository || repo?.name || "Repository";
