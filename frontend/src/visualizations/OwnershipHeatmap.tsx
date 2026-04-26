import { Owner } from "../lib/api";

export function OwnershipHeatmap({ ownership }: { ownership: Owner[] }) {
  return <div>{ownership.map((item) => <span key={`${item.path}-${item.author}`}>{item.author}</span>)}</div>;
}
