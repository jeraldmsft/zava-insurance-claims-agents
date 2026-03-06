"""Application settings for Zava Insurance Voice Agent."""
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8007
API_TITLE = "Zava Insurance Voice Agent"
API_DESCRIPTION = "A2A-compliant voice agent with Azure Voice Live API integration"
API_VERSION = "1.0.0"
CORS_ORIGINS = ["*"]
CORS_CREDENTIALS = True
CORS_METHODS = ["*"]
CORS_HEADERS = ["*"]
AGENT_ID = "client_live_voice_agent"
AGENT_NAME = "ZavaVoiceAgent"
AGENT_URL = f"http://localhost:{SERVER_PORT}/"
AGENT_INPUT_MODES = ['audio', 'text']
AGENT_OUTPUT_MODES = ['audio', 'text']
STATIC_HTML_FILE = "claims_voice_client.html"
STATIC_JS_FILES = {
    "claims_voice_client.js": "claims_voice_client.js",
    "audio-processor.js": "audio-processor.js",
    "config.js": "config.js"
}
DATABASE_QUERY_LIMIT = 10
