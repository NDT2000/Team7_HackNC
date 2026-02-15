import { useEffect, useMemo, useState } from "react";
import { analyzeEntity, fetchAlerts, type EntityType } from "./lib/api";

type Verdict = "allow" | "review" | "block";

type AnalyzeResult = {
  entity: string;
  entity_type: EntityType;
  risk_score: number;
  verdict: Verdict;
  reasons: string[];
  case_id: string;
  cached: boolean;
  ai_summary?: string | null;
  agreement?: number | null;
};

type AlertItem = {
  ts: number;
  case_id: string;
  entity: string;
  entity_type: EntityType;
  risk_score: number;
  verdict: Verdict;
  top_reason?: string | null;
};

const badgeStyle = (verdict: Verdict) => {
  if (verdict === "block") return { background: "#ff3b3b", color: "white" as const };
  if (verdict === "review") return { background: "#ffb020", color: "black" as const };
  return { background: "#1ed760", color: "black" as const };
};

export default function App() {
  const [entity, setEntity] = useState("");
  const [entityType, setEntityType] = useState<EntityType>("wallet");
  const [result, setResult] = useState<AnalyzeResult | null>(null);
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  const canAnalyze = useMemo(() => entity.trim().length > 0 && !loading, [entity, loading]);

  async function refreshAlerts() {
    try {
      const data = await fetchAlerts(20);
      setAlerts((data.alerts || []) as AlertItem[]);
    } catch {
      // ignore for MVP
    }
  }

  useEffect(() => {
    refreshAlerts();
    const id = window.setInterval(refreshAlerts, 2500);
    return () => window.clearInterval(id);
  }, []);

  async function onAnalyze() {
    setErr(null);
    setLoading(true);
    setResult(null);
    try {
      const data = (await analyzeEntity(entity.trim(), entityType)) as AnalyzeResult;
      setResult(data);
      refreshAlerts();
    } catch (e: any) {
      setErr(e?.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ minHeight: "100vh", background: "#0b0f14", color: "#e7eef7" }}>
      <div style={{ maxWidth: 1100, margin: "0 auto", padding: 24 }}>
        <header style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
          <div>
            <h1 style={{ margin: 0, fontSize: 28 }}>Operation Firewall</h1>
            <p style={{ marginTop: 6, color: "#9fb0c3" }}>
              Bank-facing fraud intelligence • Valkey timeline • AI validation (MVP)
            </p>
          </div>
          <div style={{ color: "#9fb0c3", fontSize: 12 }}>
            API: {import.meta.env.VITE_API_BASE || "http://localhost:8000"}
          </div>
        </header>

        {/* Analyze Panel */}
        <div
          style={{
            marginTop: 18,
            padding: 18,
            borderRadius: 16,
            border: "1px solid #1c2530",
            background: "#0f1620"
          }}
        >
          <h2 style={{ marginTop: 0, fontSize: 18 }}>Analyze Entity</h2>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 180px 140px", gap: 12 }}>
            <input
              value={entity}
              onChange={(e) => setEntity(e.target.value)}
              placeholder="Paste wallet / email / transaction id…"
              style={{
                padding: 12,
                borderRadius: 12,
                border: "1px solid #243242",
                background: "#0b0f14",
                color: "#e7eef7"
              }}
            />
            <select
              value={entityType}
              onChange={(e) => setEntityType(e.target.value as EntityType)}
              style={{
                padding: 12,
                borderRadius: 12,
                border: "1px solid #243242",
                background: "#0b0f14",
                color: "#e7eef7"
              }}
            >
              <option value="wallet">wallet</option>
              <option value="email">email</option>
              <option value="transaction">transaction</option>
              <option value="unknown">unknown</option>
            </select>

            <button
              onClick={onAnalyze}
              disabled={!canAnalyze}
              style={{
                padding: 12,
                borderRadius: 12,
                border: "1px solid #2a3a4d",
                background: canAnalyze ? "#e7eef7" : "#2a3a4d",
                color: canAnalyze ? "#0b0f14" : "#9fb0c3",
                fontWeight: 700,
                cursor: canAnalyze ? "pointer" : "not-allowed"
              }}
            >
              {loading ? "Analyzing…" : "Analyze"}
            </button>
          </div>

          {err && <div style={{ marginTop: 10, color: "#ff6b6b", fontSize: 13 }}>{err}</div>}

          {result && (
            <div style={{ marginTop: 16, display: "grid", gridTemplateColumns: "320px 1fr", gap: 14 }}>
              <div style={{ padding: 14, borderRadius: 14, border: "1px solid #1c2530", background: "#0b0f14" }}>
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <div>
                    <div style={{ color: "#9fb0c3", fontSize: 12 }}>Verdict</div>
                    <div
                      style={{
                        marginTop: 6,
                        display: "inline-flex",
                        padding: "6px 10px",
                        borderRadius: 999,
                        ...badgeStyle(result.verdict)
                      }}
                    >
                      {String(result.verdict).toUpperCase()}
                    </div>
                  </div>

                  <div style={{ textAlign: "right" }}>
                    <div style={{ color: "#9fb0c3", fontSize: 12 }}>Risk Score</div>
                    <div style={{ fontSize: 32, fontWeight: 800 }}>{result.risk_score}</div>
                  </div>
                </div>

                <div style={{ marginTop: 10, color: "#9fb0c3", fontSize: 12 }}>Cross-check agreement</div>
                <div style={{ fontSize: 18, fontWeight: 700 }}>
                  {typeof result.agreement === "number" ? `${Math.round(result.agreement * 100)}%` : "—"}
                </div>

                <div style={{ marginTop: 10, color: "#9fb0c3", fontSize: 12 }}>Case</div>
                <div style={{ fontSize: 12, color: "#cfe1f5" }}>
                  {result.case_id} • cached: {String(result.cached)}
                </div>
              </div>

              <div style={{ padding: 14, borderRadius: 14, border: "1px solid #1c2530", background: "#0b0f14" }}>
                <div style={{ color: "#9fb0c3", fontSize: 12 }}>Top reasons</div>
                <ul style={{ marginTop: 8, color: "#e7eef7" }}>
                  {(result.reasons || []).slice(0, 6).map((r, i) => (
                    <li key={i} style={{ marginBottom: 6 }}>
                      {r}
                    </li>
                  ))}
                </ul>

                <div style={{ marginTop: 12, color: "#9fb0c3", fontSize: 12 }}>AI Summary (placeholder)</div>
                <div style={{ marginTop: 6 }}>{result.ai_summary || "—"}</div>
              </div>
            </div>
          )}
        </div>

        {/* Threat Feed */}
        <div
          style={{
            marginTop: 18,
            padding: 18,
            borderRadius: 16,
            border: "1px solid #1c2530",
            background: "#0f1620"
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
            <div>
              <h2 style={{ margin: 0, fontSize: 18 }}>Threat Feed</h2>
              <p style={{ marginTop: 6, color: "#9fb0c3" }}>Live alerts from Valkey (polling every 2.5s)</p>
            </div>
            <button
              onClick={refreshAlerts}
              style={{
                padding: "8px 12px",
                borderRadius: 12,
                border: "1px solid #2a3a4d",
                background: "#0b0f14",
                color: "#cfe1f5",
                cursor: "pointer"
              }}
            >
              Refresh
            </button>
          </div>

          <div style={{ marginTop: 12, display: "grid", gap: 10 }}>
            {alerts.length === 0 && <div style={{ color: "#9fb0c3" }}>No alerts yet. Run an analysis above.</div>}

            {alerts.map((a, idx) => (
              <div
                key={idx}
                style={{ padding: 12, borderRadius: 14, border: "1px solid #1c2530", background: "#0b0f14" }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
                    <span style={{ padding: "4px 10px", borderRadius: 999, ...badgeStyle(a.verdict) }}>
                      {String(a.verdict).toUpperCase()}
                    </span>
                    <strong>score {a.risk_score}</strong>
                  </div>
                  <div style={{ color: "#9fb0c3", fontSize: 12 }}>{a.ts}</div>
                </div>

                <div style={{ marginTop: 6, color: "#9fb0c3", fontSize: 12 }}>
                  {a.entity_type} • {a.entity}
                </div>
                {a.top_reason && <div style={{ marginTop: 8 }}>{a.top_reason}</div>}
              </div>
            ))}
          </div>
        </div>

        <footer style={{ marginTop: 22, color: "#9fb0c3", fontSize: 12 }}>
          Next: add “Retrieved Evidence” (RAG) panel + case history.
        </footer>
      </div>
    </div>
  );
}
