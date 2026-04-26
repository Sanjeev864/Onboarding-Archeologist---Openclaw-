import { Analysis } from "../lib/api";

export function AnalysisHeader({ analysis }: { analysis: Analysis }) {
  return (
    <header className="workspaceHeader">
      <div>
        <p className="eyebrow">Repository</p>
        <h2>{analysis.owner}/{analysis.repo}</h2>
      </div>
      <span>{new Date(analysis.analyzed_at).toLocaleString()}</span>
    </header>
  );
}
