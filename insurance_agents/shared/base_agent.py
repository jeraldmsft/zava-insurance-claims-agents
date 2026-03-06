import uvicorn
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from a2a.types import AgentCard, AgentSkill, AgentCapabilities
from fastapi.responses import JSONResponse
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    def __init__(self, name: str, description: str, port: int, skills: list = None, input_modes: list = None, output_modes: list = None):
        self.name = name
        self.description = description
        self.port = port
        self.skills = skills or []
        self.input_modes = input_modes or ["text"]
        self.output_modes = output_modes or ["text"]
        
        self.agent_card = AgentCard(
            name=self.name,
            description=self.description,
            url=f"http://localhost:{self.port}/",
            version="1.0.0",
            defaultInputModes=self.input_modes,
            defaultOutputModes=self.output_modes,
            capabilities=AgentCapabilities(streaming=False),
            skills=self.skills
        )
        
        self.app = FastAPI(title=self.name, description=self.description)
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        self._register_routes()
    
    def _register_routes(self):
        @self.app.get("/.well-known/agent.json")
        async def get_agent_card():
            card_dict = self.agent_card.model_dump()
            formatted = {
                "name": card_dict.get("name"),
                "description": card_dict.get("description"),
                "url": card_dict.get("url"),
                "version": card_dict.get("version"),
                "defaultInputModes": card_dict.get("default_input_modes", []),
                "defaultOutputModes": card_dict.get("default_output_modes", []),
                "capabilities": card_dict.get("capabilities", {}),
                "skills": [s if isinstance(s, dict) else s.model_dump() for s in (card_dict.get("skills") or [])]
            }
            return JSONResponse(content=formatted)
        
        @self.app.post("/tasks/send")
        async def handle_task(request: dict):
            try:
                message = request.get("message", {})
                text_parts = [p.get("text", "") for p in message.get("parts", []) if p.get("type") == "text"]
                user_message = " ".join(text_parts)
                result = await self.process_task(user_message, request)
                return {"status": "completed", "result": result}
            except Exception as e:
                logger.error(f"Task processing error: {e}")
                return {"status": "failed", "error": str(e)}
        
        @self.app.get("/health")
        async def health():
            return {"status": "healthy", "agent": self.name}
    
    @abstractmethod
    async def process_task(self, message: str, full_request: dict = None) -> str:
        pass
    
    def run(self):
        logger.info(f"🚀 Starting {self.name} on port {self.port}")
        uvicorn.run(self.app, host="0.0.0.0", port=self.port)
