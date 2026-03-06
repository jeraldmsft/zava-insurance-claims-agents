"""
Zava Insurance - Claims Processing Dashboard & Agent Registry
Employee-facing dashboard for managing insurance claims and monitoring agents.
"""
import os
import sys
import json
import logging
import asyncio
from pathlib import Path
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import aiohttp

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

logging.basicConfig(level=logging.INFO, format="📊 [DASHBOARD] %(asctime)s - %(levelname)s - %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger(__name__)

app = FastAPI(title="Zava Insurance Dashboard", description="Claims processing dashboard and agent registry")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

STATIC_DIR = Path(__file__).parent / "static"
DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", 3000))

AGENT_PORTS = {
    "claims_orchestrator": int(os.getenv("A2A_CLAIMS_ORCHESTRATOR_PORT", 8001)),
    "intake_clarifier": int(os.getenv("A2A_INTAKE_CLARIFIER_PORT", 8002)),
    "document_intelligence": int(os.getenv("A2A_DOCUMENT_INTELLIGENCE_PORT", 8003)),
    "coverage_rules_engine": int(os.getenv("A2A_COVERAGE_RULES_ENGINE_PORT", 8004)),
    "communication_agent": int(os.getenv("A2A_COMMUNICATION_AGENT_PORT", 8005)),
    "voice_agent": int(os.getenv("VOICE_LIVE_AGENT_PORT", 8007)),
}

# Chat history per session
chat_sessions = {}

@app.get("/")
async def serve_dashboard():
    html_path = STATIC_DIR / "claims_dashboard.html"
    if html_path.exists():
        return FileResponse(html_path, media_type="text/html")
    return HTMLResponse(generate_dashboard_html())

@app.get("/static/agent_registry.html")
async def serve_agent_registry():
    html_path = STATIC_DIR / "agent_registry.html"
    if html_path.exists():
        return FileResponse(html_path, media_type="text/html")
    return HTMLResponse(generate_registry_html())

@app.get("/static/{filename}")
async def serve_static(filename: str):
    file_path = STATIC_DIR / filename
    if file_path.exists():
        media_types = {".css": "text/css", ".js": "application/javascript", ".html": "text/html"}
        mt = media_types.get(file_path.suffix, "application/octet-stream")
        return FileResponse(file_path, media_type=mt)
    raise HTTPException(status_code=404, detail=f"{filename} not found")

@app.get("/api/agents")
async def get_agents():
    agents = []
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=3)) as session:
        for name, port in AGENT_PORTS.items():
            agent_info = {"name": name, "port": port, "url": f"http://localhost:{port}", "status": "offline"}
            try:
                async with session.get(f"http://localhost:{port}/.well-known/agent.json") as resp:
                    if resp.status == 200:
                        card = await resp.json()
                        agent_info.update({"status": "online", "card": card})
            except Exception:
                pass
            agents.append(agent_info)
    return JSONResponse(content={"agents": agents, "total": len(agents)})

@app.post("/api/chat")
async def chat(request: Request):
    body = await request.json()
    message = body.get("message", "")
    session_id = body.get("session_id", "default")

    if session_id not in chat_sessions:
        chat_sessions[session_id] = []
    chat_sessions[session_id].append({"role": "user", "content": message, "timestamp": datetime.utcnow().isoformat()})

    # Forward to claims orchestrator
    orchestrator_url = f"http://localhost:{AGENT_PORTS['claims_orchestrator']}"
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as session:
            payload = {
                "id": session_id,
                "sessionId": session_id,
                "message": {"role": "user", "parts": [{"type": "text", "text": message}]}
            }
            async with session.post(f"{orchestrator_url}/tasks/send", json=payload) as resp:
                result = await resp.json()
                agent_response = result.get("result", "Processing complete.")
    except Exception as e:
        agent_response = f"⚠️ Could not reach Claims Orchestrator: {str(e)}"

    chat_sessions[session_id].append({"role": "agent", "content": agent_response, "timestamp": datetime.utcnow().isoformat()})
    return JSONResponse(content={"response": agent_response, "session_id": session_id})

@app.get("/api/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    return JSONResponse(content={"history": chat_sessions.get(session_id, [])})

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "Zava Insurance Dashboard"}

def generate_dashboard_html():
    return """<!-- Inline fallback dashboard -->
<html><head><title>Zava Insurance Dashboard</title></head>
<body style="font-family:Segoe UI;background:#0d1b2a;color:#e0e8f0;padding:2rem;">
<h1 style="color:#00b38a;">Zava Insurance Claims Dashboard</h1>
<p>Dashboard HTML not found. Please ensure claims_dashboard.html exists in static/.</p>
</body></html>"""

def generate_registry_html():
    return """<html><head><title>Agent Registry</title></head>
<body style="font-family:Segoe UI;background:#0d1b2a;color:#e0e8f0;padding:2rem;">
<h1 style="color:#0096d6;">Agent Registry</h1>
<p>Registry HTML not found. Please ensure agent_registry.html exists in static/.</p>
</body></html>"""

if __name__ == "__main__":
    logger.info(f"🚀 Starting Zava Insurance Dashboard on port {DASHBOARD_PORT}")
    uvicorn.run(app, host="0.0.0.0", port=DASHBOARD_PORT)
