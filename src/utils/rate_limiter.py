import asyncio
from typing import Optional

class AsyncRateLimiter:
    """Async rate limiter to control request frequency."""
    
    def __init__(self, max_rate: float = 10, max_concurrent: Optional[int] = None):
        """
        Initialize rate limiter.
        
        :param max_rate: Maximum requests per second
        :param max_concurrent: Maximum concurrent requests
        """
        self.max_rate = max_rate
        self.max_concurrent = max_concurrent
        self._semaphore = asyncio.Semaphore(max_concurrent) if max_concurrent else None
        self._last_call = 0
    
    async def __aenter__(self):
        """
        Async context manager entry point.
        Controls request rate and concurrent requests.
        """
        if self._semaphore:
            await self._semaphore.acquire()
        
        current_time = asyncio.get_event_loop().time()
        min_interval = 1.0 / self.max_rate
        time_since_last_call = current_time - self._last_call
        
        if time_since_last_call < min_interval:
            await asyncio.sleep(min_interval - time_since_last_call)
        
        self._last_call = asyncio.get_event_loop().time()
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Async context manager exit point.
        Releases semaphore if used.
        """
        if self._semaphore:
            self._semaphore.release()