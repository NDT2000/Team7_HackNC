import hashlib
from typing import Any, Dict, List, Tuple

def stable_hash(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]

def verdict_from_score(score: int) -> str:
    if score >= 70:
        return "block"
    if score >= 40:
        return "review"
    return "allow"

def simple_rules(entity: str, entity_type: str, context: Dict[str, Any] | None) -> Tuple[int, List[str]]:
    context = context or {}
    score = 10
    reasons: List[str] = []

    # demo-friendly rules
    if entity_type == "email" and ("@" not in entity or "." not in entity):
        score += 25
        reasons.append("Malformed email-like identifier")

    if entity_type == "wallet" and len(entity) < 20:
        score += 20
        reasons.append("Suspiciously short wallet address")

    if context.get("burst"):
        score += 30
        reasons.append("Velocity anomaly (burst activity)")

    if context.get("geo_mismatch"):
        score += 25
        reasons.append("Geo mismatch / impossible travel")

    if not reasons:
        reasons.append("No strong risk signals detected (MVP rules)")

    score = max(0, min(100, score))
    return score, reasons
