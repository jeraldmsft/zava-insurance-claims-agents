"""
Zava Insurance Claims Orchestrator Agent
Routes claims through the processing pipeline: intake → document intelligence → coverage rules → communication.
"""
import os
import logging
import json
from a2a.types import AgentSkill
from shared.base_agent import BaseAgent
from shared.a2a_client import A2AClient
from shared.cosmos_db_client import CosmosDBClient

logger = logging.getLogger(__name__)

AGENT_PORTS = {
    "intake_clarifier": int(os.getenv("A2A_INTAKE_CLARIFIER_PORT", 8002)),
    "document_intelligence": int(os.getenv("A2A_DOCUMENT_INTELLIGENCE_PORT", 8003)),
    "coverage_rules_engine": int(os.getenv("A2A_COVERAGE_RULES_ENGINE_PORT", 8004)),
    "communication_agent": int(os.getenv("A2A_COMMUNICATION_AGENT_PORT", 8005)),
}

class ClaimsOrchestratorAgent(BaseAgent):
    def __init__(self):
        skills = [
            AgentSkill(
                id="process_claim",
                name="Process Insurance Claim",
                description="Orchestrates end-to-end insurance claim processing through multiple specialized agents",
                tags=["claims", "orchestration", "insurance"]
            ),
            AgentSkill(
                id="get_claim_status",
                name="Get Claim Status",
                description="Retrieves current status and details of an insurance claim",
                tags=["claims", "status", "query"]
            ),
        ]
        super().__init__(
            name="ClaimsOrchestrator",
            description="Zava Insurance Claims Orchestrator - coordinates claim processing across specialized agents using A2A protocol",
            port=int(os.getenv("A2A_CLAIMS_ORCHESTRATOR_PORT", 8001)),
            skills=skills,
        )
        self.cosmos_client = CosmosDBClient()
        self.sub_agents = {name: A2AClient(f"http://localhost:{port}") for name, port in AGENT_PORTS.items()}
        logger.info("✅ Claims Orchestrator initialized with Cosmos DB and sub-agents")
    
    async def process_task(self, message: str, full_request: dict = None) -> str:
        logger.info(f"📋 Processing: {message}")
        
        # Extract claim ID from message
        claim_id = self._extract_claim_id(message)
        if not claim_id:
            return "Please provide a claim ID (e.g., 'Process claim IP-01' or 'Check status of OP-03')."
        
        # Fetch claim from Cosmos DB
        claim_info = self.cosmos_client.get_claim(claim_id)
        if not claim_info:
            return f"Claim {claim_id} not found in the database."
        
        # Status check
        if any(word in message.lower() for word in ["status", "check", "query", "find"]):
            return f"📋 **Claim {claim_id} Details:**\n" + \
                   f"- Patient: {claim_info.get('patientName', 'N/A')}\n" + \
                   f"- Status: {claim_info.get('status', 'N/A')}\n" + \
                   f"- Category: {claim_info.get('category', 'N/A')}\n" + \
                   f"- Diagnosis: {claim_info.get('diagnosis', 'N/A')}\n" + \
                   f"- Bill Amount: ${claim_info.get('billAmount', 0)}\n" + \
                   f"- Region: {claim_info.get('region', 'N/A')}"
        
        # Full processing pipeline
        results = {"claim_id": claim_id, "steps": []}
        
        # Step 1: Document Intelligence
        try:
            doc_result = await self.sub_agents["document_intelligence"].send_task(
                f"Extract and analyze documents for claim {claim_id}: {json.dumps(claim_info)}"
            )
            results["steps"].append({"agent": "document_intelligence", "status": "completed", "result": doc_result.get("result", "")})
            logger.info(f"✅ Document Intelligence completed for {claim_id}")
        except Exception as e:
            results["steps"].append({"agent": "document_intelligence", "status": "failed", "error": str(e)})
            logger.warning(f"⚠️ Document Intelligence failed: {e}")
        
        # Step 2: Intake Clarifier
        try:
            intake_result = await self.sub_agents["intake_clarifier"].send_task(
                f"Verify claim data for {claim_id}: {json.dumps(claim_info)}"
            )
            results["steps"].append({"agent": "intake_clarifier", "status": "completed", "result": intake_result.get("result", "")})
            logger.info(f"✅ Intake Clarifier completed for {claim_id}")
        except Exception as e:
            results["steps"].append({"agent": "intake_clarifier", "status": "failed", "error": str(e)})
            logger.warning(f"⚠️ Intake Clarifier failed: {e}")
        
        # Step 3: Coverage Rules Engine
        try:
            coverage_result = await self.sub_agents["coverage_rules_engine"].send_task(
                f"Evaluate coverage rules for claim {claim_id}: {json.dumps(claim_info)}"
            )
            results["steps"].append({"agent": "coverage_rules_engine", "status": "completed", "result": coverage_result.get("result", "")})
            logger.info(f"✅ Coverage Rules Engine completed for {claim_id}")
        except Exception as e:
            results["steps"].append({"agent": "coverage_rules_engine", "status": "failed", "error": str(e)})
            logger.warning(f"⚠️ Coverage Rules Engine failed: {e}")
        
        # Step 4: Communication Agent
        try:
            comm_result = await self.sub_agents["communication_agent"].send_task(
                f"Send notification for claim {claim_id} processing complete. Results: {json.dumps(results)}"
            )
            results["steps"].append({"agent": "communication_agent", "status": "completed", "result": comm_result.get("result", "")})
            logger.info(f"✅ Communication Agent completed for {claim_id}")
        except Exception as e:
            results["steps"].append({"agent": "communication_agent", "status": "failed", "error": str(e)})
            logger.warning(f"⚠️ Communication Agent failed: {e}")
        
        successful = sum(1 for s in results["steps"] if s["status"] == "completed")
        return f"✅ Claim {claim_id} processed through {successful}/{len(results['steps'])} agents.\n" + \
               "\n".join(f"  {'✅' if s['status']=='completed' else '❌'} {s['agent']}: {s['status']}" for s in results["steps"])
    
    def _extract_claim_id(self, message: str) -> str:
        import re
        match = re.search(r'(IP-\d+|OP-\d+)', message.upper())
        return match.group(1) if match else None
