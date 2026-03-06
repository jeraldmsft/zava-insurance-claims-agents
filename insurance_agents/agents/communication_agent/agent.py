"""
Zava Insurance Communication Agent
Sends email notifications for claim decisions using Azure Communication Services.
"""
import os
import logging
import json
from a2a.types import AgentSkill
from shared.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class CommunicationAgent(BaseAgent):
    def __init__(self):
        self.connection_string = os.getenv("AZURE_COMMUNICATION_CONNECTION_STRING", "")
        self.sender_email = os.getenv("AZURE_COMMUNICATION_SENDER_EMAIL", "DoNotReply@zavainsurance.com")
        
        skills = [
            AgentSkill(
                id="send_claim_notification",
                name="Send Claim Notification",
                description="Sends email notification about insurance claim decisions using Azure Communication Services",
                tags=["email", "notification", "communication", "claims"]
            ),
            AgentSkill(
                id="health_check",
                name="Email Service Health Check",
                description="Check if email service is available and configured properly",
                tags=["health", "status", "email"]
            ),
        ]
        super().__init__(
            name="CommunicationAgent",
            description="Zava Insurance Communication Agent - sends notifications for claim decisions via email",
            port=int(os.getenv("A2A_COMMUNICATION_AGENT_PORT", 8005)),
            skills=skills,
        )
    
    async def process_task(self, message: str, full_request: dict = None) -> str:
        logger.info(f"📧 Processing notification: {message[:100]}...")
        
        if not self.connection_string:
            logger.warning("⚠️ Azure Communication Services not configured - simulating email send")
            return f"📧 [SIMULATED] Notification would be sent for: {message[:200]}"
        
        try:
            from azure.communication.email import EmailClient
            email_client = EmailClient.from_connection_string(self.connection_string)
            
            email_message = {
                "senderAddress": self.sender_email,
                "recipients": {
                    "to": [{"address": "claims-team@zavainsurance.com"}]
                },
                "content": {
                    "subject": "Zava Insurance - Claim Processing Update",
                    "plainText": message,
                }
            }
            
            poller = email_client.begin_send(email_message)
            result = poller.result()
            logger.info(f"✅ Email sent successfully: {result.message_id}")
            return f"✅ Email notification sent successfully for claim processing update."
        except Exception as e:
            logger.error(f"❌ Email send failed: {e}")
            return f"⚠️ Email notification failed: {str(e)}. Claim update logged internally."
