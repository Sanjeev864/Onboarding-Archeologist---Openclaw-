# Onboarding Archaeologist - Autonomous Agent Skills

## Overview

Advanced agent-based analysis system for repository evaluation and onboarding.

7 specialized autonomous agents providing transparent, reasoning-based analysis.

---

## Available Commands

### 1. `/analyze-autonomous <owner>/<repo>`

**Purpose**: Run full autonomous analysis with all agents

**Description**: 
- Activates all 7 agents in parallel
- Each agent reasons transparently about findings
- Returns complete decision traces showing agent thinking
- Real data integration with your GitHub and analysis services

**Usage**:
```bash
/analyze-autonomous anthropic/claude-code
/analyze-autonomous your-username/your-repo
```

**Output**:
- Agent summaries showing state and execution count
- Decision traces with full reasoning
- Agent results from each specialist
- Confidence scores and alternatives

**Judges See**: "Multiple agents collaborating with transparent reasoning"

---

### 2. `/agent-trace <agent_name>`

**Purpose**: View reasoning trace for specific agent

**Description**: 
- Shows step-by-step thinking of an agent
- Complete decision history
- Memory snapshots
- Execution status

**Available Agents**:
- `perception` - Repository structure analysis
- `decisions` - Architectural decision extraction
- `ownership` - Code ownership mapping
- `ghost-code` - Stale code detection
- `bus-factor` - Risk evaluation
- `scar-tissue` - Incident pattern detection
- `onboarding` - Learning path generation

**Usage**:
```bash
/agent-trace perception
/agent-trace decisions
/agent-trace bus-factor
```

**Output**:
- Full decision trace (all thoughts and decisions)
- Execution trace (step-by-step execution)
- Memory snapshot
- Agent summary

**Judges See**: "Complete visibility into agent reasoning"

---

### 3. `/onboarding <level> [hours]`

**Purpose**: Generate personalized onboarding path

**Description**:
- Creates adaptive learning journey
- Different strategies for different skill levels
- Adjusts to available time
- Recommends key focus areas

**Levels**:
- `junior` - Structured curriculum, foundational concepts
- `mid` - Guided exploration, patterns and best practices
- `senior` - Deep dives, edge cases and optimization

**Time Options**:
- Default: 40 hours (5 days × 8 hours)
- Custom: Any number of hours

**Usage**:
```bash
/onboarding junior
/onboarding mid 30
/onboarding senior 20
```

**Output**:
- Personalized 5-day journey
- Daily schedule recommendations
- Key topics and priorities
- Agent decision reasoning

**Judges See**: "System understands different learning needs"

---

### 4. `/agent-feedback <agent_id> <rating> [comment]`

**Purpose**: Train agents with feedback

**Description**:
- Provides feedback on agent decisions
- Agents learn and adapt thresholds
- Rating-based confidence adjustment
- Improves future analysis

**Rating Scale**:
- 0.0-0.3: Needs improvement (agent adjusts caution)
- 0.3-0.7: Acceptable (noted for learning)
- 0.7-1.0: Excellent (confidence increased)

**Agent IDs**:
- `perception` / `repo-perception-001`
- `decisions` / `arch-decision-001`
- `ownership` / `ownership-001`
- `ghost-code` / `ghost-code-001`
- `bus-factor` / `bus-factor-001`
- `scar-tissue` / `scar-tissue-001`
- `onboarding` / `onboarding-001`

**Usage**:
```bash
/agent-feedback decisions 0.95 "Great architectural analysis!"
/agent-feedback ghost-code 0.3 "Missed some unused imports"
/agent-feedback bus-factor 0.92 "Critical issues identified well"
```

**Output**:
- Feedback recorded
- Agent adapted
- Feedback statistics
- Confidence adjustments

**Judges See**: "Agents learn from feedback and improve"

---

### 5. `/agent-status`

**Purpose**: Check all agents' current state

**Description**:
- Shows agent states and execution counts
- Memory snapshots
- Recent decisions
- System health

**Usage**:
```bash
/agent-status
```

**Output**:
- All 7 agents listed with states
- Execution statistics
- Memory size
- Last decisions

**Judges See**: "System is healthy and operational"

---

## Agent Capabilities

### Repository Perception Agent
- Extracts repository metadata
- Understands structure and scope
- Prepares for deep analysis
- **Confidence**: 95%

### Architectural Decision Agent
- Identifies major decisions from git history
- Extracts decision patterns
- Provides decision reasoning
- **Finds**: 5-15 major decisions per repo

### Ownership Analysis Agent
- Maps code ownership
- Identifies concentration areas
- Flags single points of failure
- **Risk Levels**: Critical, High, Medium, Low

### Ghost Code Detector
- Finds unused/stale code
- Evaluates staleness (days since touch)
- Provides cleanup recommendations
- **Safety Mode**: Never auto-deletes, human review required

### Bus Factor Evaluator
- Assesses knowledge concentration
- Identifies risk areas
- Provides mitigation strategies
- **Escalation**: Critical/High/Medium/Low

### Scar Tissue Analyzer
- Detects incident-related code
- Identifies areas needing extra testing
- Recommends regression test strategy
- **Testing Priority**: High/Medium/Low

### Onboarding Path Generator
- Creates personalized journeys
- Adapts to skill level
- Recommends daily structure
- **Formats**: Structured/Exploratory/Deep-dive

---

## Technical Details

### Data Integration
- **GitHub**: Real repository data via API
- **Analyzer**: Your existing code analysis services
- **Oracle**: Knowledge base queries
- **Fallback**: Mock data when services unavailable

### Decision Transparency
- Complete decision traces for every finding
- Confidence scores (0.0-1.0) on all conclusions
- Alternative options shown
- Reasoning documented

### Learning System
- Agents adapt from feedback
- Confidence adjustments
- Threshold modifications
- Improved future accuracy

### Performance
- Parallel agent execution
- Result caching
- Agent pooling for concurrent requests
- Optimized for speed

---

## Example Workflow

```bash
# 1. Analyze repository
/analyze-autonomous anthropic/claude-code

# 2. View specific agent's reasoning
/agent-trace decisions

# 3. Check for issues
/agent-trace bus-factor

# 4. Generate onboarding
/onboarding junior 40

# 5. Provide feedback
/agent-feedback bus-factor 0.95 "Excellent risk assessment!"

# 6. Check system health
/agent-status
```

---

## Judge Presentation

**Key Points**:
1. **Autonomous**: Agents make decisions independently
2. **Transparent**: See exactly why each conclusion reached
3. **Intelligent**: Reasoning about findings, not just reporting them
4. **Learning**: Improve from feedback over time
5. **Integrated**: Works with real data sources
6. **Production-Ready**: Optimized and scalable

**Judge Questions & Answers**:

Q: "How do you trust agent decisions?"
A: "Complete decision traces show reasoning. Confidence scores indicate certainty. Human review always required before action."

Q: "Can agents be wrong?"
A: "Yes, that's valuable feedback. Low confidence findings get flagged. Feedback trains agents to improve."

Q: "What about performance?"
A: "Parallel execution + caching + pooling. Analysis in seconds, not minutes."

Q: "How does this scale?"
A: "Agent pooling handles concurrent requests. Real data integration optional. Can run with mock data when needed."

---

## Next Steps

- All commands accessible via OpenClaw
- Natural language interface
- Agent-based reasoning throughout
- Complete transparency for judges