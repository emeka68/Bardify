import React, { useState, useEffect } from 'react';
import './App.css';

const STYLES = [
  { value: 'standard', label: '📜 Standard' },
  { value: 'dramatic', label: '🎭 Dramatic' },
  { value: 'poetic',   label: '🌹 Poetic'   },
];

const ShakespeareTranslator = () => {
  const [input, setInput] = useState('');
  const [results, setResults] = useState(null);   // { standard, dramatic, poetic }
  const [activeTab, setActiveTab] = useState('standard');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [copySuccess, setCopySuccess] = useState(false);
  const [offline, setOffline] = useState(!navigator.onLine);
  const [history, setHistory] = useState([]);
  const [concise, setConcise] = useState(false);

  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  useEffect(() => {
    const handleOnline = () => setOffline(false);
    const handleOffline = () => setOffline(true);
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  useEffect(() => {
    const saved = localStorage.getItem('shakespeare-history');
    if (saved) {
      try { setHistory(JSON.parse(saved)); } catch {}
    }
  }, []);

  const saveToHistory = (original, styleResults) => {
    const entry = { id: Date.now(), original, results: styleResults, timestamp: new Date().toISOString() };
    const updated = [entry, ...history].slice(0, 10);
    setHistory(updated);
    localStorage.setItem('shakespeare-history', JSON.stringify(updated));
  };

  const fetchStyle = async (style, text, length) => {
    const res = await fetch(`${API_BASE_URL}/transform`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, style, length }),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Transformation failed');
    }
    return res.json();
  };

  const handleTransform = async () => {
    if (!input.trim()) { setError('Please enter some text'); return; }
    if (offline) { setError('You are offline. Please check your connection.'); return; }

    setLoading(true);
    setError('');
    setResults(null);
    setActiveTab('standard');

    const length = concise ? 'concise' : 'full';

    try {
      const [standard, dramatic, poetic] = await Promise.all(
        STYLES.map((s) => fetchStyle(s.value, input.trim(), length))
      );

      const styleResults = { standard, dramatic, poetic };
      setResults(styleResults);
      saveToHistory(input.trim(), styleResults);
    } catch (err) {
      if (err instanceof TypeError && err.message.includes('Failed to fetch')) {
        setError('Cannot reach the server. Check your connection.');
      } else {
        setError(err.message || 'An error occurred. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = async () => {
    const text = results?.[activeTab]?.transformed || '';
    try {
      await navigator.clipboard.writeText(text);
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 2000);
    } catch {
      setError('Could not copy to clipboard');
    }
  };

  const handleClear = () => {
    setInput('');
    setResults(null);
    setError('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) handleTransform();
  };

  const handleLoadHistory = (item) => {
    setInput(item.original);
    setResults(item.results);
    setActiveTab('standard');
  };

  const handleClearHistory = () => {
    setHistory([]);
    localStorage.removeItem('shakespeare-history');
  };

  const totalTokens = results
    ? Object.values(results).reduce((sum, r) => sum + (r?.usage?.total_tokens || 0), 0)
    : 0;

  const exampleTexts = [
    { text: "Hey, what's up?", label: 'Greeting' },
    { text: 'That startup is totally fire', label: 'Slang' },
    { text: "I'm just chilling with my friends", label: 'Casual' },
    { text: 'No cap, that was wild', label: 'Internet slang' },
  ];

  return (
    <div className="container">
      <div className="header">
        <h1 className="title">🎭 Shakespeare Translator</h1>
        <p className="subtitle">Transform modern English into Shakespearean English</p>
        {offline && <div className="offline-banner">⚠️ Offline Mode</div>}
      </div>

      <div className="content">
        {/* Input */}
        <div className="section">
          <label className="label">Your Text</label>
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Enter modern English text... (Ctrl+Enter to transform)"
            className="textarea"
            disabled={loading}
            maxLength={2000}
          />
          <div className="char-count">{input.length} / 2000 characters</div>
        </div>

        {/* Options */}
        <div className="options-row">
          <span className="options-label">Response length</span>
          <button
            onClick={() => setConcise(!concise)}
            className={`concise-toggle ${concise ? 'active' : ''}`}
            disabled={loading}
          >
            {concise ? '⚡ Concise' : '📄 Full'}
          </button>
        </div>

        {/* Buttons */}
        <div className="button-group">
          <button
            onClick={handleTransform}
            disabled={loading || !input.trim() || offline}
            className="button primary-button"
            style={{ opacity: loading || !input.trim() || offline ? 0.6 : 1 }}
          >
            {loading ? '⏳ Transforming...' : '✨ Transform to Shakespeare'}
          </button>
          <button onClick={handleClear} disabled={loading} className="button secondary-button">
            Clear
          </button>
        </div>

        {/* Error */}
        {error && (
          <div className="error">
            <strong>❌ Error:</strong> {error}
          </div>
        )}

        {/* Tabbed Results */}
        {results && (
          <div className="section results-section">
            <div className="tabs-header">
              {STYLES.map((s) => (
                <button
                  key={s.value}
                  onClick={() => setActiveTab(s.value)}
                  className={`tab-btn ${activeTab === s.value ? 'active' : ''}`}
                >
                  {s.label}
                </button>
              ))}
            </div>

            <div className="tab-panel">
              <div className="output-box">
                {results[activeTab]?.transformed || ''}
              </div>
              <div className="output-actions">
                <button onClick={handleCopy} className="button copy-button">
                  {copySuccess ? '✅ Copied!' : '📋 Copy'}
                </button>
              </div>
              {totalTokens > 0 && (
                <div className="token-info">
                  <small>🔢 Total tokens used across all styles: {totalTokens}</small>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Examples */}
        <div className="examples">
          <h3 className="examples-title">Try These Examples</h3>
          <div className="examples-list">
            {exampleTexts.map((example, idx) => (
              <button
                key={idx}
                onClick={() => setInput(example.text)}
                className="example-button"
                title={example.label}
              >
                "{example.text.substring(0, 20)}..."
              </button>
            ))}
          </div>
        </div>

        {/* History */}
        {history.length > 0 && (
          <div className="history">
            <div className="history-header">
              <h3 className="history-title">📜 Recent Transformations</h3>
              <button onClick={handleClearHistory} className="clear-history-btn">Clear</button>
            </div>
            <div className="history-list">
              {history.map((item) => (
                <div key={item.id} className="history-item" onClick={() => handleLoadHistory(item)}>
                  <div className="history-original">{item.original.substring(0, 40)}...</div>
                  <small className="history-date">
                    {new Date(item.timestamp).toLocaleTimeString()}
                  </small>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="footer">
        <p>Built with React + Claude API + FastAPI</p>
        <p>
          <a href="https://github.com/emeka68/Bardify" className="link">GitHub</a>
          {' | '}
          <a href="http://localhost:8000/docs" className="link">API Docs</a>
          {' | '}
          <a href="https://twitter.com/SirTivaa" className="link">Twitter</a>
        </p>
      </div>
    </div>
  );
};

export default ShakespeareTranslator;
