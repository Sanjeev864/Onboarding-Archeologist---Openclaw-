import { BusFactorAlert } from "../lib/api";

export function BusFactorGauge({ alerts }: { alerts: BusFactorAlert[] }) {
  const critical = alerts.filter((alert) => alert.risk_level === "critical").length;
  return <meter min={0} max={alerts.length || 1} value={critical} />;
}
