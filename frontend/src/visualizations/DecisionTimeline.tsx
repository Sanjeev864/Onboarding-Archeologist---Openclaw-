import { Decision } from "../lib/api";

export function DecisionTimeline({ decisions }: { decisions: Decision[] }) {
  return <ol>{decisions.map((item) => <li key={item.commit_sha}>{item.title}</li>)}</ol>;
}
