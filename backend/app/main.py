import time
import asyncio
import json
import re
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .threat_analyzer import ThreatAnalyzer
from .models import MessageInput, TransactionInput, AnalyzeRequest, AnalyzeResponse, CryptoWalletInput
# from .config import settings
# from .models import AnalyzeRequest, AnalyzeResponse
# from .storage import ValkeyStore
# from .risk_engine import stable_hash, simple_rules, verdict_from_score
# from .integrations.backboard import backboard_analyze
# from .integrations.gemini import gemini_crosscheck

app = FastAPI(title="Operation Firewall API", version="0.1.0")
threat_analyzer = ThreatAnalyzer()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# store = ValkeyStore(settings.valkey_url)

@app.get("/health")
def health() -> Dict[str, Any]:
    return {"status": "ok", "ts": int(time.time())}

@app.get("/alerts")
def alerts(limit: int = 50):
    """Return recent threat alerts"""
    # TODO: Fetch from database/cache
    # For now, return empty list - will be populated by analyze endpoint
    return {
        "alerts": []
    }

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest) -> AnalyzeResponse:
    """Unified analyze endpoint for various entity types"""
    try:
        # Pass the body text for email analysis
        if req.entity_type == "email":
            # Analyze as message/email for phishing
            result = await threat_analyzer.analyze_message(req.entity, req.context.get("body", req.context.get("message", "")) if req.context else "")
        elif req.entity_type == "transaction":
            # Analyze as transaction for anomalies
            amount = req.context.get("amount", 0) if req.context else 0
            merchant = req.context.get("merchant", "") if req.context else ""
            result = await threat_analyzer.analyze_transaction(req.entity, amount, merchant)
        elif req.entity_type == "wallet":
            result = await threat_analyzer.analyze_crypto_wallet(req.entity)
        else:
            result = await threat_analyzer.analyze_message(req.entity, "")

        # The analyzer may return a plain string (AI text) or a dict
        # Handle blocklist results first
        if isinstance(result, dict) and result.get("status") == "BLOCKED":
            return AnalyzeResponse(
                entity=req.entity,
                entity_type=req.entity_type,
                risk_score=100,
                verdict="block",
                reasons=[result.get("reason", "Blocked entity")],
                case_id=f"case_{hash(req.entity) % 10000}",
                cached=False,
                ai_summary=result.get("reason", "Entity is on the blocklist."),
                agreement=None,
            )

        if isinstance(result, str) and result.strip():
            # Try to parse JSON from AI response to extract confidence score
            parsed = {}
            try:
                parsed = json.loads(result)
            except (json.JSONDecodeError, TypeError):
                # Try to find JSON embedded in the string
                json_match = re.search(r'\{.*\}', result, re.DOTALL)
                if json_match:
                    try:
                        parsed = json.loads(json_match.group())
                    except (json.JSONDecodeError, TypeError):
                        pass

            # Extract confidence score and convert to risk score (0-100)
            confidence = parsed.get("confidence score", parsed.get("confidence", None))
            summary_text = parsed.get("explanation", parsed.get("explaination", result))

            if confidence is not None:
                try:
                    confidence = float(confidence)
                    risk_score = int(confidence * 100)
                except (ValueError, TypeError):
                    risk_score = 0
            else:
                risk_score = 0

            result = {"summary": summary_text, "risk_score": risk_score}
        elif not isinstance(result, dict):
            result = {"summary": str(result)}
        elif isinstance(result, str):
            result = {"summary": "Analysis returned empty response.", "risk_score": 0}
        elif not isinstance(result, dict):
            result = {"summary": str(result)}

        risk_score = result.get("risk_score", 0)
        # Derive verdict from risk score
        if risk_score >= 70:
            verdict = "block"
        elif risk_score >= 40:
            verdict = "review"
        else:
            verdict = result.get("verdict", "allow")

        return AnalyzeResponse(
            entity=req.entity,
            entity_type=req.entity_type,
            risk_score=risk_score,
            verdict=verdict,
            reasons=result.get("reasons", []),
            case_id=f"case_{hash(req.entity) % 10000}",
            cached=False,
            ai_summary=result.get("summary"),
            agreement=None,
        )
    except Exception as e:
        print(f"Error in analyze: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/message")
async def analyze_message(data: MessageInput):
    """Analyze a message for phishing"""
    try:
        result = await threat_analyzer.analyze_message(data.sender, data.body)
        return {"analysis": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/transaction")
async def analyze_transaction(data: TransactionInput):
    """Analyze a transaction for anomalies"""
    try:
        result = await threat_analyzer.analyze_transaction(data.user_id, data.amount, data.merchant)
        return {"analysis": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/crypto")
async def analyze_crypto(data: CryptoWalletInput):
    """Analyze crypto wallet for suspicious activity"""
    try:
        result = await threat_analyzer.analyze_crypto_wallet(data.address)
        return {"analysis": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# @app.post("/analyze", response_model=AnalyzeResponse)
# async def analyze(req: AnalyzeRequest) -> AnalyzeResponse:
#     entity_hash = stable_hash(req.entity)
#     cache_key = f"risk:cache:{entity_hash}"

#     cached = store.get_json(cache_key)
#     if cached:
#         cached["cached"] = True
#         return AnalyzeResponse(**cached)

#     # demo rate/velocity signal (repeat analysis quickly to trigger burst)
#     burst_count = store.incr_with_ttl(f"rate:{entity_hash}:10s", ttl_seconds=10)
#     context = req.context or {}
#     if burst_count >= 5:
#         context = {**context, "burst": True}

#     score, reasons = simple_rules(req.entity, req.entity_type, context)
#     verdict = verdict_from_score(score)

#     signals = {"score": score, "reasons": reasons, "context": context}
#     bb = await backboard_analyze(req.entity, signals)
#     gx = await gemini_crosscheck(req.entity, bb)

#     case_id = f"case_{entity_hash}"

#     result = AnalyzeResponse(
#         entity=req.entity,
#         entity_type=req.entity_type,
#         risk_score=score,
#         verdict=verdict,
#         reasons=reasons,
#         case_id=case_id,
#         cached=False,
#         ai_summary=bb.get("summary"),
#         agreement=gx.get("agreement"),
#     ).model_dump()

#     store.set_json(cache_key, result, ttl_seconds=900)
#     store.push_alert({
#         "case_id": case_id,
#         "entity": req.entity,
#         "entity_type": req.entity_type,
#         "risk_score": score,
#         "verdict": verdict,
#         "top_reason": reasons[0] if reasons else None,
#     })

#     return AnalyzeResponse(**result)
