"""
Zava Insurance Document Intelligence Agent
Processes and extracts data from medical documents (bills, discharge summaries, memos).
"""
import os
import logging
import json
from a2a.types import AgentSkill
from shared.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class DocumentIntelligenceAgent(BaseAgent):
    def __init__(self):
        skills = [
            AgentSkill(
                id="extract_document_data",
                name="Extract Document Data",
                description="Extracts structured data from medical documents using Azure Document Intelligence",
                tags=["document", "extraction", "ocr", "pdf"]
            ),
        ]
        super().__init__(
            name="DocumentIntelligenceAgent",
            description="Zava Insurance Document Intelligence - extracts and analyzes medical documents for claims processing",
            port=int(os.getenv("A2A_DOCUMENT_INTELLIGENCE_PORT", 8003)),
            skills=skills,
        )
    
    async def process_task(self, message: str, full_request: dict = None) -> str:
        logger.info(f"📄 Processing document: {message[:100]}...")
        
        try:
            claim_data = json.loads(message.split(":", 1)[-1].strip()) if ":" in message else {}
        except (json.JSONDecodeError, IndexError):
            claim_data = {}
        
        claim_id = claim_data.get("claimId", "unknown")
        
        # Simulate document extraction (in production, this would call Azure Document Intelligence)
        extracted = {
            "claimId": claim_id,
            "patientName": claim_data.get("patientName", ""),
            "diagnosis": claim_data.get("diagnosis", ""),
            "billAmount": claim_data.get("billAmount", 0),
            "category": claim_data.get("category", ""),
            "documentsProcessed": [],
        }
        
        # Check for document attachments
        attachments = []
        for key in ["billAttachment", "memoAttachment", "dischargeAttachment"]:
            if key in claim_data and claim_data[key]:
                attachments.append(key.replace("Attachment", ""))
                extracted["documentsProcessed"].append(key)
        
        if attachments:
            result = f"📄 Document Intelligence Results for {claim_id}:\n" + \
                     f"  Documents found: {', '.join(attachments)}\n" + \
                     f"  Patient: {extracted['patientName']}\n" + \
                     f"  Diagnosis: {extracted['diagnosis']}\n" + \
                     f"  Extracted Bill Amount: ${extracted['billAmount']}\n" + \
                     f"  Status: ✅ Extraction complete"
        else:
            result = f"📄 Document Intelligence for {claim_id}:\n" + \
                     f"  ⚠️ No document attachments found. Using submitted data.\n" + \
                     f"  Patient: {extracted['patientName']}\n" + \
                     f"  Diagnosis: {extracted['diagnosis']}"
        
        logger.info(f"✅ Document extraction completed for {claim_id}")
        return result
