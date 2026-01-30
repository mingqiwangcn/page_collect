import asyncio
import logging
from pagecollect.context import WorkerContext

logger = logging.getLogger(__name__)

# Global rate limit: at least 0.3 seconds between two requests (~3 req/s)
rate = 0.3
lock = asyncio.Lock()
last_req_time = 0.0

class TemporaryFetchError(Exception):
    """
    Marks a *temporary* failure:
    - e.g., HTTP 5xx
    - Safe to retry
    """
    ...

async def rate_limit():
    """
    Global async rate limiter:
    - Called before every fetch
    - Uses a lock so only one coroutine updates last_req_time at a time
    - Sleeps if the previous request was too recent
    """
    global last_req_time
    async with lock:
        now_req_time = asyncio.get_running_loop().time()
        wait = rate - (now_req_time - last_req_time)
        if wait > 0:
            await asyncio.sleep(wait)
        last_req_time = asyncio.get_running_loop().time()

async def fetch_page_impl(url: str, worker_context: WorkerContext, timeout=10) -> str | None:
    """
    Perform a single HTTP attempt:
    - No retry logic here
    - Classifies responses by status code
    """
    async with worker_context.session.get(url, timeout=timeout) as resp:
        if resp.status == 200:
            content_type = resp.headers.get("Content-Type", "").lower()
            if "text/html" not in content_type:
               logger.info(f"content_type {content_type} not supported: {url}")
               return None   
            return await resp.text()
        if 400 <= resp.status < 500:
            logger.info(f"Skip {url}: {resp.status}")
        
        if 500 <= resp.status < 600:
            raise TemporaryFetchError()

        return None

async def fetch_page(url: str, worker_context: WorkerContext, timeout=10, max_attempts: int = 3) -> str | None:
    """
    Fetch a page with:
    - robots.txt enforcement
    - global rate limiting
    - automatic retries for temporary failures
    """
    if worker_context.robots_policy:
        if not await worker_context.robots_policy.allowed(url):
            return None

    for attempt in range(1, max_attempts+1):
        await rate_limit()
        try:
            return await fetch_page_impl(url, worker_context, timeout=timeout)
        
        except (TemporaryFetchError, asyncio.TimeoutError) as e:
            if attempt >= max_attempts:
                logger.warning(f"Give up {url}: {e}")
                return None
            await asyncio.sleep(3)

        except Exception as e:
            logger.error(f"Fetch failed for {url}: {e}")
            return None