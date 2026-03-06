"""
Zava Insurance Intake Clarifier Agent
Validates claim data consistency - checks submitted data against extracted data.
"""
import os
import logging
import json
from a2a.types import AgentSkill
from shared.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class IntakeClarifierAgent(BaseAgent):
    def __init__(self):
        skills = [
            AgentSkill(
                id="verify_claim_data",
                name="Verify Claim Data",
                description="Validates claim data consistency, checks for mismatches between submitted and extracted data",
                tags=["validation", "verification", "intake"]
            ),
        ]
        super().__init__(
            name="IntakeClarifier",
            description="Zava Insurance Intake Clarifier - validates and verifies claim data consistency",
            port=int(os.getenv("A2A_INTAKE_CLARIFIER_PORT", 8002)),
            skills=skills,
        )
    
    async def process_task(self, message: str, full_request: dict = None) -> str:
        logger.info(f"🔍 Verifying claim data: {message[:100]}...")
        
        try:
            claim_data = json.loads(message) if message.strip().startswith("{") else {}
        except json.JSONDecodeError:
            claim_data = {}
        
        verification_results = []
        
        # Check required fields
        required_fields = ["claimId", "patientName", "diagnosis", "billAmount", "category"]
        for field in required_fields:
            if field in claim_data and claim_data[field]:
                verification_results.append(f"✅ {field}: present")
            else:
                verification_results.append(f"❌ {field}: missing or empty")
        
        # Check bill amount validity
        bill_amount = claim_data.get("billAmount", 0)
        if isinstance(bill_amount, (int, float)) and bill_amount > 0:
            verification_results.append(f"✅ Bill amount ${bill_amount} is valid")
        else:
            verification_results.append(f"❌ Bill amount is invalid: {bill_amount}")
        
        # Check category
        valid_categories = ["Inpatient", "Outpatient"]
        category = claim_data.get("category", "")
        if category in valid_categories:
            verification_results.append(f"✅ Category '{category}' is valid")
        else:
            verification_results.append(f"⚠️ Category '{category}' - please verify")
        
        passed = sum(1 for r in verification_results if "✅" in r)
        total = len(verification_results)
        status = "Data verification passed" if passed == total else "Data verification has issues"
        
        claim_id = claim_data.get("claimId", "unknown")
        result = f"📋 Intake Verification for {claim_id}: {status}\n" + "\n".join(verification_results)
        logger.info(f"{'✅' if passed == total else '⚠️'} Verification: {passed}/{total} checks passed")
        return result
