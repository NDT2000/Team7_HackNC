import time
from typing import Any, Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .models import AnalyzeRequest, AnalyzeResponse
from .storage import ValkeyStore
from .risk_engine import stable_hash, simple_rules, verdict_from_score
from .integrations.backboard import backboard_analyze
from .integrations.gemini import gemini_crosscheck

app = FastAPI(title="Operation Firewall API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

store = ValkeyStore(settings.valkey_url)

@app.get("/health")
def health() -> Dict[str, Any]:
    return {"status": "ok", "ts": int(time.time())}

@app.get("/alerts")
def alerts(limit: int = 50):
    return {"alerts": store.list_alerts(limit=limit)}

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest) -> AnalyzeResponse:
    entity_hash = stable_hash(req.entity)
    cache_key = f"risk:cache:{entity_hash}"

    cached = store.get_json(cache_key)
    if cached:
        cached["cached"] = True
        return AnalyzeResponse(**cached)

    # demo rate/velocity signal (repeat analysis quickly to trigger burst)
    burst_count = store.incr_with_ttl(f"rate:{entity_hash}:10s", ttl_seconds=10)
    context = req.context or {}
    if burst_count >= 5:
        context = {**context, "burst": True}

    score, reasons = simple_rules(req.entity, req.entity_type, context)
    verdict = verdict_from_score(score)

    signals = {"score": score, "reasons": reasons, "context": context}
    bb = await backboard_analyze(req.entity, signals)
    gx = await gemini_crosscheck(req.entity, bb)

    case_id = f"case_{entity_hash}"

    result = AnalyzeResponse(
        entity=req.entity,
        entity_type=req.entity_type,
        risk_score=score,
        verdict=verdict,
        reasons=reasons,
        case_id=case_id,
        cached=False,
        ai_summary=bb.get("summary"),
        agreement=gx.get("agreement"),
    ).model_dump()

    store.set_json(cache_key, result, ttl_seconds=900)
    store.push_alert({
        "case_id": case_id,
        "entity": req.entity,
        "entity_type": req.entity_type,
        "risk_score": score,
        "verdict": verdict,
        "top_reason": reasons[0] if reasons else None,
    })

    return AnalyzeResponse(**result)
