#!/bin/bash
# Install Onboarding Archaeologist OpenClaw skill on Linux/macOS
# Usage: ./scripts/install-openclaw-skill.sh [--api-url http://localhost:8000]

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SKILL_DIR="${HOME}/.openclaw/skills/archaeologist"
API_URL="${1:-http://localhost:8000}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${YELLOW}Installing Onboarding Archaeologist OpenClaw Skill${NC}"
echo "Skill directory: $SKILL_DIR"
echo "Backend API: $API_URL"
echo ""

# 1. Create skill directory
echo -e "${GREEN}[1/5]${NC} Creating skill directory..."
mkdir -p "$SKILL_DIR"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Directory created: $SKILL_DIR"
else
    echo -e "${RED}✗${NC} Failed to create directory"
    exit 1
fi

# 2. Copy skill files
echo -e "${GREEN}[2/5]${NC} Copying skill files..."
if [ ! -d "$PROJECT_ROOT/openclaw/skills/archaeologist" ]; then
    echo -e "${RED}✗${NC} Source directory not found: $PROJECT_ROOT/openclaw/skills/archaeologist"
    exit 1
fi

cp "$PROJECT_ROOT/openclaw/skills/archaeologist/skill.yaml" "$SKILL_DIR/" || {
    echo -e "${RED}✗${NC} Failed to copy skill.yaml"
    exit 1
}
cp "$PROJECT_ROOT/openclaw/skills/archaeologist/handlers.py" "$SKILL_DIR/" || {
    echo -e "${RED}✗${NC} Failed to copy handlers.py"
    exit 1
}
cp "$PROJECT_ROOT/openclaw/skills/archaeologist/system_prompt.md" "$SKILL_DIR/" || {
    echo -e "${RED}✗${NC} Failed to copy system_prompt.md"
    exit 1
}

echo -e "${GREEN}✓${NC} Skill files copied"

# 3. Verify backend connectivity
echo -e "${GREEN}[3/5]${NC} Verifying backend connectivity..."
if ! command -v curl &> /dev/null; then
    echo -e "${YELLOW}⚠${NC} curl not found, skipping backend check"
else
    if curl -s -m 5 "$API_URL/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Backend is reachable at $API_URL"
    else
        echo -e "${YELLOW}⚠${NC} Backend not responding at $API_URL (it may start later)"
        echo "   Make sure to start FastAPI before running OpenClaw:"
        echo "   $ uvicorn backend.app.main:app --host 0.0.0.0 --port 8000"
    fi
fi

# 4. Create .env file for skill (optional)
echo -e "${GREEN}[4/5]${NC} Setting up environment..."
SKILL_ENV="$SKILL_DIR/.env"
if [ ! -f "$SKILL_ENV" ]; then
    cat > "$SKILL_ENV" << EOF
# Onboarding Archaeologist OpenClaw Skill Environment
ARCHAEOLOGIST_API_URL=${API_URL}
EOF
    echo -e "${GREEN}✓${NC} Created $SKILL_ENV"
else
    echo -e "${YELLOW}⚠${NC} $SKILL_ENV already exists, skipping"
fi

# 5. Summary
echo -e "${GREEN}[5/5]${NC} Installation complete!"
echo ""
echo -e "${GREEN}✓ Onboarding Archaeologist skill installed successfully${NC}"
echo ""
echo "Next steps:"
echo "1. Set your Telegram bot token:"
echo "   ${YELLOW}export TELEGRAM_BOT_TOKEN='your_bot_token_here'${NC}"
echo ""
echo "2. Start the FastAPI backend (in another terminal):"
echo "   ${YELLOW}cd $PROJECT_ROOT && uvicorn backend.app.main:app --host 0.0.0.0 --port 8000${NC}"
echo ""
echo "3. Start OpenClaw Gateway:"
echo "   ${YELLOW}openclaw run --config openclaw.config.yaml${NC}"
echo ""
echo "4. Send a Telegram message to your bot with:"
echo "   ${YELLOW}/analyze-autonomous owner/repo${NC}"
echo ""
echo "For help, see docs/OPENCLAW_INTEGRATION.md"
