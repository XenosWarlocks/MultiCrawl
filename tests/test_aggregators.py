import pytest
import json
from typing import List, Dict
from src.data_processing.aggregator import DataAggregator

class TestDataAggregator:
    """
    Comprehensive test suite for the DataAggregator class.
    Covers various data types, aggregation scenarios, and edge cases.
    """
    
    @pytest.fixture
    def data_aggregator(self):
        """
        Fixture to create a fresh DataAggregator instance for each test.
        """
        return DataAggregator()
    
    def test_empty_input(self, data_aggregator):
        """
        Test aggregation with an empty input list.
        Ensures the method handles empty input gracefully.
        """
        result = data_aggregator.aggregate([])
        
        assert isinstance(result, dict), "Result should be a dictionary"
        assert 'cross_source' in result, "Cross-source aggregation should always be present"
        assert result['cross_source']['total_entries'] == 0, "Total entries should be 0"
        assert result['cross_source']['unique_sources'] == 0, "Unique sources should be 0"
    
    def test_html_aggregation(self, data_aggregator):
        """
        Test HTML data aggregation with multiple entries.
        Verifies title frequency, most common title, and other HTML-specific metrics.
        """
        html_data = [
            {
                'type': 'html',
                'titles': ['Tech News', 'Latest Updates', 'Tech News']
            },
            {
                'type': 'html',
                'titles': ['Tech News', 'Sports', 'Finance']
            }
        ]
        
        result = data_aggregator.aggregate(html_data)
        
        # Check HTML-specific aggregation results
        html_agg = result.get('html', {})
        assert html_agg['total_sources'] == 2, "Should correctly count HTML sources"
        assert html_agg['unique_title_count'] == 4, "Should count unique titles"
        assert html_agg['most_common_title'] == ('Tech News', 2), "Most common title should be correct"
        
        # Verify title frequency
        expected_title_freq = {
            'Tech News': 2,
            'Latest Updates': 1,
            'Sports': 1,
            'Finance': 1
        }
        assert html_agg['title_frequency'] == expected_title_freq, "Title frequency should match"
    
    def test_json_aggregation(self, data_aggregator):
        """
        Test JSON data aggregation with different JSON structures.
        Checks data keys, total entries, and aggregation capabilities.
        """
        json_data = [
            {
                'type': 'json',
                'raw_data': {
                    'users': [{'id': 1}, {'id': 2}],
                    'metadata': {'source': 'API'}
                }
            },
            {
                'type': 'json',
                'raw_data': {
                    'products': [{'name': 'A'}, {'name': 'B'}, {'name': 'C'}],
                    'version': '1.0'
                }
            }
        ]
        
        result = data_aggregator.aggregate(json_data)
        
        # Verify JSON-specific aggregation
        json_agg = result.get('json', {})
        assert json_agg['total_sources'] == 2, "Should correctly count JSON sources"
        assert json_agg['total_entries'] == 5, "Should correctly count total JSON entries"
        
        # Check data keys
        expected_keys = {'users', 'metadata', 'products', 'version'}
        assert set(json_agg['data_keys']) == expected_keys, "Should extract all unique keys"
    
    def test_mixed_data_sources(self, data_aggregator):
        """
        Test aggregation with multiple data types.
        Verifies cross-source aggregation and type distribution.
        """
        mixed_data = [
            {'type': 'html', 'source_url': 'https://example1.com'},
            {'type': 'json', 'source_url': 'https://example2.com'},
            {'type': 'html', 'source_url': 'https://example3.com'},
            {'type': 'text', 'source_url': 'https://example4.com'}
        ]
        
        result = data_aggregator.aggregate(mixed_data)
        
        # Verify cross-source aggregation
        cross_source = result.get('cross_source', {})
        assert cross_source['total_entries'] == 4, "Should count total entries"
        assert cross_source['unique_sources'] == 4, "Should count unique sources"
        
        # Check source type distribution
        expected_type_dist = {
            'html': 2,
            'json': 1,
            'text': 1
        }
        assert cross_source['source_type_distribution'] == expected_type_dist, "Source type distribution incorrect"
    
    def test_error_handling(self, data_aggregator):
        """
        Test handling of entries with missing or invalid data.
        Ensures robust error handling and default behavior.
        """
        error_data = [
            {'type': 'unknown'},  # Missing data
            {'type': 'error', 'error_message': 'Parsing failed'},  # Error entry
            {}  # Completely empty entry
        ]
        
        result = data_aggregator.aggregate(error_data)
        
        # Verify cross-source aggregation handles problematic entries
        cross_source = result.get('cross_source', {})
        assert cross_source['total_entries'] == 3, "Should count all entries"
        assert cross_source['source_type_distribution'].get('unknown', 0) == 1, "Unknown type should be counted"
    
    def test_large_dataset(self, data_aggregator):
        """
        Performance and stress test with a large number of entries.
        Validates aggregation efficiency and correctness.
        """
        # Generate a large dataset with 1000 mixed entries
        large_data = []
        for i in range(500):
            large_data.append({
                'type': 'html',
                'titles': [f'Title {i % 10}']
            })
        for i in range(500):
            large_data.append({
                'type': 'json',
                'raw_data': {'key': f'value_{i}'}
            })
        
        result = data_aggregator.aggregate(large_data)
        
        # Verify large dataset aggregation
        assert result['cross_source']['total_entries'] == 1000, "Should handle large datasets"
        
        # Check HTML aggregation in large dataset
        html_agg = result.get('html', {})
        assert html_agg['total_sources'] == 500, "Should correctly count HTML sources"
        assert html_agg['unique_title_count'] == 10, "Should have 10 unique titles"
        
        # Check JSON aggregation in large dataset
        json_agg = result.get('json', {})
        assert json_agg['total_sources'] == 500, "Should correctly count JSON sources"
        assert json_agg['total_entries'] == 500, "Should count JSON entries"
    
    def test_edge_cases(self, data_aggregator):
        """
        Test various edge cases to ensure robust handling.
        Covers scenarios like nested data, empty collections, etc.
        """
        edge_case_data = [
            # Nested JSON data
            {
                'type': 'json',
                'raw_data': {
                    'nested': {
                        'deep': {
                            'value': 'test'
                        }
                    }
                }
            },
            # Empty collections
            {
                'type': 'json',
                'raw_data': []
            },
            {
                'type': 'html',
                'titles': []
            }
        ]
        
        result = data_aggregator.aggregate(edge_case_data)
        
        # Verify handling of edge cases
        assert result['cross_source']['total_entries'] == 3, "Should count all entries"
        assert result.get('json', {}).get('total_entries') == 1, "Should handle nested and empty JSON"
    
    def test_type_specific_aggregation(self, data_aggregator):
        """
        Detailed test of type-specific aggregation methods.
        Ensures each data type is processed correctly.
        """
        test_data = [
            {
                'type': 'json',
                'raw_data': {'key1': 'value1', 'key2': 'value2'}
            },
            {
                'type': 'html',
                'titles': ['Test Title', 'Another Title']
            },
            {
                'type': 'text',
                'content': 'Sample text content'
            }
        ]
        
        result = data_aggregator.aggregate(test_data)
        
        # Verify presence of type-specific and cross-source aggregations
        assert 'json' in result, "JSON aggregation should be present"
        assert 'html' in result, "HTML aggregation should be present"
        assert 'cross_source' in result, "Cross-source aggregation should always be present"
        
        # Verify cross-source metrics
        cross_source = result['cross_source']
        assert cross_source['total_entries'] == 3, "Should count total entries"
        assert cross_source['source_type_distribution'] == {'json': 1, 'html': 1, 'text': 1}, "Type distribution should be correct"

# Optional: Add configuration for more detailed test output
def pytest_configure(config):
    """
    Pytest configuration to improve test output readability.
    """
    config.addinivalue_line(
        "markers", 
        "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )