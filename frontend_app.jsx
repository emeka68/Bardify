/**
 * Shakespeare Translator — React Frontend
 * 
 * Simple, single-file React component for transforming text.
 * This is a starter template. Create a full React app with:
 *   npx create-react-app frontend
 * Then use this as src/App.jsx
 */

import React, { useState } from 'react';

const ShakespeareTranslator = () => {
  const [input, setInput] = useState('');
  const [output, setOutput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [tokenUsage, setTokenUsage] = useState(null);
  const [copySuccess, setCopySuccess] = useState(false);

  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  const handleTransform = async () => {
    if (!input.trim()) {
      setError('Please enter some text');
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
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Transformation failed');
      }

      const data = await response.json();

      setOutput(data.transformed);
      if (data.usage) {
        setTokenUsage(data.usage);
      }
    } catch (err) {
      setError(err.message || 'An error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(output);
    setCopySuccess(true);
    setTimeout(() => setCopySuccess(false), 2000);
  };

  const handleClear = () => {
    setInput('');
    setOutput('');
    setError('');
    setTokenUsage(null);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      handleTransform();
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1 style={styles.title}>🎭 Shakespeare Translator</h1>
        <p style={styles.subtitle}>
          Transform modern English into Shakespearean English
        </p>
      </div>

      <div style={styles.content}>
        {/* Input Section */}
        <div style={styles.section}>
          <label style={styles.label}>Your Text</label>
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Enter modern English text..."
            style={styles.textarea}
            disabled={loading}
            maxLength={2000}
          />
          <div style={styles.charCount}>
            {input.length} / 2000 characters
          </div>
        </div>

        {/* Buttons */}
        <div style={styles.buttonGroup}>
          <button
            onClick={handleTransform}
            disabled={loading || !input.trim()}
            style={{
              ...styles.button,
              ...styles.primaryButton,
              opacity: loading || !input.trim() ? 0.6 : 1,
            }}
          >
            {loading ? '⏳ Transforming...' : '✨ Transform to Shakespeare'}
          </button>
          <button
            onClick={handleClear}
            disabled={loading}
            style={{
              ...styles.button,
              ...styles.secondaryButton,
            }}
          >
            Clear
          </button>
        </div>

        {/* Error Message */}
        {error && (
          <div style={styles.error}>
            <strong>❌ Error:</strong> {error}
          </div>
        )}

        {/* Output Section */}
        {output && (
          <div style={styles.section}>
            <label style={styles.label}>Shakespearean Version</label>
            <div style={styles.outputBox}>
              <p>{output}</p>
            </div>
            <div style={styles.outputActions}>
              <button
                onClick={handleCopy}
                style={styles.copyButton}
              >
                {copySuccess ? '✅ Copied!' : '📋 Copy'}
              </button>
            </div>

            {/* Token Usage */}
            {tokenUsage && (
              <div style={styles.tokenInfo}>
                <small>
                  🔢 Tokens used: {tokenUsage.total_tokens}
                  (input: {tokenUsage.input_tokens}, output: {tokenUsage.output_tokens})
                </small>
              </div>
            )}
          </div>
        )}

        {/* Examples */}
        <div style={styles.examples}>
          <h3 style={styles.examplesTitle}>Examples</h3>
          <div style={styles.examplesList}>
            {[
              { input: "Hey, what's up?", desc: "Casual greeting" },
              { input: "That startup is totally fire", desc: "Modern slang" },
              { input: "I'm just chilling", desc: "Casual activity" },
              { input: "No cap, for real", desc: "Internet slang" },
            ].map((example, idx) => (
              <button
                key={idx}
                onClick={() => setInput(example.input)}
                style={styles.exampleButton}
                title={example.desc}
              >
                "{example.input}"
              </button>
            ))}
          </div>
        </div>
      </div>

      <div style={styles.footer}>
        <p>Built with FastAPI + Claude AI</p>
        <p>
          <a href="https://github.com/emeka68/shakespeare-translator" style={styles.link}>
            GitHub
          </a>
          {' | '}
          <a href="http://localhost:8000/docs" style={styles.link}>
            API Docs
          </a>
        </p>
      </div>
    </div>
  );
};

const styles = {
  container: {
    minHeight: '100vh',
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    padding: '20px',
    fontFamily: 'sans-serif',
  },
  header: {
    textAlign: 'center',
    color: 'white',
    marginBottom: '40px',
  },
  title: {
    fontSize: '3em',
    margin: '0 0 10px 0',
  },
  subtitle: {
    fontSize: '1.2em',
    margin: '0',
    opacity: 0.9,
  },
  content: {
    maxWidth: '800px',
    margin: '0 auto',
    background: 'white',
    borderRadius: '12px',
    padding: '40px',
    boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
  },
  section: {
    marginBottom: '30px',
  },
  label: {
    display: 'block',
    fontSize: '1.1em',
    fontWeight: 'bold',
    marginBottom: '10px',
    color: '#333',
  },
  textarea: {
    width: '100%',
    minHeight: '150px',
    padding: '15px',
    fontSize: '1em',
    border: '2px solid #ddd',
    borderRadius: '8px',
    fontFamily: 'inherit',
    resize: 'vertical',
    boxSizing: 'border-box',
    transition: 'border-color 0.3s',
  },
  charCount: {
    fontSize: '0.85em',
    color: '#999',
    marginTop: '5px',
    textAlign: 'right',
  },
  buttonGroup: {
    display: 'flex',
    gap: '10px',
    marginBottom: '30px',
  },
  button: {
    flex: 1,
    padding: '12px 20px',
    fontSize: '1em',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    fontWeight: 'bold',
    transition: 'all 0.3s',
  },
  primaryButton: {
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    color: 'white',
  },
  secondaryButton: {
    background: '#f0f0f0',
    color: '#333',
    border: '2px solid #ddd',
  },
  error: {
    background: '#fee',
    border: '2px solid #f99',
    color: '#c33',
    padding: '15px',
    borderRadius: '8px',
    marginBottom: '20px',
  },
  outputBox: {
    background: '#f9f9f9',
    border: '2px solid #ddd',
    padding: '20px',
    borderRadius: '8px',
    lineHeight: '1.6',
    fontSize: '1.05em',
  },
  outputActions: {
    marginTop: '15px',
  },
  copyButton: {
    padding: '8px 16px',
    fontSize: '0.9em',
    background: '#4CAF50',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    transition: 'background 0.3s',
  },
  tokenInfo: {
    marginTop: '10px',
    padding: '10px',
    background: '#f0f0f0',
    borderRadius: '6px',
    color: '#666',
  },
  examples: {
    marginTop: '40px',
    paddingTop: '30px',
    borderTop: '2px solid #eee',
  },
  examplesTitle: {
    marginTop: '0',
    color: '#333',
  },
  examplesList: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '10px',
  },
  exampleButton: {
    padding: '12px',
    background: '#f5f5f5',
    border: '2px solid #ddd',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '0.9em',
    transition: 'all 0.3s',
  },
  footer: {
    textAlign: 'center',
    color: 'white',
    marginTop: '40px',
    fontSize: '0.9em',
  },
  link: {
    color: 'white',
    textDecoration: 'none',
    borderBottom: '2px solid white',
  },
};

export default ShakespeareTranslator;
