"""Cosmos DB client for Zava Insurance claims processing."""
import logging
import os
from datetime import datetime, timezone
from typing import Optional
from azure.cosmos import CosmosClient, PartitionKey, exceptions
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class CosmosDBClient:
    def __init__(self, endpoint: str = None, key: str = None, database_name: str = None, container_name: str = None):
        self.endpoint = endpoint or os.getenv("COSMOS_ENDPOINT")
        self.key = key or os.getenv("COSMOS_KEY")
        self.database_name = database_name or os.getenv("COSMOS_DATABASE", "insurance")
        self.container_name = container_name or os.getenv("COSMOS_CONTAINER", "claim_details")
        
        if not self.endpoint or not self.key:
            raise ValueError("COSMOS_ENDPOINT and COSMOS_KEY must be set")
        
        self.client = CosmosClient(self.endpoint, self.key)
        self.database = self.client.get_database_client(self.database_name)
        self.container = self.database.get_container_client(self.container_name)
        logger.info(f"✅ Connected to Cosmos DB: {self.database_name}/{self.container_name}")
    
    def get_claim(self, claim_id: str) -> Optional[dict]:
        try:
            items = list(self.container.query_items(
                query="SELECT * FROM c WHERE c.claimId = @claimId",
                parameters=[{"name": "@claimId", "value": claim_id}],
                enable_cross_partition_query=True
            ))
            return items[0] if items else None
        except Exception as e:
            logger.error(f"Error fetching claim {claim_id}: {e}")
            return None
    
    def get_all_claims(self) -> list:
        try:
            return list(self.container.query_items(
                query="SELECT * FROM c",
                enable_cross_partition_query=True
            ))
        except Exception as e:
            logger.error(f"Error fetching claims: {e}")
            return []
    
    def update_claim_status(self, claim_id: str, status: str, updated_by: str, reason: str = None) -> Optional[dict]:
        try:
            claim = self.get_claim(claim_id)
            if not claim:
                return None
            claim["status"] = status
            claim["updated_by"] = updated_by
            claim["lastUpdatedAt"] = datetime.now(timezone.utc).isoformat()
            if reason:
                claim["verification_reason"] = reason
                claim["verification_timestamp"] = datetime.now(timezone.utc).isoformat()
            self.container.upsert_item(claim)
            logger.info(f"✅ Updated claim {claim_id}: status={status}, by={updated_by}")
            return claim
        except Exception as e:
            logger.error(f"Error updating claim {claim_id}: {e}")
            return None
    
    def create_claim(self, claim_data: dict) -> Optional[dict]:
        try:
            if "id" not in claim_data:
                claim_data["id"] = claim_data.get("claimId", str(datetime.now(timezone.utc).timestamp()))
            claim_data["submittedAt"] = claim_data.get("submittedAt", datetime.now(timezone.utc).isoformat())
            claim_data["lastUpdatedAt"] = datetime.now(timezone.utc).isoformat()
            self.container.create_item(claim_data)
            logger.info(f"✅ Created claim: {claim_data.get('claimId')}")
            return claim_data
        except Exception as e:
            logger.error(f"Error creating claim: {e}")
            return None
    
    def save_extracted_data(self, claim_id: str, extracted_data: dict) -> Optional[dict]:
        try:
            ext_container = self.database.get_container_client("extracted_patient_data")
            doc = {
                "id": f"ext-{claim_id}",
                "claimId": claim_id,
                "extractedData": extracted_data,
                "extractedAt": datetime.now(timezone.utc).isoformat()
            }
            ext_container.upsert_item(doc)
            logger.info(f"✅ Saved extracted data for claim {claim_id}")
            return doc
        except Exception as e:
            logger.error(f"Error saving extracted data for {claim_id}: {e}")
            return None
    
    def get_claims_by_status(self, status: str) -> list:
        try:
            return list(self.container.query_items(
                query="SELECT * FROM c WHERE c.status = @status",
                parameters=[{"name": "@status", "value": status}],
                enable_cross_partition_query=True
            ))
        except Exception as e:
            logger.error(f"Error fetching claims by status {status}: {e}")
            return []
