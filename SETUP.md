# Shakespeare Translator — Setup Guide

Quick setup for local development and deployment.

---

## Local Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/emeka68/shakespeare-translator.git
cd shakespeare-translator
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add your Anthropic API key:

```env
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

Get your API key from: https://console.anthropic.com/keys

### 5. Run the Server

```bash
python main.py
```

Server starts at: `http://localhost:8000`

### 6. Test the API

In another terminal:

```bash
# Test direct transformation
python test_api.py

# Or use curl
curl -X POST http://localhost:8000/transform \
  -H "Content-Type: application/json" \
  -d '{"text": "Hey what is up?"}'
```

### 7. View API Documentation

Open in your browser:
```
http://localhost:8000/docs
```

---

## Frontend Setup (React)

### 1. Create React App

```bash
# From shakespeare-translator directory
npx create-react-app frontend
cd frontend
```

### 2. Copy Frontend Component

Copy `frontend_app.jsx` to `frontend/src/App.jsx`:

```bash
cp ../frontend_app.jsx src/App.jsx
```

### 3. Install Dependencies

```bash
npm install
```

### 4. Set API URL

Create `.env` file in `frontend/`:

```env
REACT_APP_API_URL=http://localhost:8000
```

### 5. Run Frontend

```bash
npm start
```

Frontend opens at: `http://localhost:3000`

---

## Deployment

### Deploy Backend to VPS

```bash
# SSH into your VPS
ssh user@your-vps-ip

# Clone repo
git clone https://github.com/emeka68/shakespeare-translator.git
cd shakespeare-translator

# Setup Python environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn

# Configure environment
cp .env.example .env
# Edit .env with your API key

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 main:app
```

For production, use a process manager like systemd:

```bash
sudo nano /etc/systemd/system/shakespeare.service
```

```ini
[Unit]
Description=Shakespeare Translator API
After=network.target

[Service]
User=deploy
WorkingDirectory=/home/deploy/shakespeare-translator
ExecStart=/home/deploy/shakespeare-translator/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 main:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable shakespeare
sudo systemctl start shakespeare
```

### Deploy Frontend to Vercel

```bash
cd frontend
npm install -g vercel
vercel deploy
```

During deployment, set environment variables:

```
REACT_APP_API_URL=https://your-backend-domain.com
```

---

## Environment Variables Reference

### Backend (`.env`)

```env
# Required
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
CORS_ORIGINS=["http://localhost:3000", "https://your-domain.com"]
```

### Frontend (`.env`)

```env
# API endpoint
REACT_APP_API_URL=http://localhost:8000
```

---

## Testing

### Run Test Suite

```bash
# Direct transformer tests
python test_api.py

# With pytest (optional)
pip install pytest
pytest test_api.py
```

### Manual API Testing

```bash
# Transform single text
curl -X POST http://localhost:8000/transform \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world"}'

# Check health
curl http://localhost:8000/health

# Batch transform
curl -X POST http://localhost:8000/batch \
  -H "Content-Type: application/json" \
  -d '{"texts": ["Hello", "How are you?"]}'
```

---

## Troubleshooting

### API Key Error

**Error:** `ANTHROPIC_API_KEY not set`

**Solution:**
1. Check `.env` file exists
2. Add your API key: `ANTHROPIC_API_KEY=sk-ant-...`
3. Restart the server

### Port Already in Use

**Error:** `Address already in use`

**Solution:**
1. Change PORT in `.env` to another port (e.g., 8001)
2. Or kill the process: `lsof -ti:8000 | xargs kill -9`

### CORS Issues

**Error:** `CORS policy: No 'Access-Control-Allow-Origin'`

**Solution:**
1. Update `CORS_ORIGINS` in `.env`
2. Add your frontend URL:
   ```env
   CORS_ORIGINS=["http://localhost:3000", "https://your-frontend.vercel.app"]
   ```

### Slow Responses

**Issue:** Requests taking >5 seconds

**Solutions:**
1. Check API key is valid
2. Reduce text length (max 2000 chars)
3. Check rate limiting: 30 requests/min
4. Monitor token usage

---

## Next Steps

1. ✅ Set up local development
2. ✅ Test the API
3. ✅ Build the frontend
4. ✅ Deploy to production
5. 🔄 Share on GitHub/LinkedIn
6. 🔄 Integrate into portfolio

---

## Support

- **Docs:** See `README.md`
- **Issues:** Open on GitHub
- **API Docs:** `http://localhost:8000/docs`

---

**Happy transforming! 🎭**
