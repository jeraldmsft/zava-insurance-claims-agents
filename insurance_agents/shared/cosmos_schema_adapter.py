"""Schema adapter for normalizing Cosmos DB claim documents."""

def normalize_claim(raw: dict) -> dict:
    return {
        "claimId": raw.get("claimId") or raw.get("id"),
        "status": raw.get("status", "submitted"),
        "category": raw.get("category", ""),
        "billAmount": raw.get("billAmount", 0),
        "billDate": raw.get("billDate", ""),
        "patientName": raw.get("patientName", ""),
        "memberId": raw.get("memberId", ""),
        "diagnosis": raw.get("diagnosis", ""),
        "serviceType": raw.get("serviceType", ""),
        "region": raw.get("region", ""),
        "assignedEmployeeName": raw.get("assignedEmployeeName", ""),
        "assignedEmployeeID": raw.get("assignedEmployeeID", ""),
    }
