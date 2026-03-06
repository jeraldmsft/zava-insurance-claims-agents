"""MCP Server configuration for Zava Insurance."""
import os
from dotenv import load_dotenv

load_dotenv()

MCP_SERVER_CONFIG = {
    "host": os.getenv("MCP_SERVER_HOST", "localhost"),
    "port": int(os.getenv("MCP_SERVER_PORT", 8080)),
    "cosmos_endpoint": os.getenv("COSMOS_ENDPOINT", ""),
    "cosmos_key": os.getenv("COSMOS_KEY", ""),
    "cosmos_database": os.getenv("COSMOS_DATABASE", "insurance"),
    "cosmos_container": os.getenv("COSMOS_CONTAINER", "claim_details"),
}

def get_mcp_server_url() -> str:
    return f"http://{MCP_SERVER_CONFIG['host']}:{MCP_SERVER_CONFIG['port']}"

def get_mcp_sse_url() -> str:
    return f"{get_mcp_server_url()}/sse"
