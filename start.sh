#!/bin/bash
set -e

echo "🚀 Starting Zava Insurance Multi-Agent System..."

# Start MCP Server
echo "📦 Starting Cosmos MCP Server on port 8080..."
cd /app/azure-cosmos-mcp-server/python
python cosmos_server.py &
sleep 2

# Start Core Agents
cd /app/insurance_agents

echo "🎯 Starting Claims Orchestrator on port 8001..."
python -m agents.claims_orchestrator &
sleep 1

echo "🔍 Starting Intake Clarifier on port 8002..."
python -m agents.intake_clarifier &
sleep 1

echo "📄 Starting Document Intelligence on port 8003..."
python -m agents.document_intelligence_agent &
sleep 1

echo "🛡️ Starting Coverage Rules Engine on port 8004..."
python -m agents.coverage_rules_engine &
sleep 1

echo "📧 Starting Communication Agent on port 8005..."
python -m agents.communication_agent &
sleep 1

# Start Voice Agent
echo "🎤 Starting Voice Agent on port 8007..."
cd /app/insurance_agents/agents/client_live_voice_agent
python fastapi_server.py &
sleep 1

# Start Dashboard (foreground - keeps container alive)
echo "📊 Starting Dashboard on port 3000..."
cd /app/insurance_agents/insurance_agents_registry_dashboard
python app.py
