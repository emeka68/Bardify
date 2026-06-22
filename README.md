# Shakespeare Translator 🎭

**Transform modern English into Shakespearean English using Claude AI**

A humorous, shareable tool that converts everyday language into authentic 16th-century English. Built with FastAPI and powered by Claude.

---

## What It Does

Feed it modern English. Get back Shakespeare.

**Example:**
```
Input:  "Hey, what's up? I'm just chilling with my friends."
Output: "Hark! What manner of tidings dost thou bring? I am but whiling away the hours in merry company."
```

---

## Quick Start

### Installation

```bash
git clone https://github.com/emeka68/shakespeare-translator.git
cd shakespeare-translator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### Get API Key

1. Go to [console.anthropic.com/keys](https://console.anthropic.com/keys)
2. Create a new API key
3. Copy it into your `.env` file:

```env
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### Run Server

```bash
python main.py
```

Server starts at `http://localhost:8000`

---

## API Endpoints

### Transform Single Text

**POST** `/transform`

```bash
curl -X POST http://localhost:8000/transform \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, how are you today?"}'
```

**Response:**
```json
{
  "original": "Hello, how are you today?",
  "transformed": "Hark! How dost thou fare on this fine day?",
  "timestamp": "2026-05-30T00:30:00.123456",
  "model": "claude-3-5-sonnet-20241022",
  "usage": {
    "input_tokens": 45,
    "output_tokens": 22,
    "total_tokens": 67
  },
  "error": null
}
```

### Transform Multiple Texts

**POST** `/batch`

```bash
curl -X POST http://localhost:8000/batch \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      "Hello world",
      "How are you?",
      "Lets grab some coffee"
    ]
  }'
```

### Health Check

**GET** `/health`

```bash
curl http://localhost:8000/health
```

### API Docs

**GET** `/docs`

```bash
curl http://localhost:8000/docs
```

---

## Configuration

### Environment Variables

See `.env.example` for all options:

```env
# Claude API Key (required)
ANTHROPIC_API_KEY=sk-ant-...

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=false

# Model
MODEL=claude-3-5-sonnet-20241022

# Rate Limiting
RATE_LIMIT_PER_MINUTE=30

# CORS
CORS_ORIGINS=["http://localhost:3000", ...]
```

---

## Deployment

### Deploy to Your VPS

```bash
# SSH into your VPS
ssh user@your-vps-ip

# Clone repo
git clone https://github.com/emeka68/shakespeare-translator.git
cd shakespeare-translator

# Install dependencies
pip install -r requirements.txt

# Set environment
cp .env.example .env
# Add ANTHROPIC_API_KEY to .env

# Run with gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 main:app
```

### Deploy to Vercel (Frontend)

See `frontend/` directory for React app deployment.

```bash
cd frontend
vercel deploy
```

---

## Frontend Integration

The React frontend sends requests to your FastAPI backend:

```javascript
const response = await fetch('http://your-backend/transform', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ text: inputText })
});

const data = await response.json();
console.log(data.transformed);
```

---

## Limitations

- **Max 2000 characters** per request
- **Max 10 texts** per batch request
- **Rate limit**: 30 requests per minute (per IP)
- **Token costs**: Each request costs ~50 tokens (varies)

---

## Examples

### Modern Tech Slang → Shakespeare

```
Input:  "That new framework is bussin no cap"
Output: "Verily, this new framework doth possess remarkable excellence without deception"
```

### Modern Casual → Shakespeare

```
Input:  "Just vibing in the coffee shop"
Output: "I am but idling most contentedly within this tavern of brewed beans"
```

### Modern Sales → Shakespeare

```
Input:  "Our product is the best on the market"
Output: "Our wares are unrivaled throughout the realm and held in highest esteem"
```

---

## Tech Stack

- **Framework**: FastAPI (Python)
- **AI**: Claude API (Anthropic)
- **Frontend**: React (coming soon)
- **Deployment**: VPS + Vercel

---

## Architecture

```
shakespeare-translator/
├── main.py              # FastAPI app
├── config.py            # Configuration management
├── transformer.py       # Claude API integration
├── requirements.txt     # Dependencies
├── .env.example         # Environment template
└── frontend/            # React frontend (future)
    ├── src/
    └── package.json
```

---

## Contributing

Found a bug? Have ideas for improvement? Open an issue or PR on GitHub.

---

## Author

**Nnaemeka Duru**

- GitHub: [@emeka68](https://github.com/emeka68)
- Twitter: [@SirTivaa](https://twitter.com/SirTivaa)
- LinkedIn: [Nnaemeka Duru](https://linkedin.com/in/nduru)

---

## License

MIT — Do whatever you want with it.

---

## Fun Facts

- Built in 1 night
- Uses Claude's reasoning to understand context
- Handles colloquialisms, slang, and modern references
- Preserves original meaning while adding flair
- Rate-limited to prevent abuse

---

**Transform your words. Embrace the Bard. 🎭**
