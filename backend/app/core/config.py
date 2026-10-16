import os
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_CORS_ORIGINS = [
    "https://codelens-flax.vercel.app",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


def get_cors_origins() -> list[str]:
    configured_origins = [
        origin.strip().rstrip("/")
        for origin in os.getenv("CODELENS_CORS_ORIGINS", "").split(",")
        if origin.strip()
    ]
    return list(dict.fromkeys(DEFAULT_CORS_ORIGINS + configured_origins))


def get_port() -> int:
    return int(os.getenv("PORT", "8000"))
