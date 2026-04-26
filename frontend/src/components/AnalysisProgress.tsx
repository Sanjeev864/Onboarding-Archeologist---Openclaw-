export function AnalysisProgress({ progress }: { progress: number }) {
  return <progress value={progress} max={100} />;
}
