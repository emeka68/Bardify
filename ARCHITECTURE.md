# Shakespeare Translator — Architecture & Setup

Complete technical overview and setup instructions.

---

## Project Structure

```
shakespeare-translator/
├── Backend (FastAPI)
│   ├── main.py                # FastAPI application
│   ├── transformer.py         # Claude API integration
│   ├── config.py              # Configuration management
│   ├── test_api.py            # Test suite
│   ├── requirements.txt        # Python dependencies
│   ├── .env.example            # Environment template
│   ├── README.md               # Backend docs
│   └── .gitignore
│
├── Frontend (React)
│   ├── public/
│   │   ├── index.html         # HTML template
│   │   ├── manifest.json      # PWA manifest
│   │   └── service-worker.js  # Service worker
│   ├── src/
│   │   ├── App.jsx            # Main React component
│   │   ├── App.css            # Component styles
│   │   └── index.js           # Entry point
│   ├── package.json           # Node dependencies
│   ├── .env.example           # Environment template
│   ├── vercel.json            # Vercel config
│   ├── DEPLOY.md              # Deployment guide
│   └── .gitignore
│
├── README.md                  # Project overview
├── SETUP.md                   # Setup guide
└── ARCHITECTURE.md            # This file
```

---

## Technology Stack

### Backend
- **Framework:** FastAPI (Python)
- **AI/LLM:** Claude API (Anthropic)
- **Server:** Uvicorn
- **Deployment:** VPS + Gunicorn

### Frontend
- **Framework:** React 18
- **Styling:** CSS3 (responsive, modern)
- **PWA:** Service Worker + Manifest
- **Deployment:** Vercel
- **State:** React hooks (useState, useEffect)
- **Storage:** localStorage (history caching)

### Infrastructure
- **Backend API:** Your VPS (port 8000)
- **Frontend:** Vercel CDN (global)
- **Database:** None (stateless)
- **Caching:** Browser + Service Worker

---

## Data Flow

```
User Input (React)
       ↓
Browser Fetch API
       ↓
FastAPI /transform endpoint
       ↓
Claude API (transformation)
       ↓
Return Shakespearean text
       ↓
Display in React + Cache in localStorage
```

---

## Setup Timeline

### Phase 1: Local Development (1-2 hours)

1. **Backend Setup**
   ```bash
   cd ~/shakespeare-translator
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env
   # Add ANTHROPIC_API_KEY to .env
   python main.py
   ```

2. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   cp .env.example .env.local
   # REACT_APP_API_URL=http://localhost:8000
   npm start
   ```

3. **Test Locally**
   - Open `http://localhost:3000`
   - Try transforming text
   - Check both console logs

### Phase 2: Push to GitHub (30 min)

```bash
git add .
git commit -m "feat: Shakespeare Translator - Backend + React PWA"
git push origin main
```

### Phase 3: Deploy Backend (30 min - 1 hour)

**To Your VPS:**

```bash
# On your VPS
ssh user@vps-ip
git clone https://github.com/yourusername/shakespeare-translator.git
cd shakespeare-translator
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn

# Setup .env
cp .env.example .env
# Edit with your ANTHROPIC_API_KEY

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 main:app &
```

**Or via systemd (recommended):**

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
ExecStart=/home/deploy/deploy/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 main:app
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable shakespeare
sudo systemctl start shakespeare
```

### Phase 4: Deploy Frontend to Vercel (10 min)

1. Go to [vercel.com](https://vercel.com)
2. Import the GitHub repository
3. Set "Root Directory" to `frontend`
4. Add environment variables:
   - `REACT_APP_API_URL=https://your-backend-api.com`
5. Click "Deploy"

### Phase 5: Connect Frontend to Backend (10 min)

Update backend CORS in `main.py`:

```python
CORS_ORIGINS=[
    "https://shakespeare-translator.vercel.app",
    "http://localhost:3000",
]
```

Redeploy backend and test.

---

## API Endpoints

### Transform Single Text

**POST** `/transform`

```bash
curl -X POST http://localhost:8000/transform \
  -H "Content-Type: application/json" \
  -d '{"text": "Hey, how are you?"}'
```

**Response:**
```json
{
  "original": "Hey, how are you?",
  "transformed": "Hark! How dost thou fare?",
  "timestamp": "2026-05-30T14:00:00",
  "model": "claude-3-5-sonnet-20241022",
  "usage": {
    "input_tokens": 45,
    "output_tokens": 20,
    "total_tokens": 65
  },
  "error": null
}
```

### Batch Transform

**POST** `/batch`

