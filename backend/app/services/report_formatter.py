"""
report_formatter.py - Format agent outputs into human-readable reports
"""

from typing import Dict, Any, List
from datetime import datetime


class ReportFormatter:
    """Format agent analysis into professional reports"""
    
    @staticmethod
    def format_analysis_report(analysis: Dict[str, Any]) -> str:
        """Format complete analysis into readable report"""
        
        lines = []
        lines.append("=" * 90)
        lines.append("AUTONOMOUS REPOSITORY ANALYSIS REPORT")
        lines.append("=" * 90)
        lines.append("")
        
        repo = analysis.get("repository", "Unknown")
        timestamp = analysis.get("timestamp", "")
        lines.append(f"Repository: {repo}")
        lines.append(f"Analyzed: {timestamp}")
        lines.append(f"Mode: Autonomous Agents (6 specialized agents)")
        lines.append("")
        
        # Repository Perception
        lines.extend(ReportFormatter._format_perception_section(
            analysis.get("agent_summaries", {}).get("perception", {})
        ))
        
        # Architectural Decisions
        lines.extend(ReportFormatter._format_decisions_section(
            analysis.get("agent_summaries", {}).get("decisions", {})
        ))
        
        # Ownership Analysis
        lines.extend(ReportFormatter._format_ownership_section(
            analysis.get("agent_summaries", {}).get("ownership", {})
        ))
        
        # Ghost Code
        lines.extend(ReportFormatter._format_ghost_code_section(
            analysis.get("agent_summaries", {}).get("ghost_code", {})
        ))
        
        # Bus Factor
        lines.extend(ReportFormatter._format_bus_factor_section(
            analysis.get("agent_summaries", {}).get("bus_factor", {})
        ))
        
        # Scar Tissue
        lines.extend(ReportFormatter._format_scar_tissue_section(
            analysis.get("agent_summaries", {}).get("scar_tissue", {})
        ))
        
        lines.append("")
        lines.append("=" * 90)
        lines.append("End of Autonomous Analysis Report")
        lines.append("=" * 90)
        
        return "\n".join(lines)
    
    @staticmethod
    def _format_perception_section(perception: Dict[str, Any]) -> List[str]:
        """Format perception agent findings"""
        lines = []
        lines.append("📍 REPOSITORY PERCEPTION")
        lines.append("-" * 90)
        
        state = perception.get("state", "unknown")
        steps = perception.get("steps_executed", 0)
        
        lines.append(f"Agent Status: {state.upper()}")
        lines.append(f"Analysis Steps: {steps}")
        lines.append(f"Thoughts Generated: {perception.get('thoughts_count', 0)}")
        lines.append("")
        
        return lines
    
    @staticmethod
    def _format_decisions_section(decisions: Dict[str, Any]) -> List[str]:
        """Format architectural decisions"""
        lines = []
        lines.append("🏗️  ARCHITECTURAL DECISIONS")
        lines.append("-" * 90)
        
        decision_count = decisions.get("decisions_count", 0)
        last_decision = decisions.get("last_decision", {})
        confidence = last_decision.get("confidence", 0)
        
        if decision_count == 0:
            lines.append("No significant architectural decisions detected.")
        else:
            lines.append(f"Decisions Identified: {decision_count}")
            lines.append(f"Average Confidence: {confidence:.0%}")
            lines.append(f"Last Decision Confidence: {confidence:.0%}")
        
        lines.append("")
        return lines
    
    @staticmethod
    def _format_ownership_section(ownership: Dict[str, Any]) -> List[str]:
        """Format ownership analysis"""
        lines = []
        lines.append("👥 CODE OWNERSHIP ANALYSIS")
        lines.append("-" * 90)
        
        memory = ownership.get("memory", {})
        ownership_data = memory.get("ownership_analyzed", {})
        
        lines.append(f"Paths Analyzed: {ownership_data.get('paths_analyzed', 0)}")
        
        last_decision = ownership.get("last_decision", {})
        threshold = last_decision.get("parameters", {}).get("severity_threshold", "unknown")
        
        lines.append(f"Risk Threshold: {threshold.upper()}")
        
        if threshold == "high":
            lines.append("⚠️  HIGH CONCENTRATION DETECTED - Mitigation recommended")
        
        lines.append("")
        return lines
    
    @staticmethod
    def _format_ghost_code_section(ghost: Dict[str, Any]) -> List[str]:
        """Format ghost code findings"""
        lines = []
        lines.append("👻 GHOST CODE DETECTION")
        lines.append("-" * 90)
        
        memory = ghost.get("memory", {})
        detection = memory.get("ghost_code_detected", {})
        
        candidates = detection.get("candidates_found", 0)
        lines.append(f"Stale Code Candidates: {candidates}")
        
        last_decision = ghost.get("last_decision", {})
        safety_mode = last_decision.get("parameters", {}).get("safety_first", True)
        
        if safety_mode:
            lines.append("✅ Safety Mode: ENABLED (manual review required)")
        
        lines.append("🔍 Recommendation: Review each candidate before deletion")
        lines.append("")
        
        return lines
    
    @staticmethod
    def _format_bus_factor_section(bus: Dict[str, Any]) -> List[str]:
        """Format bus factor evaluation"""
        lines = []
        lines.append("⚠️  BUS FACTOR EVALUATION")
        lines.append("-" * 90)
        
        memory = bus.get("memory", {})
        evaluation = memory.get("bus_factor_evaluated", {})
        
        alerts = evaluation.get("alerts_found", 0)
        lines.append(f"Risk Alerts: {alerts}")
        
        last_decision = bus.get("last_decision", {})
        params = last_decision.get("parameters", {})
        escalation = params.get("escalation_level", "unknown")
        
        if escalation == "critical":
            lines.append(f"🚨 ESCALATION LEVEL: CRITICAL")
            lines.append("   → Immediate action recommended")
        elif escalation == "high":
            lines.append(f"⚠️  ESCALATION LEVEL: HIGH")
            lines.append("   → Address within 30-90 days")
        
        lines.append("")
        return lines
    
    @staticmethod
    def _format_scar_tissue_section(scar: Dict[str, Any]) -> List[str]:
        """Format scar tissue findings"""
        lines = []
        lines.append("🔍 SCAR TISSUE ANALYSIS")
        lines.append("-" * 90)
        
        memory = scar.get("memory", {})
        analysis = memory.get("scar_tissue_analyzed", {})
        
        lines.append("Status: Analysis Complete")
        lines.append(f"Testing Priority: {analysis.get('testing_priority', 'unknown').upper()}")
        lines.append("💡 Recommendation: Extra testing for incident-related code")
        lines.append("")
        
        return lines
    
    @staticmethod
    def format_decision_trace_report(agent_name: str, trace: List[Dict]) -> str:
        """Format decision trace for readability"""
        
        lines = []
        lines.append("")
        lines.append("=" * 90)
        lines.append(f"AGENT DECISION TRACE: {agent_name.upper()}")
        lines.append("=" * 90)
        lines.append("")
        
        if not trace:
            lines.append("No decisions recorded yet.")
            return "\n".join(lines)
        
        for i, step in enumerate(trace, 1):
            lines.append(f"Step {i}:")
            lines.append("-" * 45)
            
            # Thought
            thought = step.get("thought", {})
            reasoning = thought.get("reasoning", "N/A")[:150]
            confidence = thought.get("confidence", 0)
            
            lines.append(f"  💭 Thought: {reasoning}...")
            lines.append(f"  📊 Confidence: {confidence:.0%}")
            
            if thought.get("alternatives"):
                lines.append(f"  🔄 Alternatives: {', '.join(thought['alternatives'][:2])}")
            
            # Decision
            decision = step.get("decision", {})
            action = decision.get("action_type", "N/A")
            
            lines.append(f"  🎯 Decision: {action}")
            lines.append(f"  💬 Reasoning: {decision.get('reasoning', 'N/A')[:100]}...")
            
            # Execution
            execution = step.get("execution", {})
            success = execution.get("success", False)
            
            status = "✅ Success" if success else "❌ Failed"
            lines.append(f"  🔧 Execution: {status}")
            lines.append("")
        
        lines.append("=" * 90)
        return "\n".join(lines)
    
    @staticmethod
    def format_onboarding_journey(journey: Dict[str, Any], level: str) -> str:
        """Format onboarding path"""
        
        lines = []
        lines.append("")
        lines.append("=" * 90)
        lines.append(f"PERSONALIZED ONBOARDING JOURNEY: {level.upper()}")
        lines.append("=" * 90)
        lines.append("")
        
        lines.append(f"Duration: {journey.get('days', 5)} days")
        lines.append(f"Daily Hours: {journey.get('daily_hours', 8)}")
        lines.append(f"Total Hours: {journey.get('total_hours', 40)}")
        lines.append(f"Structure: {journey.get('structure', 'adaptive')}")
        lines.append("")
        
        if journey.get("includes_exercises"):
            lines.append("✅ Includes hands-on exercises")
        
        if journey.get("includes_recommendations"):
            lines.append("✅ Includes personalized recommendations")
        
        lines.append("")
        lines.append("Recommended Focus Areas:")
        lines.append("-" * 45)
        
        if level == "junior":
            lines.append("  1. Core architecture and design patterns")
            lines.append("  2. Codebase navigation and structure")
            lines.append("  3. Key dependencies and libraries")
            lines.append("  4. Testing and debugging practices")
            lines.append("  5. Common workflows and tools")
        elif level == "mid":
            lines.append("  1. Decision history and architectural evolution")
            lines.append("  2. Code ownership and responsibilities")
            lines.append("  3. Edge cases and incident patterns")
            lines.append("  4. Performance optimization opportunities")
            lines.append("  5. Team practices and conventions")
        else:  # senior
            lines.append("  1. Strategic architectural insights")
            lines.append("  2. Knowledge concentration risks")
            lines.append("  3. Technical debt and scar tissue")
            lines.append("  4. Future roadmap and scalability")
            lines.append("  5. Team mentoring and knowledge transfer")
        
        lines.append("")
        lines.append("=" * 90)
        return "\n".join(lines)


