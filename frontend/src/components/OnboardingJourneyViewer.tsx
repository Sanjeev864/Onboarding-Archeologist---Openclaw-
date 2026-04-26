import { OnboardingDay } from "../lib/api";

export function OnboardingJourneyViewer({ days }: { days: OnboardingDay[] }) {
  return <div>{days.map((day) => <article key={day.day_number}>{day.focus_area}</article>)}</div>;
}
