import concurrent.futures
import requests
from typing import List, Dict, Optional
from base_crawler import BaseCrawler

class ThreadedCrawler(BaseCrawler):
    """Multithreaded web crawler implementation."""
    
    def _fetch_url_thread(self, url: str) -> Optional[Dict]:
        """
        Fetch URL content in a separate thread.
        
        :param url: URL to fetch
        :return: Crawled data or None
        """
        for attempt in range(self.max_retries):
            try:
                response = requests.get(url, timeout=self.timeout)
                response.raise_for_status()
                return {
                    'url': url,
                    'content': response.text
                }
            except requests.RequestException as e:
                self._log_error(url, e)
                if attempt == self.max_retries - 1:
                    return None
        return None
    
    async def crawl(self) -> List[Dict]:
        """
        Crawl URLs using multiple threads.
        
        :return: List of crawled data
        """
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Map urls to thread executor
            results = list(executor.map(self._fetch_url_thread, self.urls))
        
        # Filter out None results
        return [result for result in results if result]
    
    async def fetch_url(self, url: str) -> Optional[str]:
        """
        Fetch a single URL (used for compatibility with base class).
        
        :param url: URL to fetch
        :return: URL content
        """
        result = self._fetch_url_thread(url)
        return result['content'] if result else None