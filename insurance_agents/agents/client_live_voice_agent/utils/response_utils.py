"""Utility functions for response handling."""
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def create_error_response(status_code: int, message: str, detail: str = None) -> JSONResponse:
    content = {"error": message}
    if detail:
        content["detail"] = detail
    return JSONResponse(status_code=status_code, content=content)

def create_success_response(data: dict) -> JSONResponse:
    return JSONResponse(content=data)

def serve_static_file(file_path: Path, media_type: str, not_found_message: str = None) -> FileResponse:
    if file_path.exists():
        return FileResponse(file_path, media_type=media_type)
    raise FileNotFoundError(not_found_message or f"{file_path.name} not found")

def create_fallback_html(title: str, message: str, agent_card_url: str = None) -> HTMLResponse:
    link = f'<p>Agent Card: <a href="{agent_card_url}">{agent_card_url}</a></p>' if agent_card_url else ""
    return HTMLResponse(f"<html><head><title>{title}</title></head><body><h1>{title}</h1><p>{message}</p>{link}</body></html>")
