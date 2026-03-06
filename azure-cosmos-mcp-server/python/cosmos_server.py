"""
Zava Insurance - Azure Cosmos DB MCP Server
Provides MCP-compliant tools for insurance claims data operations.
"""
import os
import json
import logging
from datetime import datetime, timezone
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from azure.cosmos import CosmosClient, exceptions

load_dotenv()
logging.basicConfig(level=logging.INFO, format="🗄️ [COSMOS-MCP] %(asctime)s - %(levelname)s - %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger(__name__)

COSMOS_URI = os.getenv("COSMOS_URI", os.getenv("COSMOS_ENDPOINT", ""))
COSMOS_KEY = os.getenv("COSMOS_KEY", "")
COSMOS_DATABASE = os.getenv("COSMOS_DATABASE", "insurance")
COSMOS_CONTAINER = os.getenv("COSMOS_CONTAINER", "claim_details")
MCP_HOST = os.getenv("MCP_SERVER_HOST", "localhost")
MCP_PORT = int(os.getenv("MCP_SERVER_PORT", 8080))

mcp = FastMCP("ZavaInsurance-CosmosMCP")

# Initialize Cosmos client
cosmos_client = None
database = None
container = None

def init_cosmos():
    global cosmos_client, database, container
    try:
        cosmos_client = CosmosClient(COSMOS_URI, COSMOS_KEY)
        database = cosmos_client.get_database_client(COSMOS_DATABASE)
        container = database.get_container_client(COSMOS_CONTAINER)
        logger.info(f"✅ Connected to Cosmos DB: {COSMOS_DATABASE}/{COSMOS_CONTAINER}")
    except Exception as e:
        logger.error(f"❌ Cosmos DB connection failed: {e}")

@mcp.tool()
def get_claim(claim_id: str) -> str:
    """Get insurance claim details by claim ID (e.g., IP-01, OP-03)."""
    try:
        items = list(container.query_items(
            query="SELECT * FROM c WHERE c.claimId = @claimId",
            parameters=[{"name": "@claimId", "value": claim_id}],
            enable_cross_partition_query=True
        ))
        if items:
            # Remove Cosmos metadata
            claim = items[0]
            for key in ["_rid", "_self", "_etag", "_attachments", "_ts"]:
                claim.pop(key, None)
            return json.dumps(claim, indent=2, default=str)
        return json.dumps({"error": f"Claim {claim_id} not found"})
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def get_all_claims() -> str:
    """Get all insurance claims from the database."""
    try:
        items = list(container.query_items(
            query="SELECT c.id, c.claimId, c.status, c.category, c.billAmount, c.patientName, c.diagnosis, c.region, c.assignedEmployeeName FROM c",
            enable_cross_partition_query=True
        ))
        return json.dumps({"claims": items, "total": len(items)}, indent=2, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def get_claims_by_status(status: str) -> str:
    """Get claims filtered by status (submitted, marked for approval, marked for rejection)."""
    try:
        items = list(container.query_items(
            query="SELECT * FROM c WHERE c.status = @status",
            parameters=[{"name": "@status", "value": status}],
            enable_cross_partition_query=True
        ))
        for item in items:
            for key in ["_rid", "_self", "_etag", "_attachments", "_ts"]:
                item.pop(key, None)
        return json.dumps({"claims": items, "total": len(items)}, indent=2, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def update_claim(claim_id: str, status: str = None, updated_by: str = None, verification_reason: str = None) -> str:
    """Update an insurance claim's status and verification details."""
    try:
        items = list(container.query_items(
            query="SELECT * FROM c WHERE c.claimId = @claimId",
            parameters=[{"name": "@claimId", "value": claim_id}],
            enable_cross_partition_query=True
        ))
        if not items:
            return json.dumps({"error": f"Claim {claim_id} not found"})
        
        claim = items[0]
        if status:
            claim["status"] = status
        if updated_by:
            claim["updated_by"] = updated_by
        if verification_reason:
            claim["verification_reason"] = verification_reason
            claim["verification_timestamp"] = datetime.now(timezone.utc).isoformat()
        claim["lastUpdatedAt"] = datetime.now(timezone.utc).isoformat()
        
        container.upsert_item(claim)
        for key in ["_rid", "_self", "_etag", "_attachments", "_ts"]:
            claim.pop(key, None)
        return json.dumps({"message": f"Claim {claim_id} updated", "claim": claim}, indent=2, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def create_claim(claim_id: str, patient_name: str, category: str, diagnosis: str, bill_amount: float, service_type: str, region: str = "US") -> str:
    """Create a new insurance claim."""
    try:
        claim = {
            "id": claim_id,
            "claimId": claim_id,
            "status": "submitted",
            "category": category,
            "billAmount": bill_amount,
            "billDate": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "submittedAt": datetime.now(timezone.utc).isoformat(),
            "lastUpdatedAt": datetime.now(timezone.utc).isoformat(),
            "patientName": patient_name,
            "diagnosis": diagnosis,
            "serviceType": service_type,
            "region": region,
        }
        container.create_item(claim)
        return json.dumps({"message": f"Claim {claim_id} created", "claim": claim}, indent=2, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
def save_extracted_data(claim_id: str, extracted_data: str) -> str:
    """Save document intelligence extracted data for a claim."""
    try:
        ext_container = database.get_container_client("extracted_patient_data")
        doc = {
            "id": f"ext-{claim_id}",
            "claimId": claim_id,
            "extractedData": json.loads(extracted_data) if isinstance(extracted_data, str) else extracted_data,
            "extractedAt": datetime.now(timezone.utc).isoformat()
        }
        ext_container.upsert_item(doc)
        return json.dumps({"message": f"Extracted data saved for {claim_id}"}, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)})

if __name__ == "__main__":
    init_cosmos()
    logger.info(f"🚀 Starting Zava Insurance Cosmos MCP Server on {MCP_HOST}:{MCP_PORT}")
    mcp.run(transport="sse")
