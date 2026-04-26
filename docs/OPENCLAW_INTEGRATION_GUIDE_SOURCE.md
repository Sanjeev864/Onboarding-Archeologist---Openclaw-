# OpenClaw Integration Guide for Onboarding Archaeologist
## Complete Step-by-Step Implementation (12 Parts)

---

## PART 1: INSTALL OPENCLAW (5 minutes)

### Step 1.1: Prerequisites Check

```bash
# Check Node.js version (need 22.14+ or Node 24)
node --version
# If you don't have Node, install from: https://nodejs.org/

# Check npm
npm --version

# Check git
git --version
```

### Step 1.2: Install OpenClaw via Official Installer

**For macOS/Linux:**
```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```

**For Windows (PowerShell):**
```powershell
iwr -useb https://openclaw.ai/install.ps1 | iex
```

**Alternative: Manual installation (all platforms)**
```bash
# Clone the repository
git clone https://github.com/openclaw/openclaw.git
cd openclaw

# Install dependencies
npm install

# Run onboarding wizard (creates local config)
npm run openclaw -- onboard --install-daemon
```

### Step 1.3: Verify Installation

```bash
# Check if OpenClaw installed correctly
openclaw --version

# Start the onboarding wizard
openclaw onboard
```

**Expected Output:**
```
✓ OpenClaw installed successfully
✓ Gateway configuration created
✓ Ready to configure AI provider
```

---

## PART 2: CONFIGURE OPENCLAW (10 minutes)

### Step 2.1: Run the Onboarding Wizard

```bash
openclaw onboard --install-daemon
```

This wizard will ask you to:
1. **Choose an AI Provider** - Select "Anthropic" (free API tier)
2. **Enter API Key** - Get free key from https://console.anthropic.com
3. **Choose Channels** - Select "Telegram" for now (easiest to test)
4. **Bot Token** - Create a Telegram bot via @BotFather on Telegram

### Step 2.2: Get Anthropic API Key

1. Go to https://console.anthropic.com
2. Sign up (free tier available)
3. Create a new API key
4. Copy the key (save it safely)
5. Paste it when prompted in the wizard

### Step 2.3: Create Telegram Bot

1. Open Telegram app
2. Search for "@BotFather" bot
3. Send `/start`
4. Send `/newbot`
5. Follow prompts:
   - Bot name: "Archaeologist Bot" (can be anything)
   - Username: "archaeologist_bot" (must be unique, ending with `_bot`)
6. Copy the **token** (looks like: `123456789:ABCDefGHIjklmnoPQRsTUvwxyz`)
7. Paste it when prompted in OpenClaw wizard

### Step 2.4: Verify Configuration

```bash
# Check OpenClaw configuration
openclaw config view

# Start the gateway (this runs your agent)
openclaw gateway
```

**Expected Output:**
```
✓ Gateway started on localhost:8080
✓ Telegram connected
✓ Model provider: Anthropic Claude 3.5 Sonnet
✓ Ready for messages
```

---

## PART 3: CREATE THE ARCHAEOLOGY SKILL (20 minutes)

### Step 3.1: Create Skill Directory Structure

```bash
# Navigate to OpenClaw skills directory
cd ~/.openclaw/skills

# Create Archaeology skill folder
mkdir archaeologist
cd archaeologist

# Create required structure
mkdir scripts
mkdir resources

# Create main skill file
touch SKILL.md
```

### Step 3.2: Write SKILL.md (Core Skill Definition)

**File:** `~/.openclaw/skills/archaeologist/SKILL.md`

