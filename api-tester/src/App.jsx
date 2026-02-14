import { useState, useCallback } from 'react'
import './App.css'

const METHODS = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']

function App() {
  const [url, setUrl] = useState('')
  const [method, setMethod] = useState('GET')
  const [headers, setHeaders] = useState('{\n  "Content-Type": "application/json"\n}')
  const [body, setBody] = useState('')
  const [response, setResponse] = useState(null)
  const [loading, setLoading] = useState(false)
  const [history, setHistory] = useState([])

  const sendRequest = useCallback(async () => {
    if (!url) return
    setLoading(true)
    setResponse(null)

    const startTime = performance.now()

    try {
      let parsedHeaders = {}
      try {
        parsedHeaders = JSON.parse(headers)
      } catch {
        // ignore bad header JSON
      }

      const options = {
        method,
        headers: parsedHeaders,
      }

      if (!['GET', 'HEAD'].includes(method) && body.trim()) {
        options.body = body
      }

      const res = await fetch(url, options)
      const elapsed = Math.round(performance.now() - startTime)

      let responseBody
      const contentType = res.headers.get('content-type') || ''
      if (contentType.includes('application/json')) {
        responseBody = await res.json()
      } else {
        responseBody = await res.text()
      }

      const result = {
        status: res.status,
        statusText: res.statusText,
        time: elapsed,
        headers: Object.fromEntries(res.headers.entries()),
        body: responseBody,
      }

      setResponse(result)
      setHistory(prev => [
        { method, url, status: res.status, time: elapsed, timestamp: new Date().toLocaleTimeString() },
        ...prev.slice(0, 19),
      ])
    } catch (err) {
      setResponse({ error: err.message })
    } finally {
      setLoading(false)
    }
  }, [url, method, headers, body])

  const statusColor = (status) => {
    if (status >= 200 && status < 300) return '#4caf50'
    if (status >= 300 && status < 400) return '#ff9800'
    if (status >= 400 && status < 500) return '#f44336'
    if (status >= 500) return '#9c27b0'
    return '#888'
  }

  return (
    <div className="app">
      <h1>⚡ API Endpoint Tester</h1>

      {/* Request Section */}
      <div className="request-bar">
        <select value={method} onChange={(e) => setMethod(e.target.value)}>
          {METHODS.map((m) => (
            <option key={m} value={m}>{m}</option>
          ))}
        </select>
        <input
          type="text"
          placeholder="Enter URL (e.g. https://jsonplaceholder.typicode.com/posts)"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && sendRequest()}
        />
        <button onClick={sendRequest} disabled={loading || !url}>
          {loading ? 'Sending…' : 'Send'}
        </button>
      </div>

      <div className="panels">
        {/* Left Panel: Headers & Body */}
        <div className="panel">
          <h3>Headers</h3>
          <textarea
            rows={5}
            value={headers}
            onChange={(e) => setHeaders(e.target.value)}
            spellCheck={false}
          />

          {!['GET', 'HEAD'].includes(method) && (
            <>
              <h3>Body</h3>
              <textarea
                rows={8}
                placeholder='{"key": "value"}'
                value={body}
                onChange={(e) => setBody(e.target.value)}
                spellCheck={false}
              />
            </>
          )}
        </div>

        {/* Right Panel: Response */}
        <div className="panel">
          <h3>Response</h3>
          {loading && <div className="loader">Loading…</div>}
          {response && !response.error && (
            <div className="response">
              <div className="response-meta">
                <span className="badge" style={{ backgroundColor: statusColor(response.status) }}>
                  {response.status} {response.statusText}
                </span>
                <span className="time">{response.time}ms</span>
              </div>
              <details>
                <summary>Response Headers</summary>
                <pre>{JSON.stringify(response.headers, null, 2)}</pre>
              </details>
              <pre className="response-body">
                {typeof response.body === 'object'
                  ? JSON.stringify(response.body, null, 2)
                  : response.body}
              </pre>
            </div>
          )}
          {response?.error && (
            <div className="error">❌ {response.error}</div>
          )}
        </div>
      </div>

      {/* History */}
      {history.length > 0 && (
        <div className="history">
          <h3>History</h3>
          <table>
            <thead>
              <tr>
                <th>Time</th>
                <th>Method</th>
                <th>URL</th>
                <th>Status</th>
                <th>Duration</th>
              </tr>
            </thead>
            <tbody>
              {history.map((h, i) => (
                <tr key={i} onClick={() => { setMethod(h.method); setUrl(h.url) }}>
                  <td>{h.timestamp}</td>
                  <td><span className={`method-badge ${h.method.toLowerCase()}`}>{h.method}</span></td>
                  <td className="url-cell">{h.url}</td>
                  <td><span style={{ color: statusColor(h.status) }}>{h.status}</span></td>
                  <td>{h.time}ms</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

export default App
