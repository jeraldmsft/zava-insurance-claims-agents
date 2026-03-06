"""
Zava Insurance Voice Agent FastAPI Server
Provides real-time voice interface for claim status inquiries.
"""
import sys
import os
import logging
import json
import uvicorn
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from a2a.types import AgentCard, AgentSkill, AgentCapabilities

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

logging.basicConfig(level=logging.INFO, format='🎤 [ZAVA-VOICE] %(asctime)s - %(levelname)s - %(message)s', datefmt="%H:%M:%S")
logger = logging.getLogger(__name__)

app = FastAPI(title="Zava Insurance Voice Agent", description="Voice-enabled claims status assistant")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

STATIC_DIR = Path(__file__).parent / "static"
PORT = int(os.getenv("VOICE_LIVE_AGENT_PORT", 8007))

agent_card = AgentCard(
    name="ZavaVoiceAgent",
    description="Zava Insurance voice-enabled claims assistant with real-time voice interaction",
    url=f"http://localhost:{PORT}/",
    version="1.0.0",
    defaultInputModes=["audio", "text"],
    defaultOutputModes=["audio", "text"],
    capabilities=AgentCapabilities(streaming=True),
    skills=[
        AgentSkill(id="voice_claim_status", name="Voice Claim Status", description="Check claim status via voice", tags=["voice", "claims", "status"]),
    ]
)

@app.get("/.well-known/agent.json")
async def get_agent_card():
    return JSONResponse(content={
        "name": agent_card.name,
        "description": agent_card.description,
        "url": agent_card.url,
        "version": agent_card.version,
        "id": "client_live_voice_agent",
        "defaultInputModes": ["audio", "text"],
        "defaultOutputModes": ["audio", "text"],
        "capabilities": {"audio": True, "voice": True, "streaming": True, "real_time": True},
        "skills": [{"id": s.id, "name": s.name, "description": s.description, "tags": s.tags} for s in agent_card.skills]
    })

@app.get("/")
async def serve_voice_interface():
    html_path = STATIC_DIR / "claims_voice_client.html"
    if html_path.exists():
        return FileResponse(html_path, media_type="text/html")
    return HTMLResponse("<html><body><h1>Zava Insurance Voice Agent</h1><p>Voice client not found.</p></body></html>")

@app.get("/{filename}.js")
async def serve_js(filename: str):
    js_path = STATIC_DIR / f"{filename}.js"
    if js_path.exists():
        return FileResponse(js_path, media_type="application/javascript")
    raise HTTPException(status_code=404, detail=f"{filename}.js not found")

@app.get("/health")
async def health():
    return {"status": "healthy", "agent": "ZavaVoiceAgent"}

if __name__ == "__main__":
    logger.info(f"🚀 Starting Zava Insurance Voice Agent on port {PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
