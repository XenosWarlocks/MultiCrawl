import pytest
import json
from src.data_processing.parser import DataParser

class TestDataParser:
    @pytest.fixture
    def parser(self):
        return DataParser()

    def test_parse_json_valid(self, parser):
        """Test parsing valid JSON content."""
        json_content = json.dumps({"key": "value", "numbers": [1, 2, 3]})
        entry = {"url": "https://example.com", "content": json_content}
        
        result = parser.parse_single(entry)
        
        assert result['type'] == 'json'
        assert result['source_url'] == 'https://example.com'
        assert 'content_hash' in result
        assert result['raw_data'] == {"key": "value", "numbers": [1, 2, 3]}

    def test_parse_html_extraction(self, parser):
        """Test HTML parsing with comprehensive content extraction."""
        html_content = """
        <html>
            <body>
                <h1>Test Page</h1>
                <h2>Subtitle</h2>
                <p>This is a paragraph with some text.</p>
                <a href="/link1">Link 1</a>
                <a href="https://external.com">External Link</a>
                <img src="image.jpg" alt="Test Image">
            </body>
        </html>
        """
        entry = {"url": "https://example.com", "content": html_content}
        
        result = parser.parse_single(entry)
        
        assert result['type'] == 'html'
        assert len(result['metadata']['titles']) == 2
        assert len(result['metadata']['links']) == 2
        assert len(result['metadata']['images']) == 1
        assert result['parsed_domain'] == 'example.com'

    def test_parse_text_content(self, parser):
        """Test text content parsing with word analysis."""
        text_content = "This is a sample text for parsing. It contains multiple words."
        entry = {"url": "https://example.com", "content": text_content}
        
        result = parser.parse_single(entry)
        
        assert result['type'] == 'text'
        assert result['metadata']['word_count'] > 0
        assert result['metadata']['unique_word_count'] > 0
        assert 'text_sample' in result

    def test_keyword_extraction(self, parser):
        """Test keyword extraction from different content types."""
        html_content = "<html><body><p>Python is an amazing programming language for web development and data science.</p></body></html>"
        entry = {"url": "https://example.com", "content": html_content}
        
        parsed_result = parser.parse_single(entry)
        keywords = parser.extract_keywords(parsed_result)
        
        assert isinstance(keywords, list)
        assert len(keywords) > 0
        assert all(len(keyword) > 2 for keyword in keywords)

    def test_language_detection(self, parser):
        """Test language detection for different content types."""
        html_content_en = "<html><body><p>Hello, this is an English text about programming.</p></body></html>"
        html_content_fr = "<html><body><p>Bonjour, ceci est un texte en français sur la programmation.</p></body></html>"
        
        entry_en = {"url": "https://example.com/en", "content": html_content_en}
        entry_fr = {"url": "https://example.com/fr", "content": html_content_fr}
        
        parsed_result_en = parser.parse_single(entry_en)
        parsed_result_fr = parser.parse_single(entry_fr)
        
        lang_en = parser.detect_language(parsed_result_en)
        lang_fr = parser.detect_language(parsed_result_fr)
        
        assert lang_en in ['en']
        assert lang_fr in ['fr']

    def test_parse_batch_with_mixed_content(self, parser):
        """Test parsing a batch of entries with mixed content types."""
        entries = [
            {"url": "https://example1.com", "content": '{"key": "json"}'},
            {"url": "https://example2.com", "content": "<html><body>HTML content</body></html>"},
            {"url": "https://example3.com", "content": "Plain text content"}
        ]
        
        results = parser.parse_batch(entries)
        
        assert len(results) == 3
        assert set(result['type'] for result in results) == {'json', 'html', 'text'}