class HTMLReportFormatter:
    """Format reports as HTML for web viewing"""
    
    @staticmethod
    def format_analysis_as_html(analysis: Dict[str, Any]) -> str:
        """Generate HTML report"""
        
        html = """
        <html>
        <head>
            <title>Autonomous Analysis Report</title>
            <style>
                body { font-family: 'Segoe UI', Tahoma, sans-serif; margin: 20px; }
                h1 { color: #333; border-bottom: 3px solid #007bff; padding-bottom: 10px; }
                h2 { color: #555; margin-top: 30px; }
                .agent-section { background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }
                .success { color: #28a745; font-weight: bold; }
                .warning { color: #ffc107; font-weight: bold; }
                .critical { color: #dc3545; font-weight: bold; }
                table { width: 100%; border-collapse: collapse; }
                th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
                th { background-color: #007bff; color: white; }
            </style>
        </head>
        <body>
            <h1>🤖 Autonomous Repository Analysis</h1>
        """
        
        repo = analysis.get("repository", "Unknown")
        html += f"<p><strong>Repository:</strong> {repo}</p>"
        html += f"<p><strong>Analysis Time:</strong> {analysis.get('timestamp', '')}</p>"
        
        # Add sections
        agents = analysis.get("agent_summaries", {})
        
        for agent_name, summary in agents.items():
            html += f"""
            <div class="agent-section">
                <h2>📊 {agent_name.replace('_', ' ').title()}</h2>
                <p><strong>State:</strong> {summary.get('state', 'unknown')}</p>
                <p><strong>Steps Executed:</strong> {summary.get('steps_executed', 0)}</p>
                <p><strong>Decisions Made:</strong> {summary.get('decisions_count', 0)}</p>
            </div>
            """
        
        html += """
        </body>
        </html>
        """
        
        return html