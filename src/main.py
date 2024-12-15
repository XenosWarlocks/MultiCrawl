import asyncio
import logging
from typing import List, Dict, Optional

from src.crawler.sequential_crawler import SequentialCrawler
from src.crawler.threaded_crawler import ThreadedCrawler
from src.crawler.async_crawler import AsyncCrawler
from src.data_processing.parser import DataParser
from src.data_processing.aggregator import DataAggregator
from src.data_processing.report_generator import ReportGenerator

class WebCrawlerApp:
    """
    Advanced web crawler application with enhanced parsing and analysis capabilities.
    Supports multiple crawling strategies and in-depth data extraction.
    """
    
    def __init__(self, 
                 urls: List[str], 
                 mode: str = 'async', 
                 language_filter: Optional[str] = None,
                 top_keywords: int = 10):
        """
        Initialize the web crawler application with advanced configuration.
        
        :param urls: List of URLs to crawl
        :param mode: Crawling mode (sequential, threaded, async)
        :param language_filter: Optional language code to filter results
        :param top_keywords: Number of top keywords to extract
        """
        self.urls = urls
        self.mode = mode
        self.language_filter = language_filter
        self.top_keywords = top_keywords
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize crawler based on mode
        self.crawler_map = {
            'sequential': SequentialCrawler,
            'threaded': ThreadedCrawler,
            'async': AsyncCrawler
        }
    
    async def run(self) -> Dict:
        """
        Run the web crawler with advanced parsing and analysis.
        
        :return: Comprehensive crawling results
        """
        # Select crawler based on mode
        crawler_class = self.crawler_map.get(self.mode, AsyncCrawler)
        crawler = crawler_class(self.urls)
        
        # Crawl websites
        self.logger.info(f"Starting crawler in {self.mode} mode")
        crawled_data = await crawler.crawl()
        
        # Initialize parser
        parser = DataParser()
        
        # Parse crawled data
        parsed_data = parser.parse_batch(crawled_data)
        
        # Advanced analysis
        enriched_data = self._enrich_parsed_data(parser, parsed_data)
        
        # Aggregate data
        aggregator = DataAggregator()
        aggregated_results = aggregator.aggregate(enriched_data)
        
        # Generate report
        report_generator = ReportGenerator()
        report = report_generator.generate_report(aggregated_results)
        
        return {
            'raw_data': crawled_data,
            'parsed_data': parsed_data,
            'enriched_data': enriched_data,
            'aggregated_results': aggregated_results,
            'report': report
        }
    
    def _enrich_parsed_data(self, parser: DataParser, parsed_data: List[Dict]) -> List[Dict]:
        """
        Enrich parsed data with additional analysis.
        
        :param parser: DataParser instance
        :param parsed_data: List of parsed data entries
        :return: Enriched parsed data
        """
        enriched_results = []
        
        for entry in parsed_data:
            # Skip error entries
            if entry.get('type') == 'error':
                enriched_results.append(entry)
                continue
            
            # Detect language
            entry['language'] = parser.detect_language(entry)
            
            # Filter by language if specified
            if (self.language_filter and 
                entry.get('language') != self.language_filter):
                continue
            
            # Extract entities
            entry['entities'] = parser.extract_entities(entry)
            
            # Extract keywords
            entry['keywords'] = parser.extract_keywords(entry, top_n=self.top_keywords)
            
            enriched_results.append(entry)
        
        return enriched_results

async def main():
    """Main entry point for the advanced web crawler application."""
    logging.basicConfig(level=logging.INFO)
    
    urls = [
        'https://example.com/jobs',
        'https://another-jobs-site.com/listings',
        'https://tech-news-site.com/articles'
    ]
    
    # Example configurations
    app = WebCrawlerApp(
        urls, 
        mode='async',           # Use async crawler
        language_filter='en',   # Only keep English content
        top_keywords=15         # Extract top 15 keywords
    )
    
    try:
        results = await app.run()
        
        # Print summary of results
        print("Crawling Completed:")
        print(f"Total URLs Crawled: {len(results['raw_data'])}")
        print(f"Parsed Entries: {len(results['parsed_data'])}")
        print(f"Enriched Entries: {len(results['enriched_data'])}")
        
        # Print the report
        print("\nReport Summary:")
        print(results['report'])
        
    except Exception as e:
        logging.error(f"Crawling failed: {e}")

if __name__ == '__main__':
    asyncio.run(main())