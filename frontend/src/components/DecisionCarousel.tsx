import { Decision } from "../lib/api";

export function DecisionCarousel({ decisions }: { decisions: Decision[] }) {
  return <div>{decisions.map((decision) => <article key={decision.commit_sha}>{decision.title}</article>)}</div>;
}
