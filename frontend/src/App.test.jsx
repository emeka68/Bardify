import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import App from './App';

test('renders the title and input textarea', () => {
  render(<App />);
  expect(screen.getByText(/Shakespeare Translator/i)).toBeInTheDocument();
  expect(screen.getByPlaceholderText(/Enter modern English text/i)).toBeInTheDocument();
});

test('transform button is disabled until text is entered', () => {
  render(<App />);
  const button = screen.getByRole('button', { name: /Transform to Shakespeare/i });
  expect(button).toBeDisabled();
});

test('clear button resets the input field', () => {
  render(<App />);
  const textarea = screen.getByPlaceholderText(/Enter modern English text/i);

  fireEvent.change(textarea, { target: { value: 'test input' } });
  expect(textarea.value).toBe('test input');

  const clearButton = screen.getByRole('button', { name: /Clear/i });
  fireEvent.click(clearButton);

  expect(textarea.value).toBe('');
});

test('favorites loaded from localStorage render in the Favorites section', () => {
  const favorite = {
    id: 123,
    original: 'A saved favorite translation',
    results: {
      standard: { transformed: 'Hark! A saved favorite translation.' },
      dramatic: { transformed: 'By the heavens, a saved favorite translation!' },
      poetic: { transformed: 'A saved, favored translation of old.' },
    },
    timestamp: new Date().toISOString(),
  };
  localStorage.setItem('shakespeare-favorites', JSON.stringify([favorite]));

  render(<App />);

  expect(screen.getByText(/⭐ Favorites/i)).toBeInTheDocument();
  expect(screen.getByText(/A saved favorite translation/i)).toBeInTheDocument();

  localStorage.removeItem('shakespeare-favorites');
});

test('removing a favorite from the Favorites list removes it from the DOM', () => {
  const favorite = {
    id: 456,
    original: 'Another favorite to remove',
    results: {
      standard: { transformed: 'Hark!' },
      dramatic: { transformed: 'By the heavens!' },
      poetic: { transformed: 'A verse most fine.' },
    },
    timestamp: new Date().toISOString(),
  };
  localStorage.setItem('shakespeare-favorites', JSON.stringify([favorite]));

  render(<App />);
  expect(screen.getByText(/Another favorite to remove/i)).toBeInTheDocument();

  const removeButton = screen.getByRole('button', { name: /Remove from favorites/i });
  fireEvent.click(removeButton);

  expect(screen.queryByText(/Another favorite to remove/i)).not.toBeInTheDocument();

  localStorage.removeItem('shakespeare-favorites');
});
