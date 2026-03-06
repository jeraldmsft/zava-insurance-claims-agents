"""Dynamic workflow logger for Zava Insurance claims processing pipeline."""
import logging
import json
import os
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

class WorkflowLogger:
    def __init__(self, log_dir: str = None):
        self.log_dir = log_dir or os.path.join(os.path.dirname(__file__), "..", "workflow_logs")
        Path(self.log_dir).mkdir(parents=True, exist_ok=True)
        self.current_workflow = None
        self.steps = []
    
    def start_workflow(self, claim_id: str, workflow_type: str = "claims_processing"):
        self.current_workflow = {
            "claimId": claim_id,
            "workflowType": workflow_type,
            "startedAt": datetime.now(timezone.utc).isoformat(),
            "steps": []
        }
        self.steps = []
        logger.info(f"📋 Workflow started for claim {claim_id}")
    
    def log_step(self, agent_name: str, action: str, status: str, details: dict = None):
        step = {
            "agent": agent_name,
            "action": action,
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": details or {}
        }
        self.steps.append(step)
        emoji = "✅" if status == "success" else "❌" if status == "failed" else "⏳"
        logger.info(f"{emoji} [{agent_name}] {action}: {status}")
    
    def end_workflow(self, final_status: str = "completed"):
        if self.current_workflow:
            self.current_workflow["steps"] = self.steps
            self.current_workflow["completedAt"] = datetime.now(timezone.utc).isoformat()
            self.current_workflow["finalStatus"] = final_status
            
            claim_id = self.current_workflow.get("claimId", "unknown")
            log_file = os.path.join(self.log_dir, f"workflow_{claim_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            with open(log_file, "w") as f:
                json.dump(self.current_workflow, f, indent=2)
            logger.info(f"📝 Workflow log saved: {log_file}")
            return self.current_workflow
        return None
