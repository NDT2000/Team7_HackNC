import { useEffect, useMemo, useState } from "react";
import { analyzeEntity, fetchAlerts, type EntityType } from "./lib/api";
import "./App.css";

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

function badgeClass(verdict: Verdict) {
  return "badge badge-" + verdict;
}

function riskClass(score: number) {
  if (score >= 70) return "risk-score high";
  if (score >= 40) return "risk-score medium";
  return "risk-score low";
}

function formatTime(ts: number) {
  try {
    const d = new Date(ts * 1000);
    return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
  } catch {
    return String(ts);
  }
}

export default function App() {
  const [entityType, setEntityType] = useState<EntityType>("wallet");
  const [emailData, setEmailData] = useState({ message: "", senderId: "" });
  const [walletData, setWalletData] = useState({ cryptoId: "" });
  const [transactionData, setTransactionData] = useState({ userId: "", senderId: "", amount: "" });
  const [result, setResult] = useState<AnalyzeResult | null>(null);
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  const getCanAnalyze = () => {
    if (loading) return false;
    switch (entityType) {
      case "email":
        return emailData.message.trim().length > 0 && emailData.senderId.trim().length > 0;
      case "wallet":
        return walletData.cryptoId.trim().length > 0;
      case "transaction":
        return (
          transactionData.userId.trim().length > 0 &&
          transactionData.senderId.trim().length > 0 &&
          transactionData.amount.trim().length > 0
        );
      default:
        return false;
    }
  };

  const canAnalyze = useMemo(() => getCanAnalyze(), [emailData, walletData, transactionData, entityType, loading]);

  async function refreshAlerts() {
    try {
      const data = await fetchAlerts(20);
      console.log("Alerts data:", data);
      setAlerts((data.alerts || []) as AlertItem[]);
    } catch (e: any) {
      console.error("Alert fetch error:", e);
      // ignore for MVP
    }
  }

  useEffect(() => {
    console.log("App mounted, fetching initial alerts");
    refreshAlerts();
    const id = window.setInterval(refreshAlerts, 2500);
    return () => window.clearInterval(id);
  }, []);

  async function onAnalyze() {
    setErr(null);
    setLoading(true);
    setResult(null);
    try {
      let entityValue = "";
      let context: any = null;
      switch (entityType) {
        case "email":
          entityValue = emailData.senderId;
          context = { body: emailData.message };
          break;
        case "wallet":
          entityValue = walletData.cryptoId;
          break;
        case "transaction":
          entityValue = transactionData.userId;
          context = { amount: parseFloat(transactionData.amount) || 0, merchant: transactionData.senderId };
          break;
      }

      const data = (await analyzeEntity(entityValue, entityType, context)) as AnalyzeResult;
      setResult(data);
      
      // Add to alerts feed
      const alertItem: AlertItem = {
        ts: Math.floor(Date.now() / 1000),
        case_id: data.case_id,
        entity: data.entity,
        entity_type: data.entity_type,
        risk_score: data.risk_score,
        verdict: data.verdict,
        top_reason: data.reasons?.[0] || undefined
      };
      
      setAlerts((prev) => [alertItem, ...prev].slice(0, 20)); // Keep last 20 alerts
    } catch (e: any) {
      setErr(e?.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Enter" && canAnalyze) onAnalyze();
  }

  return (
    <div className="app-shell">
      <div className="app-container">
        {/* Header */}
        <header className="header">
          <div>
            <div className="header-brand">
              <div className="header-logo">&#x1f6e1;&#xfe0f;</div>
              <div>
                <div className="header-title">Operation Firewall</div>
                <div className="header-subtitle">
                  Bank-facing fraud intelligence &bull; Valkey timeline &bull; AI validation
                </div>
              </div>
            </div>
          </div>
          <div className="header-meta">
            <span className="status-dot" />
            {import.meta.env.VITE_API_BASE || "http://localhost:8000"}
          </div>
        </header>

        {/* Analyze Panel */}
        <section className="card" style={{ animationDelay: "0.05s" }}>
          <div className="card-header">
            <div>
              <div className="card-title">
                <span className="icon">&#x1f50d;</span> Analyze Entity
              </div>
              <div className="card-desc">Submit a wallet, email, or transaction ID for risk assessment</div>
            </div>
          </div>

          <div className="analyze-grid">
            {entityType === "email" && (
              <>
                <input
                  className="input-field"
                  value={emailData.message}
                  onChange={(e) => setEmailData({ ...emailData, message: e.target.value })}
                  onKeyDown={handleKeyDown}
                  placeholder="Enter message content..."
                />
                <input
                  className="input-field"
                  value={emailData.senderId}
                  onChange={(e) => setEmailData({ ...emailData, senderId: e.target.value })}
                  onKeyDown={handleKeyDown}
                  placeholder="Enter sender user ID..."
                />
              </>
            )}

            {entityType === "wallet" && (
              <input
                className="input-field"
                value={walletData.cryptoId}
                onChange={(e) => setWalletData({ cryptoId: e.target.value })}
                onKeyDown={handleKeyDown}
                placeholder="Enter crypto wallet ID..."
              />
            )}

            {entityType === "transaction" && (
              <>
                <input
                  className="input-field"
                  value={transactionData.userId}
                  onChange={(e) => setTransactionData({ ...transactionData, userId: e.target.value })}
                  onKeyDown={handleKeyDown}
                  placeholder="Enter user ID..."
                />
                <input
                  className="input-field"
                  value={transactionData.senderId}
                  onChange={(e) => setTransactionData({ ...transactionData, senderId: e.target.value })}
                  onKeyDown={handleKeyDown}
                  placeholder="Enter sender ID..."
                />
                <input
                  className="input-field"
                  value={transactionData.amount}
                  onChange={(e) => setTransactionData({ ...transactionData, amount: e.target.value })}
                  onKeyDown={handleKeyDown}
                  placeholder="Enter amount..."
                />
              </>
            )}

            <select
              className="select-field"
              value={entityType}
              onChange={(e) => setEntityType(e.target.value as EntityType)}
            >
              <option value="wallet">Wallet</option>
              <option value="email">Email</option>
              <option value="transaction">Transaction</option>
              <option value="unknown">Unknown</option>
            </select>

            <button className="btn-primary" onClick={onAnalyze} disabled={!canAnalyze}>
              {loading && <span className="spinner" />}
              {loading ? "Analyzing..." : "Analyze"}
            </button>
          </div>

          {err && <div className="error-msg">{err}</div>}

          {result && (
            <div className="result-grid">
              <div className="result-card">
                <div className="result-overview">
                  <div>
                    <div className="label">Verdict</div>
                    <span className={badgeClass(result.verdict)}>
                      {result.verdict.toUpperCase()}
                    </span>
                  </div>
                  <div style={{ textAlign: "right" }}>
                    <div className="label">Risk Score</div>
                    <div className={riskClass(result.risk_score)}>{result.risk_score}</div>
                  </div>
                </div>

                <div style={{ marginTop: 20 }}>
                  <div className="label">Cross-check Agreement</div>
                  <div className="agreement-value">
                    {typeof result.agreement === "number"
                      ? Math.round(result.agreement * 100) + "%"
                      : "\u2014"}
                  </div>
                </div>

                <div style={{ marginTop: 16 }}>
                  <div className="label">Case ID</div>
                  <div className="case-meta">
                    {result.case_id}
                    {result.cached && <span className="cached-badge">Cached</span>}
                  </div>
                </div>
              </div>

              <div className="result-card">
                <div className="label">Top Reasons</div>
                <ul className="reasons-list">
                  {(result.reasons || []).slice(0, 6).map((r, i) => (
                    <li key={i}>{r}</li>
                  ))}
                </ul>

                <div className="ai-summary">
                  <div className="ai-summary-label">
                    <span>&#x2728;</span> AI Summary
                  </div>
                  {result.ai_summary || "No AI summary available for this entity."}
                </div>
              </div>
            </div>
          )}
        </section>

        {/* Threat Feed */}
        <section className="card threat-feed">
          <div className="card-header">
            <div>
              <div className="card-title">
                <span className="icon">&#x1f4e1;</span> Threat Feed
              </div>
              <div className="card-desc">Live alerts from Valkey &mdash; auto-refreshing every 2.5s</div>
            </div>
            <button className="btn-ghost" onClick={refreshAlerts}>
              &#x21bb; Refresh
            </button>
          </div>

          <div className="alert-list">
            {alerts.length === 0 && (
              <div className="empty-state">
                <div className="empty-icon">&#x1f4ed;</div>
                No alerts yet. Run an analysis above to generate threat data.
              </div>
            )}

            {alerts.map((a, idx) => (
              <div className="alert-item" key={idx} style={{ animationDelay: idx * 0.05 + "s" }}>
                <div className="alert-top">
                  <div className="alert-left">
                    <span className={badgeClass(a.verdict)}>{a.verdict.toUpperCase()}</span>
                    <span className="alert-score">Score: {a.risk_score}</span>
                  </div>
                  <span className="alert-time">{formatTime(a.ts)}</span>
                </div>
                <div className="alert-entity">
                  <span className="entity-type-tag">{a.entity_type}</span>
                  {a.entity}
                </div>
                {a.top_reason && <div className="alert-reason">{a.top_reason}</div>}
              </div>
            ))}
          </div>
        </section>

        <footer className="footer">
          Operation Firewall &bull; HackNC Team 7 &bull; MVP
        </footer>
      </div>
    </div>
  );
}
