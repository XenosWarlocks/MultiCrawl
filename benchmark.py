import asyncio
import time
from typing import List, Dict
import matplotlib.pyplot as plt
import numpy as np

from src.crawler.sequential_crawler import SequentialCrawler
from src.crawler.threaded_crawler import ThreadedCrawler
from src.crawler.async_crawler import AsyncCrawler

class CrawlerBenchmark:
    """Benchmark different crawling strategies."""
    
    @staticmethod
    async def benchmark_crawler(
        crawler_class: type, 
        urls: List[str], 
        name: str,
        num_runs: int = 5
    ) -> Dict:
        """
        Benchmark a specific crawler implementation with multiple runs.
        
        :param crawler_class: Crawler class to benchmark
        :param urls: URLs to crawl
        :param name: Name of the crawler strategy
        :param num_runs: Number of benchmark runs
        :return: Benchmark results dictionary
        """
        execution_times = []
        
        for run in range(num_runs):
            start_time = time.time()
            
            crawler = crawler_class(urls)
            await crawler.crawl()
            
            end_time = time.time()
            execution_time = end_time - start_time
            execution_times.append(execution_time)
            
            print(f"{name} Crawler Run {run + 1}: {execution_time:.4f} seconds")
        
        results = {
            'name': name,
            'mean_time': np.mean(execution_times),
            'std_dev': np.std(execution_times),
            'min_time': np.min(execution_times),
            'max_time': np.max(execution_times)
        }
        return results
    
    @classmethod
    async def run_benchmarks(cls, urls: List[str], num_runs: int = 5):
        """
        Run benchmarks for different crawler strategies and visualize results.
        
        :param urls: URLs to crawl
        :param num_runs: Number of benchmark runs
        :return: List of benchmark results
        """
        crawlers = [
            (SequentialCrawler, "Sequential"),
            (ThreadedCrawler, "Threaded"),
            (AsyncCrawler, "Async")
        ]
        
        benchmark_results = []
        for crawler_class, crawler_name in crawlers:
            result = await cls.benchmark_crawler(
                crawler_class, 
                urls, 
                crawler_name, 
                num_runs
            )
            benchmark_results.append(result)
        
        # Visualize benchmark results
        cls.plot_benchmark_results(benchmark_results)
        
        return benchmark_results
    
    @staticmethod
    def plot_benchmark_results(results: List[Dict]):
        """
        Create a bar plot to visualize benchmark results.
        
        :param results: List of benchmark result dictionaries
        """
        plt.figure(figsize=(10, 6))
        
        names = [result['name'] for result in results]
        mean_times = [result['mean_time'] for result in results]
        std_devs = [result['std_dev'] for result in results]
        
        plt.bar(names, mean_times, yerr=std_devs, capsize=10)
        plt.title('Web Crawler Performance Comparison')
        plt.xlabel('Crawler Strategy')
        plt.ylabel('Execution Time (seconds)')
        plt.tight_layout()
        plt.savefig('crawler_benchmark.png')
        plt.close()

async def main():
    """Main benchmark entry point."""
    urls = [
        'https://example.com/jobs',
        'https://another-jobs-site.com/listings',
        'https://job-portal.com/openings'
    ]
    
    results = await CrawlerBenchmark.run_benchmarks(urls)
    
    # Print detailed results
    for result in results:
        print(f"\n{result['name']} Crawler Results:")
        print(f"Mean Execution Time: {result['mean_time']:.4f} seconds")
        print(f"Standard Deviation: {result['std_dev']:.4f} seconds")
        print(f"Min Execution Time: {result['min_time']:.4f} seconds")
        print(f"Max Execution Time: {result['max_time']:.4f} seconds")

if __name__ == '__main__':
    asyncio.run(main())