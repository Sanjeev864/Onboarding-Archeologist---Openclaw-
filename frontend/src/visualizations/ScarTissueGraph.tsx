import { ScarTissue } from "../lib/api";

export function ScarTissueGraph({ scarTissue }: { scarTissue: ScarTissue[] }) {
  return <div>{scarTissue.length} defensive patterns</div>;
}
