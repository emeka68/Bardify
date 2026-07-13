import React, { useState, useEffect, useRef } from 'react';
import './App.css';

const STYLES = [
  { value: 'standard', label: '📜 Standard' },
  { value: 'dramatic', label: '🎭 Dramatic' },
  { value: 'poetic',   label: '🌹 Poetic'   },
];

const VOICES = [
  { key: 'posh',       emoji: '🎩', name: 'Posh British'  },
  { key: 'roadman',    emoji: '🧢', name: 'Roadman'        },
  { key: 'villain',    emoji: '😈', name: 'Villain'        },
  { key: 'southern',   emoji: '🌸', name: 'Southern Belle' },
  { key: 'romantic',   emoji: '💕', name: 'Romantic'       },
  { key: 'theatre',    emoji: '🎬', name: 'Theatre Kid'    },
  { key: 'elder',      emoji: '🦉', name: 'Wise Elder'     },
  { key: 'mysterious', emoji: '🌙', name: 'Mysterious'     },
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
  const [favorites, setFavorites] = useState([]);
  const [currentEntryId, setCurrentEntryId] = useState(null);
  const [concise, setConcise] = useState(false);
  const [regenLoading, setRegenLoading] = useState(false);
  const [selectedVoice, setSelectedVoice] = useState(VOICES[0].key);
  const [audioLoading, setAudioLoading] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [ttsEnabled, setTtsEnabled] = useState(true);
  const audioRef = useRef(null);

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
    const savedFavorites = localStorage.getItem('shakespeare-favorites');
    if (savedFavorites) {
      try { setFavorites(JSON.parse(savedFavorites)); } catch {}
    }
  }, []);

  const saveToHistory = (id, original, styleResults) => {
    const entry = { id, original, results: styleResults, timestamp: new Date().toISOString() };
    const updated = [entry, ...history].slice(0, 10);
    setHistory(updated);
    localStorage.setItem('shakespeare-history', JSON.stringify(updated));
  };

  const saveFavorites = (updated) => {
    setFavorites(updated);
    localStorage.setItem('shakespeare-favorites', JSON.stringify(updated));
  };

  const isFavorited = (id) => favorites.some((f) => f.id === id);

  const handleToggleFavorite = (item) => {
    const exists = favorites.some((f) => f.id === item.id);
    const updated = exists ? favorites.filter((f) => f.id !== item.id) : [item, ...favorites];
    saveFavorites(updated);
  };

  const handleToggleCurrentFavorite = () => {
    if (!currentEntryId || !results) return;
    handleToggleFavorite({
      id: currentEntryId,
      original: input,
      results,
      timestamp: new Date().toISOString(),
    });
  };

  const handleClearFavorites = () => {
    saveFavorites([]);
  };

  const handleExportFavorites = () => {
    const blob = new Blob([JSON.stringify(favorites, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'bardify-favorites.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
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
      const entryId = Date.now();
      setResults(styleResults);
      setCurrentEntryId(entryId);
      saveToHistory(entryId, input.trim(), styleResults);
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

  const handleRegen = async () => {
    if (!input.trim() || regenLoading) return;
    setRegenLoading(true);
    try {
      const data = await fetchStyle(activeTab, input.trim(), concise ? 'concise' : 'full');
      setResults((prev) => ({ ...prev, [activeTab]: data }));
    } catch (err) {
      setError(err.message || 'Regeneration failed');
    } finally {
      setRegenLoading(false);
    }
  };

  const handleListen = async () => {
    if (audioLoading || !results?.[activeTab]?.transformed) return;

    // Toggle off if already playing
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
      setIsPlaying(false);
      return;
    }

    setAudioLoading(true);
    setError('');

    try {
      const res = await fetch(`${API_BASE_URL}/speak`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: results[activeTab].transformed, voice: selectedVoice }),
      });

      if (!res.ok) {
        const err = await res.json();
        if (res.status === 503) setTtsEnabled(false);
        throw new Error(err.detail || 'TTS failed');
      }

      const data = await res.json();
      const audio = new Audio(`data:audio/${data.format};base64,${data.audio}`);
      audioRef.current = audio;
      audio.onended = () => { setIsPlaying(false); audioRef.current = null; };
      audio.onerror = () => { setIsPlaying(false); setError('Audio playback failed'); audioRef.current = null; };
      setIsPlaying(true);
      audio.play();
    } catch (err) {
      setError(err.message || 'Could not play audio');
      setIsPlaying(false);
    } finally {
      setAudioLoading(false);
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
    setCurrentEntryId(null);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) handleTransform();
  };

  const handleLoadItem = (item) => {
    setInput(item.original);
    setResults(item.results);
    setActiveTab('standard');
    setCurrentEntryId(item.id);
  };

  const handleClearHistory = () => {
    setHistory([]);
    localStorage.removeItem('shakespeare-history');
  };

  const totalTokens = results
    ? Object.values(results).reduce((sum, r) => sum + (r?.usage?.total_tokens || 0), 0)
    : 0;

  const currentFavorited = currentEntryId ? isFavorited(currentEntryId) : false;

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
        {offline && <div className="offline-banner" role="status">⚠️ Offline Mode</div>}
      </div>

      <div className="content">
        {/* Input */}
        <div className="section">
          <label className="label" htmlFor="input-textarea">Your Text</label>
          <textarea
            id="input-textarea"
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
          <span className="options-label" id="response-length-label">Response length</span>
          <button
            onClick={() => setConcise(!concise)}
            className={`concise-toggle ${concise ? 'active' : ''}`}
            disabled={loading}
            aria-pressed={concise}
            aria-labelledby="response-length-label"
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
            aria-keyshortcuts="Control+Enter"
          >
            {loading ? '⏳ Transforming...' : '✨ Transform to Shakespeare'}
          </button>
          <button onClick={handleClear} disabled={loading} className="button secondary-button">
            Clear
          </button>
        </div>

        {/* Error */}
        {error && (
          <div className="error" role="alert" aria-live="polite">
            <strong>❌ Error:</strong> {error}
          </div>
        )}

        {/* Tabbed Results */}
        {results && (
          <div className="section results-section">
            <div className="tabs-header" role="tablist" aria-label="Translation style">
              {STYLES.map((s) => (
                <button
                  key={s.value}
                  onClick={() => setActiveTab(s.value)}
                  className={`tab-btn ${activeTab === s.value ? 'active' : ''}`}
                  role="tab"
                  aria-selected={activeTab === s.value}
                  id={`tab-${s.value}`}
                  aria-controls={`tabpanel-${s.value}`}
                >
                  {s.label}
                </button>
              ))}
            </div>

            {ttsEnabled && (
              <div className="voice-selector" role="group" aria-label="Choose a voice">
                {VOICES.map((v) => (
                  <button
                    key={v.key}
                    onClick={() => setSelectedVoice(v.key)}
                    className={`voice-btn ${selectedVoice === v.key ? 'active' : ''}`}
                    aria-pressed={selectedVoice === v.key}
                    aria-label={`Voice: ${v.name}`}
                  >
                    {v.emoji} {v.name}
                  </button>
                ))}
              </div>
            )}

            <div
              className="tab-panel"
              role="tabpanel"
              id={`tabpanel-${activeTab}`}
              aria-labelledby={`tab-${activeTab}`}
            >
              <div className="output-box">
                {results[activeTab]?.transformed || ''}
              </div>
              <div className="output-actions">
                <button onClick={handleCopy} className="button copy-button" aria-label="Copy translation to clipboard">
                  {copySuccess ? '✅ Copied!' : '📋 Copy'}
                </button>
                <button
                  onClick={handleRegen}
                  disabled={regenLoading}
                  className="button regen-button"
                  aria-label="Regenerate this translation"
                >
                  {regenLoading ? '⏳' : '🔁 Regenerate'}
                </button>
                {ttsEnabled && (
                  <button
                    onClick={handleListen}
                    disabled={audioLoading}
                    className={`button listen-button ${isPlaying ? 'playing' : ''}`}
                    aria-label={isPlaying ? 'Stop audio playback' : 'Listen to translation'}
                  >
                    {audioLoading ? '⏳' : isPlaying ? '⏹ Stop' : '🔊 Listen'}
                  </button>
                )}
                <button
                  onClick={handleToggleCurrentFavorite}
                  className="button favorite-button"
                  aria-label={currentFavorited ? 'Remove from favorites' : 'Add to favorites'}
                  aria-pressed={currentFavorited}
                >
                  {currentFavorited ? '⭐ Favorited' : '☆ Favorite'}
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
                aria-label={`Use example: ${example.text}`}
              >
                "{example.text.substring(0, 20)}..."
              </button>
            ))}
          </div>
        </div>

        {/* Favorites */}
        {favorites.length > 0 && (
          <div className="history favorites">
            <div className="history-header">
              <h3 className="history-title">⭐ Favorites</h3>
              <div className="history-header-actions">
                <button onClick={handleExportFavorites} className="export-favorites-btn">
                  Export as JSON
                </button>
                <button onClick={handleClearFavorites} className="clear-history-btn" aria-label="Clear all favorites">
                  Clear
                </button>
              </div>
            </div>
            <div className="history-list">
              {favorites.map((item) => (
                <div
                  key={item.id}
                  className="history-item favorite-item"
                  onClick={() => handleLoadItem(item)}
                  role="button"
                  tabIndex={0}
                  onKeyDown={(e) => { if (e.key === 'Enter') handleLoadItem(item); }}
                >
                  <div className="history-original">{item.original.substring(0, 40)}...</div>
                  <div className="history-item-footer">
                    <small className="history-date">
                      {new Date(item.timestamp).toLocaleTimeString()}
                    </small>
                    <button
                      onClick={(e) => { e.stopPropagation(); handleToggleFavorite(item); }}
                      className="favorite-star-btn"
                      aria-label="Remove from favorites"
                    >
                      ⭐
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* History */}
        {history.length > 0 && (
          <div className="history">
            <div className="history-header">
              <h3 className="history-title">📜 Recent Transformations</h3>
              <button onClick={handleClearHistory} className="clear-history-btn" aria-label="Clear translation history">
                Clear
              </button>
            </div>
            <div className="history-list">
              {history.map((item) => (
                <div
                  key={item.id}
                  className="history-item"
                  onClick={() => handleLoadItem(item)}
                  role="button"
                  tabIndex={0}
                  onKeyDown={(e) => { if (e.key === 'Enter') handleLoadItem(item); }}
                >
                  <div className="history-original">{item.original.substring(0, 40)}...</div>
                  <div className="history-item-footer">
                    <small className="history-date">
                      {new Date(item.timestamp).toLocaleTimeString()}
                    </small>
                    <button
                      onClick={(e) => { e.stopPropagation(); handleToggleFavorite(item); }}
                      className="favorite-star-btn"
                      aria-label={isFavorited(item.id) ? 'Remove from favorites' : 'Add to favorites'}
                    >
                      {isFavorited(item.id) ? '⭐' : '☆'}
                    </button>
                  </div>
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
