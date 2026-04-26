from __future__ import annotations

from dataclasses import dataclass

from ..schemas import AnalysisOut, AnswerOut


@dataclass
class OpenClawResponse:
    text: str
    repository_id: int | None = None


def format_analysis(analysis: AnalysisOut) -> OpenClawResponse:
    lines = [
        f"Analysis complete: {analysis.owner}/{analysis.repo}",
        "",
        f"Repository ID: {analysis.repository_id}",
        f"Commits analyzed: {analysis.coverage_summary.get('total_commits_analyzed', 0)}",
        f"Coverage: {analysis.coverage_summary.get('coverage_percentage', 0)}%",
        "",
        "Architectural Decisions",
    ]
    if analysis.decisions:
        for index, decision in enumerate(analysis.decisions[:5], start=1):
            lines.extend(
                [
                    f"{index}. {decision.title} ({round(decision.confidence * 100)}%)",
                    f"   Evidence: {decision.evidence}",
                ]
            )
    else:
        lines.append("- No explicit decision signals found in the analyzed history.")

    lines.extend(["", "Knowledge Concentration"])
    risky_owners = [owner for owner in analysis.ownership if owner.risk in {"high", "medium"}]
    if risky_owners:
        for owner in risky_owners[:6]:
            lines.append(f"- {owner.risk.upper()}: {owner.path} owned by {owner.author} ({owner.commits} commits)")
    else:
        lines.append("- No high or medium ownership concentration found.")

    lines.extend(["", "Ghost Code Candidates"])
    if analysis.ghost_code:
        for finding in analysis.ghost_code[:5]:
            lines.append(f"- {finding.path}: {finding.reason}; last touched {finding.last_touched_days} days ago")
    else:
        lines.append("- No ghost-code candidates found.")

    lines.extend(["", "Bus Factor Alerts"])
    if analysis.bus_factor_alerts:
        for alert in analysis.bus_factor_alerts[:5]:
            areas = ", ".join(alert.areas_affected[:4])
            lines.append(f"- {alert.risk_level.upper()}: {alert.critical_person} ({alert.concentration_percentage}%) across {areas}")
    else:
        lines.append("- No bus-factor alerts found.")

    lines.extend(["", "Next commands: /ask \"why...\", /bus-factor, /decisions, /ghost-code, /onboarding junior"])
    return OpenClawResponse(text="\n".join(lines), repository_id=analysis.repository_id)


def format_answer(answer: AnswerOut) -> str:
    lines = ["Oracle Answer", "", answer.answer, "", "Evidence"]
    if answer.evidence:
        lines.extend(f"- {item}" for item in answer.evidence[:8])
    else:
        lines.append("- No evidence returned.")
    return "\n".join(lines)


def format_decisions(analysis: AnalysisOut) -> str:
    lines = [f"Architectural Decisions: {analysis.owner}/{analysis.repo}", ""]
    if not analysis.decisions:
        lines.append("No explicit decision signals found.")
        return "\n".join(lines)
    for index, decision in enumerate(analysis.decisions[:10], start=1):
        lines.extend([f"{index}. {decision.title} ({round(decision.confidence * 100)}%)", f"   {decision.evidence}"])
    return "\n".join(lines)


def format_bus_factor(analysis: AnalysisOut) -> str:
    lines = [f"Bus Factor Analysis: {analysis.owner}/{analysis.repo}", ""]
    if not analysis.bus_factor_alerts:
        lines.append("No bus-factor alerts found.")
        return "\n".join(lines)
    for alert in analysis.bus_factor_alerts[:10]:
        lines.extend(
            [
                f"{alert.risk_level.upper()}: {alert.critical_person}",
                f"Concentration: {alert.concentration_percentage}%",
                f"Areas: {', '.join(alert.areas_affected[:8])}",
                f"Recommendation: {alert.recommendation}",
                "",
            ]
        )
    return "\n".join(lines).strip()


def format_ghost_code(analysis: AnalysisOut) -> str:
    lines = [f"Ghost Code Candidates: {analysis.owner}/{analysis.repo}", ""]
    if not analysis.ghost_code:
        lines.append("No ghost-code candidates found. Continue to verify manually before cleanup.")
        return "\n".join(lines)
    for finding in analysis.ghost_code[:10]:
        lines.extend(
            [
                f"- {finding.path}",
                f"  Reason: {finding.reason}",
                f"  Last touched: {finding.last_touched_days} days ago",
                f"  Confidence: {round(finding.confidence * 100)}%",
            ]
        )
    lines.append("")
    lines.append("Safety: treat these as review candidates, never automatic deletion.")
    return "\n".join(lines)


def format_onboarding(analysis: AnalysisOut, level: str) -> str:
    lines = [f"5-Day Onboarding Plan ({level.title()}): {analysis.owner}/{analysis.repo}", ""]
    if not analysis.onboarding_paths:
        lines.append("No onboarding path generated yet.")
        return "\n".join(lines)
    for day in analysis.onboarding_paths:
        locations = ", ".join(day.code_locations[:5]) or "No focused paths yet"
        lines.extend(
            [
                f"Day {day.day_number}: {day.focus_area}",
                f"- Concepts: {', '.join(day.key_concepts)}",
                f"- Code: {locations}",
                f"- Time: {day.estimated_hours}h",
                "",
            ]
        )
    return "\n".join(lines).strip()