```yaml
---
name: "Code Archaeologist"
description: >
  Excavates git history to reveal architectural decisions, knowledge ownership,
  ghost code, and scar tissue patterns. Use when you need to understand:
  - Why code decisions were made
  - Who owns what areas of the codebase
  - Dead or abandoned code
  - Over-engineered defensive patterns
  
  Commands: /analyze <owner/repo>, /ask <question>
  
version: "1.0.0"
author: "Your Name"
tools:
  - exec
  - browser
  - fetch
tags:
  - codebase
  - git
  - analysis
  - architecture

skill-invocation: true
disable-model-invocation: false
---

# Code Archaeologist

## Purpose

This skill lets you analyze any GitHub repository to understand its decision history,
knowledge concentration, code quality patterns, and critical risks.

It's designed to accelerate developer onboarding and reduce bus factor risks.

## Tools & APIs Used

- **GitHub API** (free tier, no token required for public repos)
- **Local Analyzer** (running on localhost:8000)
- **Claude 3.5 Sonnet** (Anthropic free API)

## When to Use

Ask the archaeologist when you need to:
- Understand why a major architectural decision was made
- Identify who owns specific parts of the codebase
- Find dead or deprecated code candidates
- Locate over-engineered defensive patterns and trace them to incidents
- Create an onboarding plan for a new developer
- Check bus factor risks (critical knowledge concentration)

## Step-by-Step Instructions

### Basic Analysis Flow

1. **User provides repo**: "Analyze facebook/react"
   - Extract owner and repo name
   - Call the analyzer API on localhost:8000
   - Wait for analysis to complete (30-60 seconds)

2. **Analyzer returns findings**:
   - Decision signals (architectural decisions with confidence)
   - Ownership data (who owns what, concentration metrics)
   - Ghost code (dead/stale code candidates)
   - Bus factor alerts (critical person risks)

3. **Present results to user**:
   - Show top 5 decisions with confidence scores
   - List high-risk knowledge concentration areas
   - Flag ghost code for review
   - Highlight critical bus factor risks

4. **Answer follow-up questions**:
   - "Why was [feature] built this way?"
   - "Who should I ask about the database module?"
   - "Is this code safe to delete?"
   - "What areas are single-person dependencies?"

### Detailed Workflow

#### Command: /analyze

**User Input**: `/analyze facebook/react`

**Steps**:
1. Parse the owner and repo from the input
2. Make HTTP POST to: `http://localhost:8000/api/analyze`
3. Body: `{"owner": "facebook", "repo": "react", "branch": ""}`
4. Wait for response (timeout: 90 seconds)
5. Extract from response:
   - decisions (list of architectural decisions)
   - ownership (knowledge ownership with risk levels)
   - ghost_code (stale/dead code candidates)
   - repository_id (save this for follow-up questions)

6. **Format the response for Telegram**:
   ```
   📊 Analysis of facebook/react
   
   🏛️ ARCHITECTURAL DECISIONS (Top 5)
   • [Decision 1] - 95% confidence
     Evidence: [commit message]
   • [Decision 2] - 87% confidence
     Evidence: [commit message]
   ... (limit to 5)
   
   👥 KNOWLEDGE CONCENTRATION (High Risk Areas)
   🔴 HIGH RISK: auth/ owned by john_doe (78% commits)
   🟡 MEDIUM: database/ owned by jane_smith (62% commits)
   ... (only show HIGH and MEDIUM risk)
   
   👻 GHOST CODE (Stale candidates)
   • src/legacy/v1-api.js (last touched 800 days ago)
   • src/utils/old-utils.ts (contains: DEPRECATED, LEGACY markers)
   ... (limit to 5)
   
   ⚠️ BUS FACTOR ALERT
   Only john_doe understands: auth, security, key-rotation
   Recommendation: Schedule knowledge transfer session
   ```

#### Command: /ask

**User Input**: `/ask "Why is there so much error handling in the auth module?"`

**Steps**:
1. Extract the question from the command
2. Get the repository_id from the last analysis
3. Make HTTP POST to: `http://localhost:8000/api/oracle`
4. Body:
   ```json
   {
     "repository_id": 1,
     "question": "Why is there so much error handling in the auth module?"
   }
   ```
5. Response contains:
   - answer (synthesized answer from git history)
   - evidence (list of specific commits/PRs that support the answer)

6. **Format for Telegram**:
   ```
   🧠 Oracle Answer:
   
   [Full answer from Claude with git history context]
   
   📌 EVIDENCE:
   • Commit abc123: "Fix auth timeout issues - add retry logic"
   • PR #5234: "Add circuit breaker pattern to prevent cascade failures"
   • Issue #892: "Database connection drops cause login hangs"
   
   Click links to see full details on GitHub
   ```

