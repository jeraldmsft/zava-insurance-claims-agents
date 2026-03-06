"""A2A Client for inter-agent communication in Zava Insurance claims processing."""
import aiohttp
import logging
import json
import uuid
from typing import Optional

logger = logging.getLogger(__name__)

class A2AClient:
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.timeout = aiohttp.ClientTimeout(total=timeout)
    
    async def get_agent_card(self) -> dict:
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            url = f"{self.base_url}/.well-known/agent.json"
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                raise Exception(f"Failed to fetch agent card: {response.status}")
    
    async def send_task(self, message: str, task_id: str = None, session_id: str = None) -> dict:
        task_id = task_id or str(uuid.uuid4())
        session_id = session_id or str(uuid.uuid4())
        
        payload = {
            "id": task_id,
            "sessionId": session_id,
            "message": {
                "role": "user",
                "parts": [{"type": "text", "text": message}]
            }
        }
        
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            url = f"{self.base_url}/tasks/send"
            logger.info(f"📤 Sending task to {self.base_url}: {message[:100]}...")
            async with session.post(url, json=payload) as response:
                result = await response.json()
                logger.info(f"📥 Response from {self.base_url}: status={result.get('status')}")
                return result
    
    async def check_health(self) -> bool:
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                async with session.get(f"{self.base_url}/health") as response:
                    return response.status == 200
        except Exception:
            return False


class A2AAgentManager:
    def __init__(self):
        self.agents = {}
    
    def register_agent(self, name: str, url: str):
        self.agents[name] = A2AClient(url)
        logger.info(f"✅ Registered agent: {name} at {url}")
    
    async def send_to_agent(self, agent_name: str, message: str) -> dict:
        if agent_name not in self.agents:
            raise ValueError(f"Agent '{agent_name}' not registered")
        return await self.agents[agent_name].send_task(message)
    
    async def discover_agents(self, agent_urls: dict) -> dict:
        discovered = {}
        for name, url in agent_urls.items():
            try:
                client = A2AClient(url)
                card = await client.get_agent_card()
                self.register_agent(name, url)
                discovered[name] = card
                logger.info(f"🔍 Discovered agent: {name} - {card.get('description', 'N/A')}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to discover agent {name} at {url}: {e}")
        return discovered
