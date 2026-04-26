import { OracleAnswer } from "../lib/api";

export function OracleInterface({ answer }: { answer: OracleAnswer | null }) {
  return answer ? <section>{answer.answer}</section> : null;
}
