import { BusFactorAlert as Alert } from "../lib/api";

export function BusFactorAlert({ alert }: { alert: Alert }) {
  return <article>{alert.critical_person}: {alert.risk_level}</article>;
}
