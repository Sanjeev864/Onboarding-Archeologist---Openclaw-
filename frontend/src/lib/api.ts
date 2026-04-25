const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export type Decision = {
  title: string;
  summary: string;
  evidence: string;
  confidence: number;
  commit_sha: string;
  committed_at: string;
  author: string;
};

export type Owner = {
  path: string;
  author: string;
  commits: number;
  risk: "low" | "medium" | "high";
};

export type GhostCode = {
  path: string;
  reason: string;
  last_touched_days: number;
  confidence: number;
};

export type Analysis = {
  repository_id: number;
  owner: string;
  repo: string;
  analyzed_at: string;
  decisions: Decision[];
  ownership: Owner[];
  ghost_code: GhostCode[];
};

export type OracleAnswer = {
  answer: string;
  evidence: string[];
};

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail ?? `Request failed with ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export function analyze(owner: string, repo: string, branch?: string) {
  return request<Analysis>("/api/analyze", {
    method: "POST",
    body: JSON.stringify({ owner, repo, branch: branch || undefined }),
  });
}

export function askOracle(repositoryId: number, question: string) {
  return request<OracleAnswer>("/api/oracle", {
    method: "POST",
    body: JSON.stringify({ repository_id: repositoryId, question }),
  });
}
