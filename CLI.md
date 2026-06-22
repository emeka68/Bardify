# Shakespeare Translator — CLI Tool

**Command-line interface for transforming text into Shakespearean English**

Use the CLI tool to transform text from the command line, pipes, or files.

---

## Installation

### From Source (Recommended)

```bash
git clone https://github.com/emeka68/shakespeare-translator.git
cd shakespeare-translator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install with CLI support
pip install -e .
```

This makes `shakespeare` available globally in your terminal.

### Without Installation (Direct)

```bash
python cli.py transform "Your text here"
```

---

## Usage

### Single Text

```bash
shakespeare "Hey, what's up?"
```

**Output:**
```
📝 Original:
Hey, what's up?

🎭 Shakespearean:
==================================================
Hark! What manner of tidings dost thou bring?
==================================================
```

### Pipe Input

```bash
echo "I'm just chilling" | shakespeare
```

### From File

```bash
shakespeare --file input.txt
```

### To File

```bash
shakespeare "Hello world" --output output.txt
```

### Interactive Mode

```bash
shakespeare --interactive
```

Reads text line-by-line from your input:

```
🎭 Shakespeare Translator — Interactive Mode
Enter text to transform (Ctrl+C to exit):

→ Hey how are you
← Hark! How dost thou fare?

→ What's up
← What manner of tidings dost thou bring?
```

### Quiet Mode (Output Only)

```bash
shakespeare "Hello" --quiet
```

**Output:**
```
Hark, well met!
```

Perfect for piping to other commands.

### Show Token Usage

```bash
shakespeare "Hello" --show-tokens
```

Shows how many Claude API tokens the transformation used.

---

## Advanced Examples

### Batch Process Files

```bash
# Transform all lines in a file
cat messages.txt | shakespeare > transformed.txt
```

### Chain with Other Commands

```bash
# Use with fortune
fortune | shakespeare

# Get random Shakespeare quote
shuf -n 1 quotes.txt | shakespeare

# Process CSV files
cat data.csv | shakespeare > data-transformed.csv
```

### Create Shell Aliases

```bash
# Add to ~/.zshrc or ~/.bashrc
alias to-shakespeare='shakespeare --quiet'

# Usage:
echo "Hey!" | to-shakespeare
```

### One-Liners

```bash
# Transform a sentence from the web
curl https://example.com | grep "sentence" | shakespeare

# Transform git commit messages
git log --oneline | head -5 | shakespeare

# Transform system messages
dmesg | tail -20 | shakespeare
```

---

## Options

### Global Options

- `--version` — Show version
- `--help` — Show help

### Transform Command Options

- `--file, -f` — Read from file instead of argument
- `--output, -o` — Write to file (default: stdout)
- `--interactive, -i` — Interactive mode
- `--quiet, -q` — Output only transformed text (no headers)
- `--show-tokens, -t` — Display token usage
- `--help` — Show help for this command

### Other Commands

```bash
shakespeare config      # Show current configuration
shakespeare examples    # Show usage examples
shakespeare version     # Show version info
```

---

## Configuration

The CLI uses the same `.env` file as the backend.

### Required

```env
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### Optional

```env
# API endpoint (for remote backend)
API_BASE_URL=http://localhost:8000

# Logging
LOG_LEVEL=INFO
```

---

## Examples

### Poetry/Verse

```bash
# Transform poetry
shakespeare "Shall I compare thee to a summer's day"
```

### Technical Writing

```bash
shakespeare "The API returns a JSON response with status code 200"
```

### Social Media Posts

```bash
shakespeare "Just shipped a new feature! 🚀"
```

### Git Commits

```bash
git commit -m "$(echo 'Fixed critical bug' | shakespeare --quiet)"
```

### Documentation

```bash
# Transform README content
shakespeare --file README.md > README_SHAKESPEARE.md
```

---

## Performance Tips

### Speed Up Multiple Transformations

Use `--quiet` mode for faster output:

```bash
# Faster
cat input.txt | shakespeare --quiet

# Slower (includes headers)
cat input.txt | shakespeare
```

### Reduce Token Usage

- Shorter texts cost fewer tokens
- Around $0.003 per transformation (Claude API pricing)
- Interactive mode batches requests efficiently

### Offline Mode

The CLI requires internet access for the Claude API. For offline use, consider:

1. **Pre-transform common phrases** and cache them
2. **Use a local LLM** (requires different setup)
3. **Build a cache layer** (future enhancement)

---

## Troubleshooting

### Command Not Found

If `shakespeare` isn't recognized:

```bash
# Reinstall with editable mode
pip install -e .

# Or use directly:
python cli.py transform "text"
```

### API Key Error

```
❌ Error: ANTHROPIC_API_KEY not set
```

**Solution:**
1. Create `.env` file in project root
2. Add: `ANTHROPIC_API_KEY=sk-ant-your-key`
3. Verify file is in the right directory

### Connection Error

```
❌ Error: Cannot reach the server
```

**Solution:**
1. Ensure backend is running: `python main.py`
2. Check `API_BASE_URL` in `.env`
3. Verify network connectivity

---

## Tips & Tricks

### Create a Function

```bash
# Add to ~/.zshrc
shak() {
  echo "$@" | shakespeare --quiet
}

# Usage:
shak "Hello world"
```

### Transform Large Files

```bash
# Split and process in batches
split -l 10 large.txt batch_

for file in batch_*; do
  shakespeare --file "$file" >> output.txt
done
```

### Monitor Token Usage

```bash
# Track API costs
for text in "hello" "how are you" "what's up"; do
  shakespeare "$text" --show-tokens
done
```

### Create a Script

```bash
#!/bin/bash
# shak.sh - Batch Shakespeare translator

for file in "$@"; do
  echo "📄 Processing $file..."
  shakespeare --file "$file" --output "${file%.txt}_shakespeare.txt"
  echo "✅ Done"
done
```

---

## Integration Examples

### With Python Scripts

```python
import subprocess

def transform_to_shakespeare(text):
    result = subprocess.run(
        ["shakespeare", "--quiet"],
        input=text,
        capture_output=True,
        text=True
    )
    return result.stdout.strip()

# Usage
print(transform_to_shakespeare("Hey what's up?"))
```

### With Node.js

```javascript
const { exec } = require('child_process');

function transformToShakespeare(text) {
  return new Promise((resolve, reject) => {
    exec(`echo "${text}" | shakespeare --quiet`, (error, stdout) => {
      if (error) reject(error);
      resolve(stdout.trim());
    });
  });
}
```

### With Shell Scripts

```bash
#!/bin/bash
# process_emails.sh

while IFS= read -r email; do
  subject=$(echo "$email" | grep "Subject:" | cut -d: -f2)
  shakespearian_subject=$(echo "$subject" | shakespeare --quiet)
  echo "New subject: $shakespearian_subject"
done < emails.txt
```

---

## Performance Benchmarks

On a local machine with the backend running:

- **Single text:** ~1.5-2 seconds
- **Interactive mode:** ~2 seconds per transformation
- **Batch (10 items):** ~20 seconds total
- **Pipe throughput:** Limited by Claude API rate (30 req/min)

---

## Contributing

Found a bug? Want a feature?

1. Open an issue on GitHub
2. Submit a PR with your improvements
3. Follow the code style (`black` formatting)

---

## License

MIT — Use freely

---

**Transform your words on the command line. 🎭**

For more, see:
- Main README: `README.md`
- API Documentation: Run `python main.py` and visit `http://localhost:8000/docs`
- Backend Docs: `SETUP.md`
