"""Agent discovery service for Zava Insurance multi-agent system."""
import logging
import os
import aiohttp
import json
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

DEFAULT_AGENT_PORTS = {
    "claims_orchestrator": int(os.getenv("A2A_CLAIMS_ORCHESTRATOR_PORT", 8001)),
    "intake_clarifier": int(os.getenv("A2A_INTAKE_CLARIFIER_PORT", 8002)),
    "document_intelligence": int(os.getenv("A2A_DOCUMENT_INTELLIGENCE_PORT", 8003)),
    "coverage_rules_engine": int(os.getenv("A2A_COVERAGE_RULES_ENGINE_PORT", 8004)),
    "communication_agent": int(os.getenv("A2A_COMMUNICATION_AGENT_PORT", 8005)),
    "voice_agent": int(os.getenv("VOICE_LIVE_AGENT_PORT", 8007)),
}

class AgentDiscovery:
    def __init__(self, agent_ports: dict = None):
        self.agent_ports = agent_ports or DEFAULT_AGENT_PORTS
        self.registered_agents: Dict[str, dict] = {}
    
    def get_agent_url(self, agent_name: str) -> str:
        port = self.agent_ports.get(agent_name)
        if not port:
            raise ValueError(f"Unknown agent: {agent_name}")
        return f"http://localhost:{port}"
    
    async def discover_agent(self, agent_name: str) -> Optional[dict]:
        url = self.get_agent_url(agent_name)
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                async with session.get(f"{url}/.well-known/agent.json") as response:
                    if response.status == 200:
                        card = await response.json()
                        self.registered_agents[agent_name] = {
                            "url": url, "card": card, "status": "online"
                        }
                        logger.info(f"🔍 Discovered {agent_name} at {url}")
                        return card
        except Exception as e:
            logger.warning(f"⚠️ Agent {agent_name} not reachable at {url}: {e}")
            self.registered_agents[agent_name] = {"url": url, "status": "offline"}
        return None
    
    async def discover_all(self) -> Dict[str, dict]:
        for name in self.agent_ports:
            await self.discover_agent(name)
        online = {k: v for k, v in self.registered_agents.items() if v.get("status") == "online"}
        logger.info(f"📋 Discovery complete: {len(online)}/{len(self.agent_ports)} agents online")
        return self.registered_agents
    
    def get_online_agents(self) -> Dict[str, dict]:
        return {k: v for k, v in self.registered_agents.items() if v.get("status") == "online"}