```bash
curl -X POST http://localhost:8000/batch \
  -H "Content-Type: application/json" \
  -d '{"texts": ["Hello", "How are you?"]}'
```

### Health Check

**GET** `/health`

```bash
curl http://localhost:8000/health
```

### API Documentation

**GET** `/docs` (Swagger UI)

Access at `http://backend-url/docs`

---

## Configuration

### Backend (.env)

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

### Frontend (.env.local)

```env
REACT_APP_API_URL=http://localhost:8000
```

---

## Features

### Complete
- ✅ Text transformation to Shakespearean English
- ✅ Error handling (empty text, API errors, offline)
- ✅ Rate limiting (30 req/min per IP)
- ✅ Token usage tracking
- ✅ Copy to clipboard
- ✅ Transformation history (localStorage)
- ✅ Example buttons
- ✅ Responsive design
- ✅ PWA (installable, offline support)
- ✅ Service Worker caching

### Coming Soon
- 🔄 Voice output (Shakespeare accent TTS)
- 🔄 Electron desktop app
- 🔄 Share transformations
- 🔄 User accounts & sync history

---

## Performance

### Metrics to Track

1. **API Response Time:** <2s for transformation
2. **Bundle Size:** ~150KB (gzipped)
3. **Lighthouse Score:** 90+
4. **Web Vitals:** LCP <2.5s, FID <100ms, CLS <0.1

### Optimizations Done

- Lazy loading service worker
- CSS minification
- Code splitting (React)
- Image optimization (SVG icons)
- Caching strategy (cache-first for assets, network-first for API)

---

## Troubleshooting

### Backend Issues

**Error:** `ANTHROPIC_API_KEY not set`
- Check `.env` file exists
- Ensure API key is valid format (sk-ant-...)

**Error:** `Address already in use`
- Change PORT in `.env`
- Or: `lsof -ti:8000 | xargs kill -9`

**Error:** CORS policy violation
- Update `CORS_ORIGINS` in `main.py`
- Include frontend URL
- Redeploy backend

### Frontend Issues

**Can't reach API**
- Check `REACT_APP_API_URL` in `.env`
- Ensure backend is running
- Test with curl first

**Service Worker not installing**
- Check HTTPS on production (Vercel handles this)
- Clear browser cache and DevTools

**Offline mode not working**
- Check browser supports service workers
- Verify service-worker.js is accessible

---

## Security

### Best Practices Implemented

✅ Environment variables for secrets
✅ CORS configured (no wildcard)
✅ Rate limiting enabled
✅ Input validation (max 2000 chars)
✅ Error messages don't leak data
✅ HTTPS enforced (Vercel)
✅ Service Worker only caches GET requests

### To Do

- [ ] Add API key rotation mechanism
- [ ] Implement user authentication (optional)
- [ ] Add request signing for sensitive operations
- [ ] Monitor for abuse patterns

---

## Monitoring & Logging

### Backend Logs

```bash
# View live logs
tail -f opscore.log

# Or with systemd
sudo journalctl -u shakespeare -f
```

### Frontend Monitoring

- Vercel Analytics (built-in)
- Browser DevTools (Network, Console)
- Sentry integration (optional)

### Health Checks

```bash
# Backend
curl http://backend/health

# Frontend (Vercel status page)
# https://www.vercel-status.com
```

---

## Scaling Considerations

### Current Capacity

- **Requests:** 30 req/min per IP (configurable)
- **Concurrent:** ~50-100 depending on backend resources
- **API Costs:** ~$0.003 per transformation (Claude API)

### To Scale

1. **Add Redis for rate limiting** (currently in-memory)
2. **Implement request queueing** (Bull, Celery)
3. **Add database** for user data/history
4. **CDN for static assets** (Vercel handles this)
5. **Backend load balancing** (multiple servers)

---

## Deployment Checklist

- [ ] Backend tests pass locally (`python test_api.py`)
- [ ] Frontend builds without errors (`npm run build`)
- [ ] All environment variables set
- [ ] CORS origins updated
- [ ] Backend deployed and tested
- [ ] Frontend deployed to Vercel
- [ ] Verify API communication works
- [ ] Test offline functionality
- [ ] Test on mobile (install PWA)
- [ ] Share on GitHub/LinkedIn

---

## Resources

- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **React Docs:** https://react.dev/
- **Claude API:** https://docs.anthropic.com/
- **Vercel Docs:** https://vercel.com/docs
- **PWA Guide:** https://web.dev/progressive-web-apps/

---

**Built with ❤️ for makers who want to ship fast**
