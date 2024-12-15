import asyncio
import aiohttp
from typing import List, Dict, Optional
from base_crawler import BaseCrawler
from ..utils.rate_limiter import AsyncRateLimiter

class AsyncCrawler(BaseCrawler):
    """Asynchronous web crawler implementation using aiohttp."""
    
    def __init__(self, *args, **kwargs):
        """
        Initialize AsyncCrawler with rate limiting.
        
        :param args: Positional arguments
        :param kwargs: Keyword arguments
        """
        super().__init__(*args, **kwargs)
        self.rate_limiter = AsyncRateLimiter(max_rate=10)  # 10 requests per second
    
    async def fetch_url(self, url: str) -> Optional[str]:
        """
        Asynchronously fetch URL content with rate limiting.
        
        :param url: URL to fetch
        :return: Fetched content or None
        """
        async with self.rate_limiter:
            async with aiohttp.ClientSession() as session:
                for attempt in range(self.max_retries):
                    try:
                        async with session.get(url, timeout=aiohttp.ClientTimeout(total=self.timeout)) as response:
                            response.raise_for_status()
                            return await response.text()
                    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                        self._log_error(url, e)
                        if attempt == self.max_retries - 1:
                            return None
        return None
    
    async def crawl(self) -> List[Dict]:
        """
        Crawl URLs asynchronously with concurrency control.
        
        :return: List of crawled data
        """
        async def fetch_with_metadata(url):
            content = await self.fetch_url(url)
            return {
                'url': url,
                'content': content
            } if content else None
        
        # Use asyncio.gather for concurrent fetching
        tasks = [fetch_with_metadata(url) for url in self.urls]
        results = await asyncio.gather(*tasks)
        
        # Filter out None results
        return [result for result in results if result]