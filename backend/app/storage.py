import time
import json
from typing import Any, Dict, List, Optional

import orjson
from redis import Redis

class ValkeyStore:
    def __init__(self, url: str):
        self.r = Redis.from_url(url, decode_responses=True)

    # Generic JSON get/set with TTL
    def get_json(self, key: str) -> Optional[Dict[str, Any]]:
        raw = self.r.get(key)
        return json.loads(raw) if raw else None

    def set_json(self, key: str, value: Dict[str, Any], ttl_seconds: int = 900) -> None:
        self.r.setex(key, ttl_seconds, json.dumps(value))

    # Sliding window counter (rate limiting / velocity)
    def incr_with_ttl(self, key: str, ttl_seconds: int) -> int:
        pipe = self.r.pipeline()
        pipe.incr(key)
        pipe.expire(key, ttl_seconds)
        val, _ = pipe.execute()
        return int(val)

    # Alerts timeline (ZSET)
    def push_alert(self, alert: Dict[str, Any]) -> None:
        ts = int(time.time())
        alert = {**alert, "ts": ts}
        self.r.zadd("alerts:zset", {orjson.dumps(alert).decode("utf-8"): ts})
        self.r.zremrangebyrank("alerts:zset", 0, -501)

    def list_alerts(self, limit: int = 50) -> List[Dict[str, Any]]:
        items = self.r.zrevrange("alerts:zset", 0, limit - 1)
        out = []
        for raw in items:
            try:
                out.append(orjson.loads(raw))
            except Exception:
                pass
        return out
