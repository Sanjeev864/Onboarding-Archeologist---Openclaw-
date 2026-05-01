#!/bin/bash
# OpenClaw Agent Commands Wrapper
# Routes commands to agent endpoints

set -e

BACKEND_URL="http://localhost:8000"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Command router
case "$1" in
    analyze-autonomous)
        if [ -z "$2" ]; then
            echo "Usage: analyze-autonomous <owner>/<repo>"
            exit 1
        fi
        OWNER=$(echo $2 | cut -d'/' -f1)
        REPO=$(echo $2 | cut -d'/' -f2)
        
        echo -e "${BLUE}🤖 Analyzing: $OWNER/$REPO${NC}"
        curl -s -X POST "$BACKEND_URL/api/v2/analyze-autonomous?owner=$OWNER&repo=$REPO" | jq '.'
        ;;
    
    agent-trace)
        if [ -z "$2" ]; then
            echo "Usage: agent-trace <agent_name>"
            echo "Available agents: perception, decisions, ownership, ghost-code, bus-factor, scar-tissue, onboarding"
            exit 1
        fi
        
        echo -e "${BLUE}📊 Agent Trace: $2${NC}"
        curl -s "$BACKEND_URL/api/v2/agent-decision-trace/$2" | jq '.'
        ;;
    
    agent-status)
        echo -e "${BLUE}🚦 Agent Status${NC}"
        curl -s "$BACKEND_URL/api/v2/agent-status" | jq '.agents | to_entries[] | {agent: .key, state: .value.state, steps: .value.steps_executed}'
        ;;
    
    agent-feedback)
        if [ -z "$4" ]; then
            echo "Usage: agent-feedback <agent_id> <rating> <comment>"
            exit 1
        fi
        
        AGENT_ID=$2
        RATING=$3
        COMMENT="$4"
        
        # Determine feedback type
        if (( $(echo "$RATING > 0.7" | bc -l) )); then
            FEEDBACK_TYPE="positive"
        elif (( $(echo "$RATING < 0.3" | bc -l) )); then
            FEEDBACK_TYPE="negative"
        else
            FEEDBACK_TYPE="partial"
        fi
        
        echo -e "${BLUE}📝 Submitting feedback to $AGENT_ID${NC}"
        curl -s -X POST "$BACKEND_URL/api/v2/submit-agent-feedback" \
            -H "Content-Type: application/json" \
            -d "{
                \"agent_id\": \"$AGENT_ID\",
                \"execution_id\": \"exec_$(date +%s)\",
                \"feedback_type\": \"$FEEDBACK_TYPE\",
                \"feedback_text\": \"$COMMENT\",
                \"rating\": $RATING
            }" | jq '.'
        ;;
    
    onboarding)
        LEVEL=${2:-junior}
        HOURS=${3:-40}
        
        echo -e "${BLUE}🎓 Generating Onboarding Path${NC}"
        echo "Level: $LEVEL, Hours: $HOURS"
        curl -s -X POST "$BACKEND_URL/api/v2/onboarding-autonomous?level=$LEVEL&time_available_hours=$HOURS" | jq '.'
        ;;
    
    help)
        echo "OpenClaw Agent Commands:"
        echo ""
        echo "  analyze-autonomous <owner>/<repo>  - Full analysis with all agents"
        echo "  agent-trace <name>                 - View agent decision reasoning"
        echo "  agent-status                       - Check all agents' state"
        echo "  agent-feedback <id> <rating> <msg> - Train agent with feedback"
        echo "  onboarding <level> [hours]        - Generate learning path"
        echo ""
        echo "Available agents:"
        echo "  perception, decisions, ownership, ghost-code, bus-factor, scar-tissue, onboarding"
        ;;
    
    *)
        echo "Unknown command: $1"
        echo "Use 'help' for usage information"
        exit 1
        ;;
esac