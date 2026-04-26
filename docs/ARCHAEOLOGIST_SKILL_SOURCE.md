---
name: "Code Archaeologist"
description: >
  Excavates git history to reveal architectural decisions, knowledge ownership,
  ghost code, and scar tissue patterns. Accelerates developer onboarding and 
  identifies critical bus factor risks. Use when you need to understand:
  - Why architectural decisions were made
  - Who owns and understands what parts of the codebase  
  - Dead or abandoned code candidates for cleanup
  - Over-engineered defensive patterns and their incident origins
  - Knowledge concentration risks and single points of failure
  
  Analyze public/private GitHub repositories with evidence from actual git history,
  commit messages, and code patterns. No manual documentation needed.
  
version: "1.0.0"
author: "Onboarding Archaeologist Project"
tools:
  - exec
  - browser
  - fetch
tags:
  - codebase-intelligence
  - git-history
  - architecture
  - developer-onboarding
  - risk-assessment

skill-invocation: true
disable-model-invocation: false
---

# 🏺 Code Archaeologist

## Purpose

This skill makes any GitHub repository's history transparent and actionable. Instead of guessing why code is structured the way it is, it reconstructs the actual decision-making process from git history, identifies knowledge concentration risks, and flags technical debt patterns that originated from real incidents.

**Perfect for:**
- 🚀 Accelerating developer onboarding (3-6 months → days)
- 🔴 Identifying bus factor risks before people leave
- 🧟 Finding ghost code safely with evidence
- 🏛️ Understanding architectural evolution
- ⚠️ Tracing defensive patterns to incidents
- 📚 Creating custom onboarding journeys

## How It Works

1. **You provide**: Owner and repository name (e.g., "facebook/react")
2. **Archaeologist analyzes**: Last 200 commits for signals
3. **Returns findings**: Decisions, ownership, ghost code, risks
4. **You ask follow-ups**: "Why?" "Who?" "Safe to delete?"
5. **Evidence-backed answers**: All backed by actual git history

## When to Use This Skill

### ✅ Good Use Cases

- Onboarding a new engineer: `"Analyze microsoft/vscode and create onboarding plan"`
- Understanding a decision: `"Why is the database layer in src/db?"`
- Finding dead code: `"Are there unused files in this repo?"`
- Checking knowledge concentration: `"Who is the bus factor for authentication?"`
- Architectural review: `"What were the major design decisions in this project?"`
- Risk assessment: `"Show me high bus factor areas"`

### ❌ When NOT to Use

- **Already have documentation** - Use that first (faster)
- **Private repos without GitHub token** - Will fail (set token in .env)
- **Repos with <20 commits** - Too little history for reliable signals
- **Non-code repositories** - Designed for software projects

## Commands

### `/analyze <owner>/<repo>`
Full repository analysis with all findings.

**Example**: `/analyze facebook/react`

**Output**:
```
🔍 Analyzing facebook/react...
(30-60 seconds)

📊 COMPLETE ANALYSIS
✓ 200 commits analyzed
✓ Architectural decisions identified
✓ Knowledge ownership mapped  
✓ Ghost code detected
✓ Bus factor risks flagged
```

### `/ask <question>`
Ask about the last analyzed repository.

**Examples**:
- `/ask "Why was virtual DOM chosen?"`
- `/ask "Who should I ask about the scheduler?"`
- `/ask "Is src/legacy safe to delete?"`

### `/bus-factor`
Show knowledge concentration risks for last analyzed repo.

**Output**:
```
⚠️ BUS FACTOR ANALYSIS

🔴 CRITICAL RISK: john_doe
Areas: auth/, security/, key-rotation
Concentration: 89% of commits
Last active: 2 weeks ago
Impact: Team cannot deploy without him

Recommendation: Schedule knowledge transfer
```

### `/decisions`
Show architectural decisions only.

**Output**:
```
🏛️ ARCHITECTURAL DECISIONS

1. Virtual DOM implementation (95% confidence)
   "Provides better performance and flexibility"
   
2. Fiber architecture redesign (92% confidence)
   "Enable incremental rendering and priority-based updates"
```

### `/ghost-code`
Show dead/stale code candidates.

**Output**:
```
👻 GHOST CODE CANDIDATES

⚠️ src/legacy/v1-api.js
Last touched: 2 years ago
Status: May be safe to delete
Confidence: 78%

⚠️ src/utils/deprecated-helpers.ts
Markers: DEPRECATED, TODO: remove in v3
Status: Marked for deletion
Confidence: 92%
```

### `/onboarding <level>`
Create personalized onboarding journey.

**Examples**:
- `/onboarding junior` - Gentle introduction to codebase
- `/onboarding mid` - Focus on core systems and patterns
- `/onboarding senior` - Deep architectural understanding

