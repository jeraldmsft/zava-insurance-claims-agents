"""
Zava Insurance Coverage Rules Engine
Evaluates insurance coverage rules, policy limits, and benefit calculations.
"""
import os
import logging
import json
from a2a.types import AgentSkill
from shared.base_agent import BaseAgent

logger = logging.getLogger(__name__)

# Zava Insurance Coverage Rules
COVERAGE_RULES = {
    "inpatient_care": {
        "max_coverage": 50000,
        "deductible": 500,
        "copay_percent": 20,
        "requires_preauth": True,
        "covered_diagnoses": ["Acute cholecystitis", "Appendectomy", "Cardiac bypass surgery", "Pneumonia", "Fracture repair"],
    },
    "outpatient_care": {
        "max_coverage": 5000,
        "deductible": 100,
        "copay_percent": 30,
        "requires_preauth": False,
        "covered_diagnoses": ["Routine physical exam", "Follow-up consultation", "Blood work", "X-ray", "Vaccination"],
    },
}

class CoverageRulesAgent(BaseAgent):
    def __init__(self):
        skills = [
            AgentSkill(
                id="evaluate_coverage",
                name="Evaluate Coverage Rules",
                description="Evaluates insurance coverage rules, checks policy limits, and calculates benefits for claims",
                tags=["coverage", "rules", "policy", "benefits"]
            ),
        ]
        super().__init__(
            name="CoverageRulesEngine",
            description="Zava Insurance Coverage Rules Engine - evaluates policy rules and calculates benefits",
            port=int(os.getenv("A2A_COVERAGE_RULES_ENGINE_PORT", 8004)),
            skills=skills,
        )
    
    async def process_task(self, message: str, full_request: dict = None) -> str:
        logger.info(f"🛡️ Evaluating coverage: {message[:100]}...")
        
        try:
            parts = message.split(":", 1)
            claim_data = json.loads(parts[-1].strip()) if len(parts) > 1 else json.loads(message)
        except json.JSONDecodeError:
            return "⚠️ Could not parse claim data for coverage evaluation."
        
        claim_id = claim_data.get("claimId", "unknown")
        service_type = claim_data.get("serviceType", "outpatient_care")
        bill_amount = claim_data.get("billAmount", 0)
        diagnosis = claim_data.get("diagnosis", "")
        
        rules = COVERAGE_RULES.get(service_type, COVERAGE_RULES["outpatient_care"])
        
        results = []
        is_covered = True
        
        # Check if within coverage limit
        if bill_amount <= rules["max_coverage"]:
            results.append(f"✅ Bill ${bill_amount} is within coverage limit (${rules['max_coverage']})")
        else:
            results.append(f"❌ Bill ${bill_amount} exceeds coverage limit (${rules['max_coverage']})")
            is_covered = False
        
        # Check diagnosis coverage
        if diagnosis in rules["covered_diagnoses"]:
            results.append(f"✅ Diagnosis '{diagnosis}' is covered")
        else:
            results.append(f"⚠️ Diagnosis '{diagnosis}' - manual review recommended")
        
        # Calculate patient responsibility
        deductible = rules["deductible"]
        after_deductible = max(0, bill_amount - deductible)
        copay = after_deductible * (rules["copay_percent"] / 100)
        insurance_pays = after_deductible - copay
        
        results.append(f"💰 Deductible: ${deductible}")
        results.append(f"💰 Copay ({rules['copay_percent']}%): ${copay:.2f}")
        results.append(f"💰 Insurance pays: ${insurance_pays:.2f}")
        results.append(f"💰 Patient responsibility: ${deductible + copay:.2f}")
        
        if rules.get("requires_preauth"):
            results.append("📋 Pre-authorization: Required for this service type")
        
        recommendation = "✅ APPROVE" if is_covered else "❌ DENY"
        
        result = f"🛡️ Coverage Evaluation for {claim_id}:\n" + \
                 f"  Service Type: {service_type}\n" + \
                 f"  Recommendation: {recommendation}\n" + \
                 "\n".join(f"  {r}" for r in results)
        
        logger.info(f"{'✅' if is_covered else '❌'} Coverage evaluation: {recommendation}")
        return result
