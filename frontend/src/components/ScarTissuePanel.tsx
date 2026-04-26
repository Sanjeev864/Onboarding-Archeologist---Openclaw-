import { ScarTissue } from "../lib/api";

export function ScarTissuePanel({ scarTissue }: { scarTissue: ScarTissue[] }) {
  return <div>{scarTissue.map((item) => <article key={`${item.file_path}-${item.pattern_type}`}>{item.file_path}</article>)}</div>;
}