## Examples

### Example 1: Understanding Architectural Decisions

**User**: "Analyze facebook/react"

**Archaeologist**:
```
✓ Analyzing 200 recent commits...

🏛️ MAJOR DECISIONS
1. Use JSX for component definition (95% confidence)
   Reason: "Introduced JSX for better component readability"
   
2. Implement virtual DOM (92% confidence)
   Reason: "Virtual DOM provides better performance and batch updates"
   
3. Fiber architecture (90% confidence)
   Reason: "Redesigned scheduler for better performance + async rendering"
```

### Example 2: Checking for Dead Code

**User**: "Find ghost code in facebook/react"

**Archaeologist**:
```
👻 GHOST CODE FINDINGS

⚠️ Review these for potential removal:
• src/renderers/dom/legacy/ReactLegacyElement.js
  Last touched: 312 days ago
  Markers: DEPRECATED, LEGACY
  Risk: Low (may still be in use)

• src/test/utils.js
  Last touched: 527 days ago
  Markers: UNUSED, TODO: remove after v19
  Risk: Medium (marked for deletion)
```

### Example 3: Checking Bus Factor

**User**: "Who owns the database layer in this codebase?"

**Archaeologist**:
```
👤 DATABASE LAYER OWNERSHIP

Primary: alice@company.com (87 commits, 73% contribution)
Secondary: bob@company.com (21 commits, 18% contribution)
Tertiary: charlie@company.com (11 commits, 9% contribution)

⚠️ BUS FACTOR: HIGH
- Alice is the single point of failure
- Only she modified core database connection logic
- Last change: 3 weeks ago

Recommendation: Schedule knowledge transfer to Bob and Charlie
```

## Important Constraints

1. **No Private Repos Without Token**: 
   - Public repos: Works out of the box
   - Private repos: Requires GitHub token in .env

2. **Time Limits**:
   - Analysis timeout: 90 seconds max
   - If repo >500 commits: May take longer

3. **Safe Deletions Only**:
   - NEVER recommend deletion without evidence
   - Always flag "Review carefully" for ghost code
   - Check for hidden references (imports, dynamic loading)

4. **Confidence Scores**:
   - >85%: High confidence decision
   - 60-85%: Medium confidence decision
   - <60%: Low confidence (show but note uncertainty)

5. **Privacy**:
   - Don't expose full author emails (use first name only)
   - Don't analyze private repos without explicit permission
   - Cache results locally (don't re-analyze immediately)

## Error Handling

If the analyzer is not running:
```
❌ Error: Cannot connect to analyzer on localhost:8000

Fix steps:
1. Start the Onboarding Archaeologist backend:
   cd /path/to/onboarding-archaeologist
   docker-compose up -d
   
2. Verify it's running:
   curl http://localhost:8000/health
   
3. Try the analysis again
```

If rate limited:
```
⏳ GitHub rate limited (public tier: 60 requests/hour)

Waiting for rate limit reset...
Retry analysis in 5 minutes.
```

## Commands

- `/analyze <owner>/<repo>` - Run full analysis
- `/ask <question>` - Ask oracle about last analyzed repo
- `/bus-factor` - Show bus factor risks only
- `/decisions` - Show architectural decisions only
- `/ghost-code` - Show dead code candidates only
- `/onboarding <level>` - Generate onboarding path (junior/mid/senior)

## Resources Used

- GitHub REST API (free tier)
- Local Analyzer API: http://localhost:8000
- Anthropic Claude 3.5 Sonnet (free API tier)

## Known Limitations

- Analyzes last 200 commits only (not full history)
- Heuristic-based (not ML-powered yet)
- No private repo support without GitHub token
- No pull request discussion analysis yet (coming soon)

---

# End of Skill Definition
```

### Step 3.3: Create Helper Scripts

**File:** `~/.openclaw/skills/archaeologist/scripts/analyze.sh`

```bash
#!/bin/bash
# Script to call the analyzer API

OWNER=$1
REPO=$2
BRANCH=${3:-""}

# Check if analyzer is running
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "❌ Analyzer not running on localhost:8000"
    exit 1
fi

# Call the analyze endpoint
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d "{
    \"owner\": \"$OWNER\",
    \"repo\": \"$REPO\",
    \"branch\": \"$BRANCH\"
  }"
