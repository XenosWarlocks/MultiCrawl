import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from base_crawler import BaseCrawler

class SequentialCrawler(BaseCrawler):
    """
    Sequential web crawler that fetches URLs one at a time.
    Demonstrates the baseline performance before introducing concurrency.
    """
    
    def fetch_url(self, url: str) -> Dict[str, Any]:
        """
        Fetch data from a single URL sequentially.
        
        :param url: URL to fetch
        :return: Dictionary with crawled data
        """
        if not self.validate_url(url):
            self.logger.warning(f"Invalid URL: {url}")
            return {}
        
        try:
            # Simulate rate limiting
            self.rate_limit()
            
            # Send GET request
            response = requests.get(url, timeout=self.max_workers)
            response.raise_for_status()
            
            # Parse HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract basic metadata (example for job postings)
            job_postings = soup.find_all('div', class_='job-posting')
            
            return {
                'url': url,
                'status_code': response.status_code,
                'job_count': len(job_postings),
                'titles': [job.find('h2').text for job in job_postings]
            }
        
        except requests.RequestException as e:
            self.logger.error(f"Error fetching {url}: {e}")
            return {'url': url, 'error': str(e)}
    
    def crawl(self) -> List[Dict[str, Any]]:
        """
        Crawl URLs sequentially.
        
        :return: List of crawled data from all URLs
        """
        results = []
        for url in self.urls:
            result = self.fetch_url(url)
            results.append(result)
        
        return results


