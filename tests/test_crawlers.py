import pytest
import asyncio
from src.crawler.sequential_crawler import SequentialCrawler
from src.crawler.threaded_crawler import ThreadedCrawler
from src.crawler.async_crawler import AsyncCrawler

@pytest.mark.asyncio
class TestCrawlers:
    """
    Test suite for different crawler implementations.
    Validates crawling behavior, error handling, and basic functionality.
    """
    
    @pytest.fixture
    def test_urls(self):
        """
        Provide test URLs for crawler testing.
        
        :return: List of test URLs
        """
        return [
            'https://example.com',
            'https://python.org',
            'https://github.com'
        ]
    
    @pytest.mark.parametrize("crawler_class", [
        SequentialCrawler,
        ThreadedCrawler,
        AsyncCrawler
    ])
    async def test_crawler_basic_functionality(self, test_urls, crawler_class):
        """
        Test basic crawling functionality for each crawler type.
        
        :param test_urls: List of URLs to crawl
        :param crawler_class: Crawler class to test
        """
        crawler = crawler_class(test_urls)
        results = await crawler.crawl()
        
        assert len(results) > 0, f"{crawler_class.__name__} failed to crawl any URLs"
        
        for result in results:
            assert 'url' in result, "Crawler result missing URL"
            assert 'content' in result, "Crawler result missing content"
            assert result['content'], "Crawler returned empty content"
    
    @pytest.mark.parametrize("crawler_class", [
        SequentialCrawler,
        ThreadedCrawler,
        AsyncCrawler
    ])
    async def test_crawler_invalid_urls(self, crawler_class):
        """
        Test crawler behavior with invalid URLs.
        
        :param crawler_class: Crawler class to test
        """
        invalid_urls = [
            'https://thissitedoesnotexist123456.com',
            'invalid_url'
        ]
        
        crawler = crawler_class(invalid_urls)
        results = await crawler.crawl()
        
        assert len(results) == 0, f"{crawler_class.__name__} should return empty results for invalid URLs"
    
    @pytest.mark.parametrize("crawler_class", [
        SequentialCrawler,
        ThreadedCrawler,
        AsyncCrawler
    ])
    async def test_crawler_retry_mechanism(self, crawler_class):
        """
        Verify crawler retry mechanism for temporary failures.
        
        :param crawler_class: Crawler class to test
        """
        # Note: In a real-world scenario, you'd mock network requests
        # This is a simplified test
        crawler = crawler_class(['https://example.com'], max_retries=3)
        results = await crawler.crawl()
        
        assert len(results) > 0, f"{crawler_class.__name__} failed to crawl with retry mechanism"
    
    async def test_concurrent_crawling(self, test_urls):
        """
        Compare performance of different crawler implementations.
        
        :param test_urls: List of test URLs
        """
        crawlers = [
            SequentialCrawler(test_urls),
            ThreadedCrawler(test_urls),
            AsyncCrawler(test_urls)
        ]
        
        results = await asyncio.gather(
            *[crawler.crawl() for crawler in crawlers]
        )
        
        for crawler_results in results:
            assert len(crawler_results) > 0, "Crawler failed to retrieve results"