```

**File:** `~/.openclaw/skills/archaeologist/scripts/oracle.sh`

```bash
#!/bin/bash
# Script to ask oracle questions

REPO_ID=$1
QUESTION=$2

curl -X POST http://localhost:8000/api/oracle \
  -H "Content-Type: application/json" \
  -d "{
    \"repository_id\": $REPO_ID,
    \"question\": \"$QUESTION\"
  }"
```

### Step 3.4: Create Resources

**File:** `~/.openclaw/skills/archaeologist/resources/API_REFERENCE.md`

```markdown
# Archaeologist API Reference

## Endpoints

### POST /api/analyze
Analyze a GitHub repository

**Request**:
```json
{
  "owner": "facebook",
  "repo": "react",
  "branch": "main"
}
```

**Response**:
```json
{
  "repository_id": 1,
  "owner": "facebook",
  "repo": "react",
  "decisions": [...],
  "ownership": [...],
  "ghost_code": [...]
}
```

### POST /api/oracle
Ask questions about analyzed repos

**Request**:
```json
{
  "repository_id": 1,
  "question": "Why was JSX introduced?"
}
```

**Response**:
```json
{
  "answer": "...",
  "evidence": [...]
}
```

For full API docs, visit: http://localhost:8000/docs
```

---

## PART 4: CONFIGURE SKILL IN OPENCLAW (5 minutes)

### Step 4.1: Enable the Skill

```bash
# Edit OpenClaw configuration
nano ~/.openclaw/openclaw.json
```

Find the `skills` section and add:

```json
{
  "skills": {
    "entries": {
      "archaeologist": {
        "enabled": true,
        "env": {}
      }
    }
  }
}
```

### Step 4.2: Verify Skill is Loaded

```bash
# List all skills
openclaw skills list

# You should see:
# ✓ archaeologist (Code Archaeologist)
```

---

## PART 5: START THE ANALYZER BACKEND (5 minutes)

### Step 5.1: Start Backend in Docker

```bash
cd /path/to/onboarding-archaeologist

# Build and start
docker-compose up -d --build

# Verify it's running
curl http://localhost:8000/health

# Expected response:
# {"status":"ok","time":"2026-04-27T12:34:56.789Z"}
```

### Step 5.2: Check Logs

```bash
# View backend logs
docker-compose logs -f backend

# Should show:
# backend  | Uvicorn running on http://0.0.0.0:8000
```

### Step 5.3: Alternative: Run Backend Locally

If Docker isn't available:

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## PART 6: START OPENCLAW GATEWAY (5 minutes)

### Step 6.1: Run the Gateway

```bash
# In a new terminal
openclaw gateway
```

Expected output:
```
✓ Gateway started on localhost:8080
✓ Telegram connected: @archaeologist_bot
✓ Model: Claude 3.5 Sonnet (Anthropic)
✓ Skills loaded: 49 bundled + archaeologist (custom)
✓ Ready for messages
```

### Step 6.2: Keep Gateway Running

The gateway must stay running for the agent to receive messages. Options:

**Option A: Terminal with `screen` (Linux/Mac)**
```bash
screen -S openclaw-gateway
openclaw gateway
# Press Ctrl+A then D to detach
```

**Option B: Background service (recommended)**
```bash
openclaw onboard --install-daemon
# This creates a systemd service that auto-starts
```

**Option C: Docker container (production)**
```bash
docker run -d \
  -v ~/.openclaw:/root/.openclaw \
  -p 8080:8080 \
  openclaw:latest \
  openclaw gateway
