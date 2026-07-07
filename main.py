"""
Shakespeare Translator — FastAPI Backend

A humorous app that transforms modern English into Shakespearean English.
Powered by Claude AI.

Usage:
    python main.py
    curl -X POST http://localhost:8000/transform \
        -H "Content-Type: application/json" \
        -d '{"text": "Hello, how are you today?"}'
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from config import settings, Settings
from transformer import transformer
from tts import tts_service, VOICES
from typing import Optional
import base64
import time
from collections import defaultdict
from contextlib import asynccontextmanager
from datetime import datetime, timedelta

@asynccontextmanager
async def lifespan(app: FastAPI):
    if not settings.validate():
        print("❌ Configuration validation failed")
        exit(1)
    print("\n✅ Shakespeare Translator initialized")
    settings.summary()
    yield


# Initialize FastAPI app
app = FastAPI(
    title="Shakespeare Translator",
    description="Transform modern English into Shakespearean English",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting (simple in-memory)
request_times = defaultdict(list)


class TransformRequest(BaseModel):
    """Request model for transformation."""
    text: str
    style: Optional[str] = "standard"  # standard | dramatic | poetic
    length: Optional[str] = "full"     # full | concise


class TransformResponse(BaseModel):
    """Response model for transformation."""
    original: str
    transformed: str
    timestamp: str
    model: Optional[str] = None
    style: Optional[str] = None
    length: Optional[str] = None
    usage: Optional[dict] = None
    error: Optional[str] = None


class BatchRequest(BaseModel):
    """Request model for batch transformation."""
    texts: list[str]


class SpeakRequest(BaseModel):
    """Request model for TTS."""
    text: str
    voice: str


class SpeakResponse(BaseModel):
    """Response model for TTS."""
    audio: str   # base64-encoded mp3
    voice: str
    format: str = "mp3"


def check_rate_limit(client_ip: str) -> bool:
    """Simple rate limiting check."""
    now = time.time()
    minute_ago = now - 60
    
    # Clean old requests
    request_times[client_ip] = [
        req_time for req_time in request_times[client_ip]
        if req_time > minute_ago
    ]
    
    # Check limit
    if len(request_times[client_ip]) >= settings.rate_limit_per_minute:
        return False
    
    # Record this request
    request_times[client_ip].append(now)
    return True


@app.get("/")
async def root():
    """Health check / welcome endpoint."""
    return {
        "status": "alive",
        "app": "Shakespeare Translator",
        "version": "1.0.0",
        "endpoints": {
            "transform": "POST /transform — Transform text to Shakespearean English",
            "batch": "POST /batch — Transform multiple texts",
            "health": "GET /health — Health check",
            "docs": "GET /docs — API documentation"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "model": settings.model
    }


@app.post("/transform", response_model=TransformResponse)
async def transform(request_body: TransformRequest, request: Request):
    """
    Transform modern English to Shakespearean English.
    
    Request body:
    {
        "text": "Hello, how are you today?"
    }
    
    Response:
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
    """
    
    # Get client IP for rate limiting
    client_ip = request.client.host if request.client else "unknown"
    
    # Check rate limit
    if not check_rate_limit(client_ip):
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Max {settings.rate_limit_per_minute} requests per minute"
        )
    
    # Validate input
    text = request_body.text.strip()
    
    if not text:
        raise HTTPException(
            status_code=400,
            detail="Text cannot be empty"
        )
    
    if len(text) > 2000:
        raise HTTPException(
            status_code=400,
            detail="Text too long (max 2000 characters)"
        )
    
    style = request_body.style or "standard"
    length = request_body.length or "full"

    if style not in ("standard", "dramatic", "poetic"):
        raise HTTPException(status_code=400, detail="Invalid style. Choose: standard, dramatic, poetic")
    if length not in ("full", "concise"):
        raise HTTPException(status_code=400, detail="Invalid length. Choose: full, concise")

    # Transform
    result = transformer.transform(text, style=style, length=length)
    
    if result.get("error"):
        raise HTTPException(
            status_code=500,
            detail=result["error"]
        )
    
    return TransformResponse(
        original=result["original"],
        transformed=result["transformed"],
        timestamp=result["timestamp"],
        model=result.get("model"),
        style=result.get("style"),
        length=result.get("length"),
        usage=result.get("usage"),
        error=result.get("error"),
    )


@app.post("/batch")
async def batch_transform(request_body: BatchRequest, request: Request):
    """
    Transform multiple texts (up to 10).

    Request body:
    {
        "texts": [
            "Hello world",
            "How are you?"
        ]
    }
    """

    texts = request_body.texts
    client_ip = request.client.host if request.client else "unknown"

    if not texts:
        raise HTTPException(status_code=400, detail="No texts provided")
    
    if len(texts) > 10:
        raise HTTPException(status_code=400, detail="Max 10 texts per batch")
    
    # Check rate limit for batch
    if not check_rate_limit(client_ip):
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded"
        )
    
    results = []
    for text in texts:
        text = text.strip()
        if not text or len(text) > 2000:
            continue
        
        result = transformer.transform(text)
        results.append(result)
    
    return {
        "count": len(results),
        "results": results,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/docs", tags=["documentation"])
async def docs():
    """API Documentation."""
    return {
        "title": "Shakespeare Translator API",
        "version": "1.0.0",
        "description": "Transform modern English into Shakespearean English using Claude AI",
        "endpoints": {
            "GET /": "Welcome page",
            "GET /health": "Health check",
            "POST /transform": "Transform single text",
            "POST /batch": "Transform multiple texts (up to 10)",
            "GET /docs": "This documentation"
        },
        "example": {
            "request": {
                "text": "Hey, what's up?"
            },
            "response": {
                "original": "Hey, what's up?",
                "transformed": "Hark! What manner of tidings dost thou bring?",
                "timestamp": "2026-05-30T00:30:00",
                "model": "claude-3-5-sonnet-20241022",
                "usage": {
                    "input_tokens": 50,
                    "output_tokens": 20,
                    "total_tokens": 70
                }
            }
        }
    }


@app.get("/config")
async def get_config():
    """Get current configuration (non-sensitive)."""
    return {
        "model": settings.model,
        "rate_limit": settings.rate_limit_per_minute,
        "host": settings.host,
        "port": settings.port,
        "debug": settings.debug
    }


@app.get("/voices")
async def get_voices():
    """List available TTS voices and whether TTS is enabled."""
    return {
        "voices": [
            {"key": k, "name": v["name"], "emoji": v["emoji"]}
            for k, v in VOICES.items()
        ],
        "tts_enabled": bool(settings.elevenlabs_api_key),
    }


@app.post("/speak", response_model=SpeakResponse)
async def speak(request_body: SpeakRequest, request: Request):
    """Convert Shakespearean text to speech using ElevenLabs."""
    if not settings.elevenlabs_api_key:
        raise HTTPException(status_code=503, detail="TTS not configured")

    if request_body.voice not in VOICES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid voice. Choose: {', '.join(VOICES.keys())}"
        )

    text = request_body.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    if len(text) > 5000:
        raise HTTPException(status_code=400, detail="Text too long for TTS (max 5000 chars)")

    client_ip = request.client.host if request.client else "unknown"
    if not check_rate_limit(client_ip):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    try:
        audio_bytes = await tts_service.speak(text, request_body.voice)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"TTS service error: {str(e)}")

    return SpeakResponse(
        audio=base64.b64encode(audio_bytes).decode("utf-8"),
        voice=request_body.voice,
    )


if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "=" * 60)
    print("  SHAKESPEARE TRANSLATOR — Starting Server")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
