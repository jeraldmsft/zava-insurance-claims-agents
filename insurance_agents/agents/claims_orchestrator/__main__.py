"""Launch the Claims Orchestrator agent."""
import sys
import os
import logging

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

logging.basicConfig(level=logging.INFO, format="🎯 [ORCHESTRATOR] %(asctime)s - %(levelname)s - %(message)s", datefmt="%H:%M:%S")

from claims_orchestrator.agent import ClaimsOrchestratorAgent

if __name__ == "__main__":
    agent = ClaimsOrchestratorAgent()
    agent.run()
