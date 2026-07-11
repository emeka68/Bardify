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
