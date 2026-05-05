"""
report_formatter.py - Professional text and HTML formatting for agent outputs.
"""

from __future__ import annotations

from typing import Any, Dict, List


class ReportFormatter:
    """Format agent analysis into readable reports."""

    @staticmethod
    def format_analysis_report(analysis: Dict[str, Any]) -> str:
        lines = [
            "=" * 90,
            "AGENTIC REPOSITORY ANALYSIS REPORT",
            "=" * 90,
            "",
            f"Repository: {analysis.get('repository', 'Unknown')}",
            f"Analyzed: {analysis.get('timestamp', '')}",
            f"Mode: {analysis.get('analysis_mode', 'agentic_evidence_workflow')}",
            f"Data Source: {analysis.get('data_source', 'git_history_and_github_api')}",
            "",
        ]

        lines.extend(ReportFormatter._format_perception_section(analysis))
        lines.extend(ReportFormatter._format_decisions_section(analysis))
        lines.extend(ReportFormatter._format_ownership_section(analysis))
        lines.extend(ReportFormatter._format_ghost_code_section(analysis))
        lines.extend(ReportFormatter._format_bus_factor_section(analysis))
        lines.extend(ReportFormatter._format_scar_tissue_section(analysis))

        lines.extend(["", "=" * 90, "End of Agentic Analysis Report", "=" * 90])
        return "\n".join(lines)

    @staticmethod
    def _agent_summary(analysis: Dict[str, Any], name: str) -> Dict[str, Any]:
        return analysis.get("agent_summaries", {}).get(name, {})

    @staticmethod
    def _agent_result(analysis: Dict[str, Any], name: str) -> Dict[str, Any]:
        return analysis.get("agent_results", {}).get(name, {}).get("result", {})

    @staticmethod
    def _format_perception_section(analysis: Dict[str, Any]) -> List[str]:
        summary = ReportFormatter._agent_summary(analysis, "perception")
        evidence = ReportFormatter._agent_result(analysis, "perception").get("analysis", {})
        return [
            "REPOSITORY PERCEPTION",
            "-" * 90,
            f"Agent Status: {summary.get('state', 'unknown').upper()}",
            f"Analysis Steps: {summary.get('steps_executed', 0)}",
            f"Thoughts Generated: {summary.get('thoughts_count', 0)}",
            f"Commits Analyzed: {evidence.get('total_commits_analyzed', 0)}",
            f"Default Branch: {evidence.get('default_branch', 'unknown')}",
            "",
        ]

    @staticmethod
    def _format_decisions_section(analysis: Dict[str, Any]) -> List[str]:
        summary = ReportFormatter._agent_summary(analysis, "decisions")
        result = ReportFormatter._agent_result(analysis, "decisions")
        confidence = summary.get("last_decision", {}).get("confidence", 0)
        count = result.get("decisions_found", 0)
        lines = ["ARCHITECTURAL DECISIONS", "-" * 90]
        if count == 0:
            lines.append("No explicit architectural decision commits detected.")
        else:
            lines.append(f"Decisions Identified: {count}")
        lines.extend([f"Agent Confidence: {confidence:.0%}", ""])
        return lines

    @staticmethod
    def _format_ownership_section(analysis: Dict[str, Any]) -> List[str]:
        summary = ReportFormatter._agent_summary(analysis, "ownership")
        result = ReportFormatter._agent_result(analysis, "ownership")
        threshold = summary.get("last_decision", {}).get("parameters", {}).get("severity_threshold", "unknown")
        lines = [
            "CODE OWNERSHIP ANALYSIS",
            "-" * 90,
            f"Paths Analyzed: {result.get('paths_analyzed', 0)}",
            f"Risk Threshold: {threshold.upper()}",
        ]
        if threshold == "high":
            lines.append("High concentration detected. Mitigation recommended.")
        lines.append("")
        return lines

    @staticmethod
    def _format_ghost_code_section(analysis: Dict[str, Any]) -> List[str]:
        summary = ReportFormatter._agent_summary(analysis, "ghost_code")
        result = ReportFormatter._agent_result(analysis, "ghost_code")
        safety = summary.get("last_decision", {}).get("parameters", {}).get("safety_first", True)
        return [
            "GHOST CODE DETECTION",
            "-" * 90,
            f"Stale Code Candidates: {result.get('candidates_found', 0)}",
            f"Safety Mode: {'ENABLED' if safety else 'DISABLED'}",
            "Recommendation: Review each candidate before deletion.",
            "",
        ]

    @staticmethod
    def _format_bus_factor_section(analysis: Dict[str, Any]) -> List[str]:
        result = ReportFormatter._agent_result(analysis, "bus_factor")
        return [
            "BUS FACTOR EVALUATION",
            "-" * 90,
            f"Risk Alerts: {result.get('alerts_found', 0)}",
            "",
        ]

    @staticmethod
    def _format_scar_tissue_section(analysis: Dict[str, Any]) -> List[str]:
        result = ReportFormatter._agent_result(analysis, "scar_tissue")
        return [
            "SCAR TISSUE ANALYSIS",
            "-" * 90,
            "Status: Analysis Complete",
            f"Testing Priority: {result.get('testing_priority', 'unknown').upper()}",
            f"Patterns Found: {result.get('patterns_found', 0)}",
            "Recommendation: Add extra tests around incident-related code.",
            "",
        ]

    @staticmethod
    def format_decision_trace_report(agent_name: str, trace: List[Dict[str, Any]]) -> str:
        lines = ["", "=" * 90, f"AGENT DECISION TRACE: {agent_name.upper()}", "=" * 90, ""]
        if not trace:
            lines.append("No decisions recorded yet.")
            return "\n".join(lines)

        for index, step in enumerate(trace, 1):
            thought = step.get("thought", {})
            decision = step.get("decision", {})
            execution = step.get("execution", {})
            lines.extend(
                [
                    f"Step {index}:",
                    "-" * 45,
                    f"  Thought: {thought.get('reasoning', 'N/A')[:150]}",
                    f"  Confidence: {thought.get('confidence', 0):.0%}",
                    f"  Alternatives: {', '.join(thought.get('alternatives', [])[:2]) or 'None'}",
                    f"  Decision: {decision.get('action_type', 'N/A')}",
                    f"  Reasoning: {decision.get('reasoning', 'N/A')[:100]}",
                    f"  Execution: {'Success' if execution.get('success', False) else 'Failed'}",
                    "",
                ]
            )

        lines.append("=" * 90)
        return "\n".join(lines)

    @staticmethod
    def format_onboarding_journey(journey: Dict[str, Any], level: str) -> str:
        lines = [
            "",
            "=" * 90,
            f"PERSONALIZED ONBOARDING JOURNEY: {level.upper()}",
            "=" * 90,
            "",
            f"Duration: {journey.get('days', 5)} days",
            f"Daily Hours: {journey.get('daily_hours', 8)}",
            f"Total Hours: {journey.get('total_hours', 40)}",
            f"Structure: {journey.get('structure', 'adaptive')}",
            "",
            "Recommended Focus Areas:",
            "-" * 45,
        ]
        focus_by_level = {
            "junior": [
                "Core architecture and design patterns",
                "Codebase navigation and structure",
                "Testing and debugging practices",
            ],
            "mid": [
                "Decision history and architectural evolution",
                "Code ownership and responsibilities",
                "Incident patterns and edge cases",
            ],
            "senior": [
                "Strategic architectural insights",
                "Knowledge concentration risks",
                "Technical debt and scar tissue",
            ],
        }
        for index, item in enumerate(focus_by_level.get(level, focus_by_level["junior"]), 1):
            lines.append(f"  {index}. {item}")
        lines.extend(["", "=" * 90])
        return "\n".join(lines)