```

---

## PART 7: TEST THE INTEGRATION (10 minutes)

### Step 7.1: Send Test Message to Bot

1. Open Telegram
2. Find your bot (search username, e.g., `@archaeologist_bot`)
3. Send: `/start`
4. Bot should respond with welcome message

### Step 7.2: Test Archaeology Skill

**Test 1: Simple Analysis**

```
User: /analyze facebook/react
```

**Expected Response** (in Telegram):
```
🔍 Analyzing facebook/react...
(This may take 30-60 seconds)

✓ Analysis complete!

📊 FINDINGS:

🏛️ Architectural Decisions
• Virtual DOM architecture - 95% confidence
• JSX for components - 92% confidence
...

👥 Knowledge Concentration
🔴 HIGH: john_doe owns React Core (78%)
...

👻 Ghost Code
• src/renderers/dom/legacy/ (800 days old)
...
```

**Test 2: Ask Oracle**

```
User: Who owns the scheduler?
```

**Expected Response**:
```
🧠 Oracle Answer:

Dan Abramov and Andrew Clark are the primary authors
of the scheduler module. Evidence:
• Commit abc123: "Implement Fiber scheduler"
• PR #9999: "Add priority levels to scheduler"
```

**Test 3: Check Bus Factor**

```
User: /bus-factor
```

**Expected Response**:
```
⚠️ BUS FACTOR ANALYSIS

CRITICAL RISK: Dan Abramov
- Owns: Scheduler, Priority System, Batching
- Concentration: 89% of commits in these areas
- Risk Level: CRITICAL

Recommendation: Schedule knowledge transfer session
```

---

## PART 8: CREATE TELEGRAM COMMANDS (5 minutes)

### Step 8.1: Set Up Bot Commands in BotFather

Go back to @BotFather in Telegram:

```
/setcommands

Then paste:

analyze - Analyze a GitHub repository
ask - Ask question about last analyzed repo
bus-factor - Show bus factor risks
decisions - Show architectural decisions only
ghost-code - Show ghost code candidates
onboarding - Create onboarding journey
help - Show all available commands
```

### Step 8.2: Create Help Command

Send to your bot:

```
/help
```

Should return:
```
📚 Code Archaeologist Help

🔍 Commands:
/analyze <owner>/<repo> - Full repository analysis
/ask <question> - Ask about last analyzed repo
/bus-factor - Check knowledge concentration risks
/decisions - Show key architectural decisions
/ghost-code - Find dead/stale code
/onboarding <level> - Create onboarding path
  Levels: junior, mid, senior

Examples:
/analyze facebook/react
/ask "Why was virtual DOM introduced?"
/bus-factor
```

---

## PART 9: WEBHOOK INTEGRATION (Optional, 15 minutes)

### Step 9.1: Enable GitHub Webhooks

Modify `~/.openclaw/skills/archaeologist/SKILL.md` to add webhook support:

```yaml
---
name: "Code Archaeologist"
description: "... [same as before]"
tools:
  - exec
  - browser
  - fetch
  - webhooks  # Add this
---
```

### Step 9.2: Create Webhook Handler

**File:** `backend/app/routes/webhooks.py`

```python
from fastapi import APIRouter, Request, HTTPException
import hmac
import hashlib

router = APIRouter()

@router.post("/webhooks/github")
async def github_webhook(request: Request):
    """
    Receive GitHub webhook for push events.
    Automatically re-analyze repo on push.
    """
    
    # Validate webhook signature
    signature = request.headers.get("x-hub-signature-256")
    if not signature:
        raise HTTPException(status_code=401, detail="Missing signature")
    
    payload = await request.body()
    expected = "sha256=" + hmac.new(
        os.getenv("GITHUB_WEBHOOK_SECRET").encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(signature, expected):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Parse event
    data = await request.json()
    
    if data.get("action") == "pushed":
        owner = data["repository"]["owner"]["login"]
        repo = data["repository"]["name"]
        
        # Queue re-analysis
        asyncio.create_task(
            RepositoryAnalyzer().analyze(owner, repo)
        )
        
        # Notify team on Telegram
        notify_telegram(
            f"🔄 Re-analyzing {owner}/{repo} after push...",
            webhook_secret
        )
    
    return {"status": "received"}
```

### Step 9.3: Register Webhook with GitHub

```bash
# Get webhook URL (if hosted on VPS)
WEBHOOK_URL="https://your-domain.com/webhooks/github"

# Generate secret
WEBHOOK_SECRET=$(openssl rand -hex 32)

# Register with GitHub API (requires token)
curl -X POST \
  https://api.github.com/repos/OWNER/REPO/hooks \
  -H "Authorization: token YOUR_GITHUB_TOKEN" \
  -d "{
    \"name\": \"web\",
    \"active\": true,
    \"events\": [\"push\"],
    \"config\": {
      \"url\": \"$WEBHOOK_URL\",
      \"secret\": \"$WEBHOOK_SECRET\",
      \"content_type\": \"json\"
    }
  }"
