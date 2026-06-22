# Shakespeare Translator Frontend — Deployment Guide

Complete guide for building and deploying the React PWA to Vercel.

---

## Local Development

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Create Environment File

```bash
cp .env.example .env.local
```

Edit `.env.local` and set your API URL:

```env
REACT_APP_API_URL=http://localhost:8000
```

### 3. Start Development Server

```bash
npm start
```

Server runs at: `http://localhost:3000`

### 4. Test the App

- Open `http://localhost:3000` in your browser
- Try transforming some text
- Check the browser console for service worker logs

---

## Build for Production

### Create Optimized Build

```bash
npm run build
```

This creates a production-ready build in the `build/` directory.

### Test Production Build Locally

```bash
npm install -g serve
serve -s build
```

Open `http://localhost:3000` to test the production build.

---

## Deploy to Vercel

### Option 1: Deploy with Git (Recommended)

**Step 1: Push to GitHub**

```bash
git add .
git commit -m "feat: React webapp + PWA for Shakespeare Translator"
git push origin main
```

**Step 2: Connect to Vercel**

1. Go to [vercel.com](https://vercel.com)
2. Sign in with GitHub
3. Click "New Project"
4. Select the `shakespeare-translator` repository
5. Configure:
   - **Root Directory:** `frontend`
   - **Framework:** React
   - **Build Command:** `npm run build`
6. Add environment variable:
   - `REACT_APP_API_URL` → Your backend URL (or `http://localhost:8000` for dev)
7. Click "Deploy"

**Step 3: Update Backend API URL**

Once deployed, get your Vercel URL (e.g., `https://shakespeare-translator.vercel.app`)

For production, update your backend CORS in `main.py`:

```python
CORS_ORIGINS=["https://shakespeare-translator.vercel.app"]
```

Then redeploy the backend.

---

### Option 2: Deploy with Vercel CLI

**Step 1: Install Vercel CLI**

```bash
npm install -g vercel
```

**Step 2: Deploy**

```bash
cd frontend
vercel deploy
```

Follow the prompts to connect your GitHub account and configure the project.

**Step 3: Set Environment Variables**

```bash
vercel env add REACT_APP_API_URL
# Enter your backend URL when prompted
```

**Step 4: Redeploy**

```bash
vercel deploy --prod
```

---

## Configure Environment Variables

### In Vercel Dashboard

1. Go to your project settings
2. Click "Environment Variables"
3. Add:
   - **Name:** `REACT_APP_API_URL`
   - **Value:** `https://your-backend-api.com`
   - **Environments:** Production, Preview, Development

### For Different Environments

**Development (.env.local):**
```env
REACT_APP_API_URL=http://localhost:8000
```

**Preview (Vercel staging):**
```env
REACT_APP_API_URL=https://preview-api.your-domain.com
```

**Production (Vercel live):**
```env
REACT_APP_API_URL=https://api.your-domain.com
```

---

## PWA Features

The app includes PWA support:

- ✅ Service Worker caching
- ✅ Installable on mobile/desktop
- ✅ Offline fallback
- ✅ Web app manifest
- ✅ Fast loading from cache

### Install the App

**On Mobile:**
1. Open the app in your phone's browser
2. Tap the menu icon (⋯)
3. Tap "Install app" or "Add to Home Screen"
4. Follow prompts

**On Desktop:**
1. Open the app in Chrome/Edge
2. Click the install icon in the address bar
3. Click "Install"
4. The app opens in its own window

---

## Backend Configuration

### Update CORS for Your Domain

After deploying the frontend, update your backend `main.py`:

```python
# frontend/src/App.jsx already configured to use env variable
# Update backend CORS_ORIGINS

CORS_ORIGINS=[
    "https://shakespeare-translator.vercel.app",
    "http://localhost:3000",  # Keep for local dev
]
```

Redeploy the backend:

```bash
# On your VPS or wherever backend is hosted
git pull
# ... restart your backend service
```

---

## Troubleshooting

### API Calls Return 503 (Service Unavailable)

**Cause:** Backend is offline or not reachable

**Solution:**
1. Check backend is running
2. Verify `REACT_APP_API_URL` is correct in `.env`
3. Check CORS settings match your frontend URL
4. Test API directly: `curl https://your-backend/health`

### PWA Won't Install

**Cause:** HTTPS required for PWA on production

**Solution:**
1. Vercel automatically provides HTTPS (✅)
2. For custom domain, ensure SSL certificate is valid

### Build Fails on Vercel

**Cause:** Missing environment variables or incorrect Node version

**Solution:**
1. Check all `REACT_APP_*` variables are set in Vercel
2. Ensure Node.js 18+ is used
3. Check build logs in Vercel dashboard

### Service Worker Issues

**Cause:** Cache conflicts or SW not updating

**Solution:**
1. Clear site data in browser DevTools
2. Uninstall and reinstall the app
3. Clear Vercel's cache: Settings → Deployments → Redeploy

---

## Performance Optimization

### Vercel Analytics

Monitor performance:

1. Enable Vercel Analytics in project settings
2. View Core Web Vitals dashboard
3. Optimize based on metrics

### Bundle Size

Check bundle size:

```bash
npm install --save-dev source-map-explorer
npm run build
npx source-map-explorer 'build/static/js/*.js'
```

---

## Custom Domain

### Add Custom Domain to Vercel

1. Go to project Settings → Domains
2. Click "Add"
3. Enter your domain (e.g., `shakespeare.your-domain.com`)
4. Follow DNS configuration steps
5. Verify domain

### Update Backend CORS

```python
CORS_ORIGINS=[
    "https://shakespeare.your-domain.com",
    "http://localhost:3000",
]
```

---

## Continuous Deployment

### Auto-Deploy on Push

Vercel automatically redeploys when you push to your main branch.

**To disable:**
1. Settings → Git
2. Toggle "Ignore Build Step" if needed

**To preview changes:**
1. Create a PR on GitHub
2. Vercel creates a preview deployment
3. Test before merging to main

---

## Rollback

If something breaks after deploy:

```bash
vercel rollback
```

Or through dashboard:
1. Deployments tab
2. Find the previous good deployment
3. Click the three dots → "Promote to Production"

---

## Monitoring & Logs

### View Deployment Logs

```bash
vercel logs [deployment-url]
```

### Monitor in Real Time

```bash
vercel logs --follow
```

### Check Live App

Once deployed, visit:
- Main: `https://shakespeare-translator.vercel.app`
- API Docs: `https://your-backend/docs`
- GitHub: `https://github.com/emeka68/shakespeare-translator`

---

## Next Steps

1. ✅ Build locally and test
2. ✅ Push to GitHub
3. ✅ Deploy to Vercel
4. ✅ Set environment variables
5. ✅ Update backend CORS
6. ✅ Test production app
7. ✅ Share on LinkedIn/Twitter

---

**Your app is live! 🎉**