**Output**:
```
📚 5-DAY ONBOARDING PLAN (Junior Level)

DAY 1: Architecture Overview
- What: High-level system components
- Learn: [5 key files]
- Time: 2-3 hours

DAY 2: Critical Paths
- What: Most changed and important areas
...
```

### `/help`
Show all available commands and examples.

---

## Step-by-Step Instructions

### Scenario 1: Analyze a Repository

**Goal**: Understand the architecture and key decisions of a project.

**Steps**:

1. **Send command**:
   ```
   /analyze facebook/react
   ```

2. **Archaeologist processes**:
   - Clones last 200 commits
   - Scans commit messages for decision keywords
   - Maps file ownership across commits
   - Detects stale/legacy code
   - Calculates bus factor for each area

3. **You receive findings**:
   ```
   🔍 Analysis Complete: facebook/react
   
   🏛️ MAJOR DECISIONS (Top 5)
   1. React Hooks (95% confidence)
      "Simplify state management, reusable logic"
   
   2. Virtual DOM (93% confidence)
      "Performance optimization and flexibility"
   
   👥 KNOWLEDGE CONCENTRATION
   🔴 Dan Abramov: scheduler, priority system (89%)
   🟡 Andrew Clark: fiber architecture (67%)
   
   👻 GHOST CODE
   src/renderers/dom/legacy/ - 1000+ days old
   
   ⚠️ BUS FACTOR: Dan Abramov is critical risk
   ```

4. **Ask follow-up questions**:
   ```
   /ask "Why was React Hooks introduced?"
   /bus-factor
   /ghost-code
   ```

### Scenario 2: Onboard a New Developer

**Goal**: Create a personalized learning path.

**Steps**:

1. **Analyze the repo**:
   ```
   /analyze company/backend
   ```

2. **Get onboarding plan**:
   ```
   /onboarding junior
   ```

3. **Receive day-by-day plan**:
   ```
   📚 Day 1: Database Layer
   - Learn about PostgreSQL schema
   - Key files: src/db/schema.ts, src/db/migrations/
   - Time: 2 hours
   - Focus: How data flows through system
   
   📚 Day 2: API Handlers
   - Learn about request/response cycle
   - Key files: src/api/handlers/
   - Time: 3 hours
   - Focus: Authentication and validation
   
   📚 Day 3: Business Logic
   - Learn core domain models
   - Key files: src/services/
   - Time: 3 hours
   - Focus: How data is processed
   
   📚 Day 4: Defensive Patterns
   - Learn why code is structured this way
   - Key files: src/middleware/, src/error-handling/
   - Time: 2 hours
   - Focus: Reliability patterns from incidents
   
   📚 Day 5: Getting Hands-On
   - First PR opportunities
   - Good starter tasks: 5 issues marked "good-first-issue"
   - Time: 4 hours
   ```

4. **Share with new developer**:
   ```
   Here's your 5-day onboarding plan for the backend.
   Follow this journey, and ask me questions anytime:
   [paste onboarding plan]
   ```

### Scenario 3: Check for Dead Code Before Refactoring

**Goal**: Safely identify code that can be removed.

**Steps**:

1. **Analyze the repo**:
   ```
   /analyze mycompany/api
   ```

2. **Get ghost code list**:
   ```
   /ghost-code
   ```

3. **Evaluate each candidate**:
   ```
   /ask "Is src/legacy-auth.ts safe to delete?"
   ```

4. **Get evidence-backed answer**:
   ```
   Based on git history analysis:
   
   ✓ Last changed: 18 months ago
   ✓ No tests reference it
   ✓ No other files import it
   ✓ Marked as DEPRECATED in code comments
   
   Confidence: 92% safe to delete
   
   Recommendation: 
   - Check one more time with team lead
   - Remove in separate PR
   - Keep removal commit for history
   ```

### Scenario 4: Check Bus Factor Risk

**Goal**: Identify knowledge concentration risks before attrition.

**Steps**:

1. **Analyze the repo**:
   ```
   /analyze company/mobile-app
   ```

2. **Check bus factor**:
   ```
   /bus-factor
   ```

3. **Get risk assessment**:
   ```
   ⚠️ CRITICAL BUS FACTOR RISKS
   
   🔴 Sarah Chen: iOS architecture (94% commits)
   - If she leaves: Can't ship iOS updates
   - Recommendation: Start knowledge transfer now
   - Action: Schedule pair programming sessions
   
   🔴 Marcus Lee: Push notifications (87% commits)
   - If he leaves: Can't fix notification bugs
   - Recommendation: Involve second person in design
   
   🟡 Jennifer Kim: Testing infrastructure (71% commits)
   - If she leaves: Tests become brittle
   - Recommendation: Document test patterns
   ```

