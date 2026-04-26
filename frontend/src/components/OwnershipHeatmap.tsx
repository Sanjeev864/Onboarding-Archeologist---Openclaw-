import { Owner } from "../lib/api";

export function OwnershipHeatmap({ ownership }: { ownership: Owner[] }) {
  return <div>{ownership.map((owner) => <span key={`${owner.path}-${owner.author}`}>{owner.path}</span>)}</div>;
}