class HTMLReportFormatter:
    """Format reports as simple HTML for web viewing."""

    @staticmethod
    def format_analysis_as_html(analysis: Dict[str, Any]) -> str:
        agents = analysis.get("agent_summaries", {})
        sections = "".join(
            f"""
            <section class="agent-section">
                <h2>{agent_name.replace('_', ' ').title()}</h2>
                <p><strong>State:</strong> {summary.get('state', 'unknown')}</p>
                <p><strong>Steps Executed:</strong> {summary.get('steps_executed', 0)}</p>
                <p><strong>Decisions Made:</strong> {summary.get('decisions_count', 0)}</p>
            </section>
            """
            for agent_name, summary in agents.items()
        )
        return f"""
        <html>
        <head>
            <title>Agentic Analysis Report</title>
            <style>
                body {{ font-family: Segoe UI, Tahoma, sans-serif; margin: 24px; color: #1f2937; }}
                h1 {{ border-bottom: 3px solid #2563eb; padding-bottom: 10px; }}
                .agent-section {{ background: #f8fafc; padding: 16px; border-radius: 6px; margin: 16px 0; }}
            </style>
        </head>
        <body>
            <h1>Agentic Repository Analysis</h1>
            <p><strong>Repository:</strong> {analysis.get('repository', 'Unknown')}</p>
            <p><strong>Analysis Time:</strong> {analysis.get('timestamp', '')}</p>
            <p><strong>Mode:</strong> {analysis.get('analysis_mode', '')}</p>
            {sections}
        </body>
        </html>
        """