4. **Take action**:
   ```
   Schedule knowledge transfer:
   - Sarah teaches iOS architecture to the team
   - Marcus documents push notification system
   - Jennifer creates testing guidelines
   ```

---

## Examples

### Example 1: Understanding Why Code Is the Way It Is

**User**: I'm confused why we have 5 retry layers in the payment service.

**Archaeologist**: Let me check the history...

```
/analyze company/payment-service
/ask "Why is there so much retry logic in the payment system?"
```

**Response**:
```
🧠 Oracle Answer:

The payment system has multiple retry layers because of 
a major incident in 2023 where payment processing failed 
silently for 4 hours, costing the company $50k.

Evidence:
• Commit 3a5f2e: "Add circuit breaker to payment gateway"
  Message: "Fix: Silent failures in Stripe API calls - incident #4521"
  
• Commit 7b2c1d: "Add exponential backoff for retries"
  Message: "Prevent cascade failures during provider outages"
  
• PR #892: "Add comprehensive payment retry strategy"
  Discussion: "We lost $50k due to silent failures. Never again."

This is a good pattern. The retry layers exist for a reason.
Don't remove them without understanding the incident history.
```

### Example 2: Accelerating Onboarding

**User (Team Lead)**: We just hired a backend engineer. How do we onboard them quickly?

**Archaeologist**:

```
/analyze company/backend
/onboarding junior
```

**Response**:
```
📚 5-DAY ONBOARDING PLAN - Backend (Junior Level)

📍 DAY 1: Database & Schema (2-3 hours)
What: How data is organized
Why: Everything flows through the database
Learn:
  • src/db/schema.ts - Database structure
  • src/db/migrations/ - How schema evolved
  • src/models/ - Data access layer
Key insight: Maria owns most of the database. Ask her about schema.

📍 DAY 2: Request/Response Cycle (3 hours)  
What: How requests enter and responses leave
Why: You'll write endpoints that follow this pattern
Learn:
  • src/api/routes/ - All endpoints
  • src/middleware/ - Authentication, validation
  • src/api/handlers/ - Business logic
Key insight: Defensive middleware exists because of SQL injection incident (#234)

📍 DAY 3: Core Services (3-4 hours)
What: Business logic and domain models
Why: Most of your PR reviews will touch these
Learn:
  • src/services/users/ - User management
  • src/services/billing/ - Billing logic
  • src/services/notifications/ - Alert system
Key insight: Billing service is complex. John wrote most of it (78% commits).

📍 DAY 4: Defensive Patterns (2-3 hours)
What: Why code is structured the way it is
Why: Understanding prevents mistakes
Learn:
  • src/error-handling/ - Error recovery patterns
  • src/cache/ - Caching strategy (prevents database overload)
  • src/rate-limiting/ - Prevents abuse
Key incident: 2022 - Database got hammered. Now we have circuit breaker.

📍 DAY 5: Your First PR (4 hours)
What: Get hands-on and contribute
Why: Best way to learn
Tasks:
  • Fix issue #892 (good-first-issue)
  • Add logging to src/services/users.ts
  • Write unit test for new function
Mentor: Ask Sarah for code review. She knows this area well.

Total time: 14-16 hours over 5 days
After this: Ready for real project work
```

### Example 3: Finding and Removing Dead Code Safely

**User**: We have a lot of legacy code. Can we clean it up?

**Archaeologist**:

```
/analyze company/frontend
/ghost-code
```

**Response**:
```
👻 GHOST CODE CANDIDATES (Safe for Review)

HIGH CONFIDENCE (>85%):

1. src/components/old-dashboard/ (95% confidence)
   Last modified: 1,200 days ago
   Markers: DEPRECATED, LEGACY
   Status: Appears completely unused
   Size: 8 MB (significant cleanup potential)
   Action: Safe to delete after team review

2. src/utils/deprecated-validators.ts (92% confidence)  
   Last modified: 890 days ago
   Markers: TODO: remove in v3, DEPRECATED
   Imports: 0 (no files use it)
   Action: Safe to delete

MEDIUM CONFIDENCE (70-85%):

3. src/hooks/useLegacyAuth.ts (78% confidence)
   Last modified: 450 days ago
   Markers: LEGACY (but still some imports)
   Imports: 2 files in test/ only
   Action: Check with team, likely safe

Recommendation:
1. Create PR with comment on each file:
   "This file marked for deletion. Commit: abc123"
2. Let team review for 1 week
3. Remove if no objections
4. Keep commit message referencing this analysis
```

---

## Important Constraints

### ✅ What Archaeologist Does Well

