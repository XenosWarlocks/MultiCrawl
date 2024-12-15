import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from typing import Dict, Any
import json
import os

class ReportGenerator:
    """
    Generate comprehensive reports from aggregated data.
    Supports multiple output formats and visualizations.
    """
    
    def __init__(self, output_dir: str = 'reports'):
        """
        Initialize report generator.
        
        :param output_dir: Directory to save generated reports
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_report(self, aggregated_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate comprehensive report with multiple formats and visualizations.
        
        :param aggregated_data: Aggregated data dictionary
        :return: Paths to generated report files
        """
        report_files = {}
        
        # Generate text report
        report_files['text'] = self._generate_text_report(aggregated_data)
        
        # Generate JSON report
        report_files['json'] = self._generate_json_report(aggregated_data)
        
        # Generate visualizations
        report_files.update(self._generate_visualizations(aggregated_data))
        
        return report_files
    
    def _generate_text_report(self, data: Dict[str, Any]) -> str:
        """
        Create a human-readable text report.
        
        :param data: Aggregated data
        :return: Path to text report
        """
        report_path = os.path.join(self.output_dir, 'data_summary_report.txt')
        
        with open(report_path, 'w') as f:
            f.write("Web Crawler Data Aggregation Report\n")
            f.write("===================================\n\n")
            
            # Cross-source summary
            cross_source = data.get('cross_source', {})
            f.write("Cross-Source Summary:\n")
            f.write(f"Total Entries: {cross_source.get('total_entries', 0)}\n")
            f.write(f"Unique Sources: {cross_source.get('unique_sources', 0)}\n")
            f.write("Source Type Distribution:\n")
            
            for source_type, count in cross_source.get('source_type_distribution', {}).items():
                f.write(f"  - {source_type}: {count}\n")
        
        return report_path
    
    def _generate_json_report(self, data: Dict[str, Any]) -> str:
        """
        Create a detailed JSON report.
        
        :param data: Aggregated data
        :return: Path to JSON report
        """
        report_path = os.path.join(self.output_dir, 'data_aggregation_report.json')
        
        with open(report_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        return report_path
    
    def _generate_visualizations(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Create data visualization plots.
        
        :param data: Aggregated data
        :return: Dictionary of visualization file paths
        """
        visualizations = {}
        
        # Source Type Distribution Pie Chart
        cross_source = data.get('cross_source', {})
        source_types = cross_source.get('source_type_distribution', {})
        
        plt.figure(figsize=(8, 6))
        plt.pie(
            source_types.values(), 
            labels=source_types.keys(), 
            autopct='%1.1f%%'
        )
        plt.title('Source Type Distribution')
        pie_path = os.path.join(self.output_dir, 'source_type_distribution.png')
        plt.savefig(pie_path)
        plt.close()
        
        visualizations['pie_chart'] = pie_path
        
        return visualizations