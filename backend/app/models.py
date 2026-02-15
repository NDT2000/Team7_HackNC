from pydantic import BaseModel, Field
from typing import Any, Dict, List, Literal, Optional

EntityType = Literal["wallet", "email", "transaction", "unknown"]
Verdict = Literal["allow", "review", "block"]

class AnalyzeRequest(BaseModel):
    entity: str = Field(..., description="Wallet / email / tx id / identifier")
    entity_type: EntityType = "unknown"
    context: Optional[Dict[str, Any]] = Field(default=None, description="Optional metadata")

class AnalyzeResponse(BaseModel):
    entity: str
    entity_type: EntityType
    risk_score: int
    verdict: Verdict
    reasons: List[str]
    case_id: str
    cached: bool = False
    ai_summary: Optional[str] = None
    agreement: Optional[float] = None
