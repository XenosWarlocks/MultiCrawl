import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from dataclasses import dataclass

class BaseCrawler(ABC):
    """
    Abstract base class for web crawlers with a common interface
    for different concurrency strategies.
    """
    def __init__(self, urls: List[str], max_workers: int = 5):
        """
        Initialize the crawler with target URLs and concurrency settings.
        
        :param urls: List of URLs to crawl
        :param max_workers: Maximum number of concurrent workers
        """
        self.urls = urls
        self.max_workers = max_workers
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    @abstractmethod
    async def fetch_url(self, url: str) -> Dict[str, Any]:
        """
        Abstract method to fetch data from a single URL.
        Must be implemented by specific crawler types.
        
        :param url: URL to fetch
        :return: Dictionary containing crawled data
        """
        pass
    
    @abstractmethod
    async def crawl(self) -> List[Dict[str, Any]]:
        """
        Abstract method to perform the actual crawling.
        Must implement the specific concurrency strategy.
        
        :return: List of crawled data from all URLs
        """
        pass
    
    def validate_url(self, url: str) -> bool:
        """
        Basic URL validation method.
        
        :param url: URL to validate
        :return: Boolean indicating URL validity
        """
        import re
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        return bool(url_pattern.match(url))
    
    def rate_limit(self, delay: float = 1.0):
        """
        Simple rate limiting method to prevent overwhelming target servers.
        
        :param delay: Delay between requests in seconds
        """
        import time
        time.sleep(delay)