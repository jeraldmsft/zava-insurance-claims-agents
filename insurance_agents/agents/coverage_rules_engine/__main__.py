"""Launch the Coverage Rules Engine agent."""
import sys, os, logging
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
logging.basicConfig(level=logging.INFO, format="🛡️ [COVERAGE] %(asctime)s - %(levelname)s - %(message)s", datefmt="%H:%M:%S")
from coverage_rules_engine.agent import CoverageRulesAgent
if __name__ == "__main__":
    agent = CoverageRulesAgent()
    agent.run()