```

---

## PART 10: ADVANCED FEATURES (Optional)

### Step 10.1: Multi-Channel Support

The Archaeologist skill works on any OpenClaw channel. Set up more:

**Discord Integration:**
```bash
# Install Discord channel
openclaw channels install discord

# Get bot token from Discord Developer Portal
# Add to ~/.openclaw/openclaw.json:
{
  "channels": {
    "discord": {
      "enabled": true,
      "token": "YOUR_DISCORD_BOT_TOKEN"
    }
  }
}
```

**Slack Integration:**
```bash
# Install Slack channel
openclaw channels install slack

# Get bot token from Slack app settings
# Add to ~/.openclaw/openclaw.json:
{
  "channels": {
    "slack": {
      "enabled": true,
      "token": "YOUR_SLACK_BOT_TOKEN"
    }
  }
}
```

**WhatsApp Integration:**
```bash
# WhatsApp requires Twilio account (free trial available)
openclaw channels install whatsapp

# Get credentials from Twilio dashboard
# Add to ~/.openclaw/openclaw.json:
{
  "channels": {
    "whatsapp": {
      "enabled": true,
      "account_sid": "YOUR_TWILIO_ACCOUNT_SID",
      "auth_token": "YOUR_TWILIO_AUTH_TOKEN",
      "from_number": "+1234567890"
    }
  }
}
```

### Step 10.2: Custom Memory Store

Add persistent memory for context across conversations:

**File:** `~/.openclaw/MEMORY.md`

```markdown
# Archaeology Agent Memory

## Known Repositories

### facebook/react
- Analyzed: 2026-04-27
- Key findings: Virtual DOM, Fiber architecture
- Known owners: Dan Abramov, Andrew Clark
- High risk areas: Scheduler, Batching

### kubernetes/kubernetes  
- Analyzed: 2026-04-26
- Key findings: Go, distributed consensus
- Known owners: Kubernetes team
- High risk areas: Control plane

## Team Knowledge Map

- Backend team: Prefers Go, PostgreSQL
- Frontend team: Specializes in React, TypeScript
- DevOps team: Kubernetes, Infrastructure

## Common Questions

Q: How to analyze a private repo?
A: Add GitHub token to .env, then use /analyze normally

Q: How long does analysis take?
A: 30-60 seconds for most repos, up to 2 minutes for large ones
```

### Step 10.3: Agentic Code Review

Create a skill to automatically review PRs:

**File:** `~/.openclaw/skills/archaeologist/SKILL.md` - Add new section:

```yaml
## Advanced: Agentic PR Review

When a developer submits PR, archaeologist can:
1. Analyze affected files
2. Check against known patterns
3. Flag risky changes
4. Suggest improvements
5. Auto-comment on GitHub

Usage: `/review <github-pr-url>`

This requires GitHub token and approval from org admins.
```

### Step 10.4: Bus Factor Monitoring

Set up periodic alerts:

**File:** `~/.openclaw/skills/archaeologist/SKILL.md` - Add:

```yaml
## Advanced: Automated Bus Factor Monitoring

When bus factor risk increases:
1. Detect concentration increase (>80%)
2. Flag critical person
3. Send alert to team lead
4. Suggest knowledge transfer
5. Track over time

