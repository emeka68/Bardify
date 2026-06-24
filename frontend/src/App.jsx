import React, { useState, useEffect } from 'react';
import './App.css';

const ShakespeareTranslator = () => {
  const [input, setInput] = useState('');
  const [output, setOutput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [tokenUsage, setTokenUsage] = useState(null);
  const [copySuccess, setCopySuccess] = useState(false);
  const [offline, setOffline] = useState(!navigator.onLine);
  const [history, setHistory] = useState([]);

  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  // Handle online/offline events
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

  // Load history from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('shakespeare-history');
    if (saved) {
      try {
        setHistory(JSON.parse(saved));
      } catch (e) {
        console.error('Failed to load history:', e);
      }
    }
  }, []);

  // Save to history
  const saveToHistory = (original, transformed) => {
    const newEntry = {
      id: Date.now(),
      original,
      transformed,
      timestamp: new Date().toISOString(),
    };

    const updated = [newEntry, ...history].slice(0, 10); // Keep last 10
    setHistory(updated);
    localStorage.setItem('shakespeare-history', JSON.stringify(updated));
  };

  const handleTransform = async () => {
    if (!input.trim()) {
      setError('Please enter some text');
      return;
    }

    if (offline) {
      setError('You are offline. Please check your connection.');
      return;
    }

    setLoading(true);
    setError('');
    setOutput('');
    setTokenUsage(null);

    try {
      const response = await fetch(`${API_BASE_URL}/transform`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: input }),
      });

      if (!response.ok) {
        if (response.status === 503) {
          const data = await response.json();
          if (data.offline) {
            setError('Backend is offline. Please try again later.');
          } else {
            setError('Service unavailable. Please try again later.');
          }
        } else {
          const errorData = await response.json();
          setError(errorData.detail || 'Transformation failed');
        }
        return;
      }

      const data = await response.json();

      if (data.error) {
        setError(data.error);
        return;
      }

      setOutput(data.transformed);
      saveToHistory(data.original, data.transformed);

      if (data.usage) {
        setTokenUsage(data.usage);
      }
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
    try {
      await navigator.clipboard.writeText(output);
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 2000);
    } catch {
      setError('Could not copy to clipboard');
    }
  };

  const handleClear = () => {
    setInput('');
    setOutput('');
    setError('');
    setTokenUsage(null);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      handleTransform();
    }
  };

  const handleLoadHistory = (item) => {
    setInput(item.original);
    setOutput(item.transformed);
  };

  const handleClearHistory = () => {
    setHistory([]);
    localStorage.removeItem('shakespeare-history');
  };

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
        {/* Input Section */}
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
          <div className="char-count">
            {input.length} / 2000 characters
          </div>
        </div>

        {/* Buttons */}
        <div className="button-group">
          <button
            onClick={handleTransform}
            disabled={loading || !input.trim() || offline}
            className="button primary-button"
            style={{
              opacity: loading || !input.trim() || offline ? 0.6 : 1,
            }}
          >
            {loading ? '⏳ Transforming...' : '✨ Transform to Shakespeare'}
          </button>
          <button
            onClick={handleClear}
            disabled={loading}
            className="button secondary-button"
          >
            Clear
          </button>
        </div>

        {/* Error Message */}
        {error && (
          <div className="error">
            <strong>❌ Error:</strong> {error}
          </div>
        )}

        {/* Output Section */}
        {output && (
          <div className="section">
            <label className="label">Shakespearean Version</label>
            <div className="output-box">
              <p>{output}</p>
            </div>
            <div className="output-actions">
              <button
                onClick={handleCopy}
                className="button copy-button"
              >
                {copySuccess ? '✅ Copied!' : '📋 Copy'}
              </button>
            </div>

            {/* Token Usage */}
            {tokenUsage && (
              <div className="token-info">
                <small>
                  🔢 Tokens used: {tokenUsage.total_tokens}
                  (input: {tokenUsage.input_tokens}, output: {tokenUsage.output_tokens})
                </small>
              </div>
            )}
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
              <button
                onClick={handleClearHistory}
                className="clear-history-btn"
              >
                Clear
              </button>
            </div>
            <div className="history-list">
              {history.map((item) => (
                <div
                  key={item.id}
                  className="history-item"
                  onClick={() => handleLoadHistory(item)}
                >
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
          <a href="https://github.com/emeka68/shakespeare-translator" className="link">
            GitHub
          </a>
          {' | '}
          <a href="http://localhost:8000/docs" className="link">
            API Docs
          </a>
          {' | '}
          <a href="https://twitter.com/SirTivaa" className="link">
            Twitter
          </a>
        </p>
      </div>
    </div>
  );
};

export default ShakespeareTranslator;
