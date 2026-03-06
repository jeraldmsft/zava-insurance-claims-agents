"""MCP Chat Client for Zava Insurance - communicates with MCP servers for database operations."""
import logging
import json
import aiohttp
from typing import Optional

logger = logging.getLogger(__name__)

class MCPChatClient:
    def __init__(self, server_url: str = "http://localhost:8080"):
        self.server_url = server_url.rstrip("/")
        self.session_id = None
    
    async def call_tool(self, tool_name: str, arguments: dict) -> dict:
        try:
            payload = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                },
                "id": 1
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.server_url}/mcp", json=payload) as response:
                    result = await response.json()
                    if "error" in result:
                        logger.error(f"MCP tool error: {result['error']}")
                    return result.get("result", result)
        except Exception as e:
            logger.error(f"MCP call_tool error: {e}")
            return {"error": str(e)}
    
    async def list_tools(self) -> list:
        try:
            payload = {
                "jsonrpc": "2.0",
                "method": "tools/list",
                "params": {},
                "id": 1
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.server_url}/mcp", json=payload) as response:
                    result = await response.json()
                    return result.get("result", {}).get("tools", [])
        except Exception as e:
            logger.error(f"MCP list_tools error: {e}")
            return []
    
    async def get_claim_details(self, claim_id: str) -> Optional[dict]:
        return await self.call_tool("get_claim", {"claim_id": claim_id})
    
    async def get_all_claims(self) -> list:
        result = await self.call_tool("get_all_claims", {})
        return result if isinstance(result, list) else result.get("claims", [])
    
    async def update_claim(self, claim_id: str, updates: dict) -> dict:
        return await self.call_tool("update_claim", {"claim_id": claim_id, "updates": updates})