- ✅ Analyzes public repositories without authentication
- ✅ Works with private repos (if GitHub token provided)
- ✅ Finds patterns in 200+ commits of history
- ✅ Identifies decision points from commit messages
- ✅ Maps knowledge ownership with confidence scores
- ✅ Flags stale code with evidence
- ✅ Calculates bus factor risks
- ✅ Provides evidence-backed answers

### ⚠️ Limitations

- ⚠️ Analyzes last 200 commits only (not full history)
- ⚠️ Heuristic-based pattern matching (not ML-powered yet)
- ⚠️ Cannot access GitHub pull request discussions yet
- ⚠️ May miss decisions from commit messages without keywords
- ⚠️ Cannot see actual code at runtime (only files/timestamps)
- ⚠️ Private repos require GitHub token in .env

### 🔐 Safety & Verification

**Never assume** ghost code is safe to delete:
1. **Always verify** with team and code review
2. **Check tests** - Archaeologist might miss test imports
3. **Search imports** - Use `grep -r` to triple-check
4. **Check comments** - Might be referenced in documentation
5. **Get human approval** - Never delete automatically

**Bus Factor alerts** are warnings, not facts:
1. **Verify with team** - Person might have documented everything
2. **Check for docs** - Even concentrated commits might have docs
3. **Plan carefully** - Don't stress-out the critical person
4. **Schedule knowledge transfer** - Make it a gradual process

---

## Error Handling

### "Cannot connect to analyzer"

```
❌ Error: Connection refused to http://localhost:8000

Fix:
1. Is the backend running?
   docker-compose ps
   
2. Start it if needed:
   docker-compose up -d backend
   
3. Check logs:
   docker-compose logs backend
   
4. Verify port 8000 is free:
   lsof -i :8000
```

### "Repository not found"

```
❌ Error: 404 Not Found - facebook/typo

Fix:
1. Check the repository name
   /analyze facebook/react  ✓
   /analyze facebook/typo   ✗ (doesn't exist)
   
2. Make sure it's public (or provide token)
3. Check GitHub URL: https://github.com/OWNER/REPO
```

### "GitHub rate limited"

```
❌ Error: HTTP 429 - Rate limit exceeded

Fix (add GitHub token to .env):
GITHUB_TOKEN=github_pat_xxxxx

Rate limits:
- Without token: 60 requests/hour  
- With token: 5,000 requests/hour
```

### "Analysis timeout"

```
❌ Error: Timeout - repo too large or network slow

Fix:
- Very large repos (>1000 commits) take longer
- Retry after a minute
- If persistent, check network connection
```

---

## Resources Used

### External APIs
- **GitHub REST API** (free, no authentication needed for public repos)
- **Anthropic Claude 3.5 Sonnet** (free API tier: 10k tokens/day)

### Local Services
- **Analyzer API**: http://localhost:8000
- **Database**: SQLite (local file-based)

### Configuration
- **GitHub Token** (optional): Add to .env for private repos
- **Anthropic Key** (required): Add to OpenClaw config during onboarding

---

## Known Limitations & Future Improvements

### Current (v1.0)
- ✓ 200 commits analyzed per repository
- ✓ Heuristic pattern matching
- ✓ File ownership concentration  
- ✓ Staleness detection
- ✓ Keyword-based decision extraction

### Coming Soon (v1.1-1.3)
- 🔜 Full repository history analysis (>1000 commits)
- 🔜 GitHub PR discussion analysis
- 🔜 LLM-powered semantic analysis
- 🔜 Scar tissue pattern detection (incidents → defensive code)
- 🔜 Agentic PR review
- 🔜 Automated knowledge transfer scheduling
- 🔜 Multi-repository analysis
- 🔜 Jira/Linear integration

---

## Tips for Best Results

1. **Be specific** in questions:
   - ✅ "Why is the cache layer so complex?"
   - ❌ "Tell me about the code"

2. **Check high-risk areas first**:
   - Bus factor alerts show where to focus
   - Knowledge concentration is the biggest risk

3. **Use for onboarding**:
   - Generate plan on Day 1
   - Share with new team member  
   - They follow the journey
   - Reduces ramp-up time by 50%+

4. **Verify before deleting**:
   - Ghost code confidence >85%
   - Double-check with team
   - Keep removal commit for history

5. **Schedule knowledge transfer**:
   - High bus factor? Act now
   - Don't wait for people to leave
   - Pair programming works well

---

## Support & Contributing

- **Issues**: Report bugs on GitHub
- **Questions**: Ask in the repository discussions
- **Improvements**: Submit PRs to enhance the analyzer
- **Custom needs**: Extend with your own skills

---

**Last Updated**: April 27, 2026  
**Status**: Production Ready  
**License**: MIT
