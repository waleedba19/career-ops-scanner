"""Base fetcher with retry, rate-limit, circuit-breaker, and typed result."""
import asyncio
import time
import random
from dataclasses import dataclass, field
from typing import Any, Callable
import aiohttp

@dataclass
class FetchResult:
    jobs: list[dict] = field(default_factory=list)
    source: str = ""
    latency_ms: float = 0
    error: str = ""
    http_status: int = 0

# Simple in-memory circuit breaker
_circuit: dict[str,float] = {}
FAIL_THRESHOLD = 5
COOLDOWN_SEC = 600

def circuit_open(source: str) -> bool:
    until = _circuit.get(source, 0)
    return time.time() < until

def record_failure(source: str):
    _circuit[source] = time.time() + COOLDOWN_SEC

def with_retry(max_attempts=3, base_delay=0.6):
    def deco(fn: Callable):
        async def wrapper(session, *a, **kw):
            last_err = ""
            for attempt in range(max_attempts):
                try:
                    return await fn(session, *a, **kw)
                except Exception as e:
                    last_err = str(e)
                    if attempt < max_attempts-1:
                        await asyncio.sleep(base_delay * (2**attempt) + random.random()*0.3)
                    else:
                        raise
            raise RuntimeError(last_err)
        return wrapper
    return deco

def rate_limited(calls_per_sec=4):
    """Token bucket-ish: sleep if needed. Simple per-fetcher sleep."""
    interval = 1.0 / calls_per_sec
    last: dict[str,float] = {}
    def deco(fn):
        async def wrapper(session, *a, **kw):
            src = fn.__name__
            now = time.time()
            prev = last.get(src, 0)
            wait = interval - (now - prev)
            if wait > 0:
                await asyncio.sleep(wait)
            last[src] = time.time()
            return await fn(session, *a, **kw)
        return wrapper
    return deco

class BaseFetcher:
    name: str = "base"
    tier: int = 3
    timeout: int = 12
    def __init__(self, name: str, tier: int = 3):
        self.name = name
        self.tier = tier
    async def fetch(self, session: aiohttp.ClientSession) -> FetchResult:
        raise NotImplementedError
