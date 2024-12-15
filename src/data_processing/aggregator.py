import pandas as pd
from typing import List, Dict, Any
from collections import Counter
import numpy as np

class DataAggregator:
    """
    Aggregation utility for processing and summarizing parsed data.
    Supports various aggregation strategies and statistical computations.
    """
    
    def aggregate(self, parsed_data: List[Dict]) -> Dict[str, Any]:
        """
        Aggregate parsed data from multiple sources.
        
        :param parsed_data: List of parsed data dictionaries
        :return: Aggregated results dictionary
        """
        # Categorize data by type
        categorized_data = self._categorize_data(parsed_data)
        
        # Compute aggregations for each type
        aggregations = {}
        for data_type, data_list in categorized_data.items():
            aggregations[data_type] = self._aggregate_by_type(data_type, data_list)
        
        # Cross-source aggregation
        cross_source_aggs = self._cross_source_aggregation(parsed_data)
        aggregations['cross_source'] = cross_source_aggs
        
        return aggregations
    
    def _categorize_data(self, parsed_data: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Categorize parsed data by their type.
        
        :param parsed_data: List of parsed data
        :return: Categorized data dictionary
        """
        categorized = {}
        for entry in parsed_data:
            data_type = entry.get('type', 'unknown')
            if data_type not in categorized:
                categorized[data_type] = []
            categorized[data_type].append(entry)
        return categorized
    
    def _aggregate_by_type(self, data_type: str, data_list: List[Dict]) -> Dict[str, Any]:
        """
        Perform type-specific aggregation.
        
        :param data_type: Type of data (html, json, etc.)
        :param data_list: List of data entries
        :return: Aggregation results
        """
        if data_type == 'html':
            return self._aggregate_html(data_list)
        elif data_type == 'json':
            return self._aggregate_json(data_list)
        else:
            return {
                'total_entries': len(data_list),
                'error': f'No specific aggregation for type: {data_type}'
            }
    
    def _aggregate_html(self, data_list: List[Dict]) -> Dict[str, Any]:
        """
        Aggregate HTML-based data.
        
        :param data_list: List of HTML parsed data
        :return: HTML aggregation results
        """
        # Aggregate titles
        all_titles = [title for entry in data_list for title in entry.get('titles', [])]
        title_counts = Counter(all_titles)
        
        return {
            'total_sources': len(data_list),
            'title_frequency': dict(title_counts),
            'most_common_title': title_counts.most_common(1)[0] if title_counts else None,
            'unique_title_count': len(set(all_titles))
        }
    
    def _aggregate_json(self, data_list: List[Dict]) -> Dict[str, Any]:
        """
        Aggregate JSON-based data.
        
        :param data_list: List of JSON parsed data
        :return: JSON aggregation results
        """
        # Collect raw data and metadata
        raw_data = [entry.get('raw_data', {}) for entry in data_list]
        
        return {
            'total_sources': len(data_list),
            'data_keys': list(set(key for data in raw_data for key in data.keys())),
            'total_entries': sum(len(data) if isinstance(data, (list, dict)) else 1 for data in raw_data)
        }
    
    def _cross_source_aggregation(self, parsed_data: List[Dict]) -> Dict[str, Any]:
        """
        Perform aggregations across all data sources.
        
        :param parsed_data: List of all parsed data
        :return: Cross-source aggregation results
        """
        source_types = [entry.get('type', 'unknown') for entry in parsed_data]
        source_type_counts = Counter(source_types)
        
        return {
            'total_entries': len(parsed_data),
            'source_type_distribution': dict(source_type_counts),
            'unique_sources': len(set(entry.get('source_url', '') for entry in parsed_data))
        }