Schedule: Daily at 9 AM
Notification: Telegram / Slack / Email

Setup:
  - Add cron job to openclaw config
  - Enable notifications in channels
  - Set up escalation rules
```

---

## PART 11: PRODUCTION DEPLOYMENT (20 minutes)

### Step 11.1: Deploy to Cloud VPS

**Using Railway (recommended, free tier):**

1. Go to https://railway.app
2. Sign up with GitHub
3. Create new project
4. Connect to your Onboarding Archaeologist repo
5. Add environment variables:
   ```
   ANTHROPIC_API_KEY=your_key
   GITHUB_TOKEN=your_token  # optional
   DATABASE_URL=postgresql://...
   ```
6. Deploy automatically

**Using Render (alternative):**

1. Go to https://render.com
2. Create new Web Service
3. Connect GitHub repo
4. Render auto-detects Docker setup
5. Deploy with one click

**Using DigitalOcean (more control):**

```bash
# Create VPS (4GB RAM, $6/month)
# SSH in:
ssh root@your_vps_ip

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Clone your repo
git clone https://github.com/YOUR_USERNAME/onboarding-archaeologist.git
cd onboarding-archaeologist

# Create .env
nano .env
# Add: ANTHROPIC_API_KEY, etc.

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Check logs
docker-compose logs -f backend

# Set up auto-restart
sudo systemctl enable docker
```

### Step 11.2: Enable SSL/TLS

If webhooks need HTTPS:

```bash
# Using Let's Encrypt + Certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot certonly --standalone -d your-domain.com

# Update nginx config
# Or use Caddy (auto HTTPS):
docker pull caddy
# Configure Caddy to reverse proxy your API
```

### Step 11.3: Set Up Monitoring

```bash
# Add Prometheus metrics
# File: backend/app/middleware/metrics.py

from prometheus_client import Counter, Histogram

analysis_requests = Counter(
    'archaeology_analyses_total',
    'Total analyses performed'
)

analysis_duration = Histogram(
    'archaeology_analysis_seconds',
    'Time spent analyzing repo'
)

# Set up alerting
# If error rate > 5%, send alert
# If response time > 60s, send alert
```

### Step 11.4: Backup Strategy

```bash
# Daily backup of database
0 2 * * * docker-compose exec db mysqldump archaeologist > /backups/db_$(date +\%Y\%m\%d).sql

# Weekly backup to S3
0 3 * * 0 aws s3 sync /backups s3://your-bucket/archaeologist-backups/
```

---

## PART 12: TROUBLESHOOTING & SUPPORT

### Issue 1: Analyzer Not Running

**Error**: `Cannot connect to http://localhost:8000`

**Solutions**:
```bash
# Check if backend is running
docker-compose ps

# If not, start it
docker-compose up -d backend

# Check logs
docker-compose logs backend

# If port conflict
lsof -i :8000  # Find what's using port
kill -9 <PID>  # Kill the process
```

### Issue 2: Telegram Bot Not Responding

**Error**: Message sent but no response

**Solutions**:
```bash
# Check if OpenClaw gateway is running
pgrep -f "openclaw gateway"

# Check Telegram token is correct
grep "telegram" ~/.openclaw/openclaw.json

# Restart gateway
pkill -f "openclaw gateway"
openclaw gateway

# Check for errors
tail -f ~/.openclaw/logs/gateway.log
```

### Issue 3: GitHub Rate Limiting

**Error**: `HTTP 429 Too Many Requests`

**Solutions**:
```bash
# Add GitHub token to .env
echo "GITHUB_TOKEN=your_token" >> .env
docker-compose restart backend

# Rate limits with token:
# Public repo: 5000 requests/hour
# Authenticated: 15000 requests/hour
```

### Issue 4: Skill Not Loading

**Error**: Skill doesn't appear in `/help`

**Solutions**:
```bash
# Check skill file exists
ls ~/.openclaw/skills/archaeologist/SKILL.md

# Check YAML syntax (no tabs!)
cat ~/.openclaw/skills/archaeologist/SKILL.md | head -20

# Verify in config
grep archaeologist ~/.openclaw/openclaw.json

# Restart gateway
openclaw gateway
```

### Issue 5: LLM API Errors

**Error**: `Authentication failed` or `Rate limit exceeded`

**Solutions**:
```bash
# Check API key
echo $ANTHROPIC_API_KEY

# Verify key is valid
curl https://api.anthropic.com/v1/models \
  -H "x-api-key: $ANTHROPIC_API_KEY"

# Check quota on console.anthropic.com
# Free tier: 10k tokens/day
# Upgrade if needed
```

### Debugging Commands

```bash
# View all gateway logs
openclaw logs tail 100

# Check skill diagnostics
openclaw skills doctor archaeologist

# Validate SKILL.md
openclaw skills validate ~/.openclaw/skills/archaeologist

# Test analyzer API directly
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"owner":"facebook","repo":"react","branch":""}'

# Test oracle API
curl -X POST http://localhost:8000/api/oracle \
  -H "Content-Type: application/json" \
  -d '{"repository_id":1,"question":"Why?"}'
```

---

## QUICK REFERENCE

### Essential Commands

```bash
# Start OpenClaw
openclaw gateway

# List skills
openclaw skills list

# Install skill from ClawHub
openclaw skills install skill-name

# View configuration
openclaw config view

# Edit configuration
nano ~/.openclaw/openclaw.json

# View logs
openclaw logs tail

# Start backend analyzer
docker-compose up -d backend

# Stop all services
docker-compose down

# Restart services
docker-compose restart
```

### File Locations

```
~/.openclaw/                    # OpenClaw home directory
~/.openclaw/openclaw.json       # Main configuration
~/.openclaw/skills/             # Skills directory
~/.openclaw/skills/archaeologist/SKILL.md  # Your skill
~/.openclaw/workspace/          # Session data
~/.openclaw/logs/               # Log files
```

### Common Workflows

**Setup (One-time)**:
1. `openclaw onboard --install-daemon`
2. Create `archaeologist` skill
3. Start backend: `docker-compose up -d`
4. Test in Telegram: `/analyze facebook/react`

**Daily Use**:
1. Talk to bot in Telegram
2. Use commands: `/analyze`, `/ask`, `/bus-factor`
3. Get instant insights about repos

**Adding New Features**:
1. Edit `SKILL.md`
2. Restart gateway: `openclaw gateway`
3. Test in Telegram
4. Deploy to production

---

## SUCCESS CHECKLIST

- [x] OpenClaw installed and running
- [x] Anthropic API key configured
- [x] Telegram bot created and connected
- [x] Archaeologist skill created and enabled
- [x] Backend analyzer running on localhost:8000
- [x] Gateway running and receiving messages
- [x] Test analysis successful (`/analyze facebook/react`)
- [x] Test oracle working (`/ask "...?"`)
- [x] Bus factor alerts working
- [x] Production deployment configured
- [x] Monitoring and alerting set up
- [x] Backup strategy in place

---

## NEXT STEPS

1. **Customize the Skill**
   - Modify SKILL.md for your use case
   - Add company-specific analysis
   - Create custom commands

2. **Add More Channels**
   - Discord (for dev teams)
   - Slack (for enterprise)
   - WhatsApp (for mobile-first)

3. **Implement Advanced Features**
   - Agentic PR reviews
   - Bus factor monitoring
   - GitHub webhook auto-analysis
   - Knowledge transfer scheduling

4. **Scale to Enterprise**
   - Multi-repo analysis
   - Team-level bus factor tracking
   - Integration with Jira/Linear
   - Custom metrics and dashboards

---

## SUPPORT & COMMUNITY

- **OpenClaw Docs**: https://docs.openclaw.ai
- **OpenClaw GitHub**: https://github.com/openclaw/openclaw
- **OpenClaw Discord**: https://discord.gg/openclaw
- **Onboarding Archaeologist**: https://github.com/YOUR_REPO

---

**Document Version**: 1.0  
**Last Updated**: April 27, 2026  
**Status**: Ready for Implementation
