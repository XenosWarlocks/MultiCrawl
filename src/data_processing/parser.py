import datetime
import re
import json
from typing import List, Dict, Any
from bs4 import BeautifulSoup
import hashlib
import urllib.parse

import chardet

class DataParser:
    """
    Comprehensive parsing utility for extracting structured data from web content.
    Supports HTML, JSON, and text parsing with flexible extraction methods.
    """

    def parse_batch(self, crawled_data: List[Dict]) -> List[Dict]:
        """
        Parse multiple crawled data entries with improved error handling.
        
        :param crawled_data: List of crawled data dictionaries
        :return: List of parsed data
        """
        parsed_results = []
        for entry in crawled_data:
            try:
                parsed_entry = self.parse_single(entry)
                parsed_results.append(parsed_entry)
            except Exception as e:
                # Log parsing errors without stopping entire batch
                parsed_results.append({
                    'source_url': entry.get('url', 'unknown'),
                    'type': 'error',
                    'error_message': str(e)
                })
        return parsed_results

    def parse_single(self, entry: Dict) -> Dict:
        """
        Parse a single crawled data entry with enhanced type detection.
        
        :param entry: Crawled data dictionary
        :return: Parsed data dictionary
        """
        url = entry.get('url', '')
        content = entry.get('content', '')

        # Detect content encoding
        detected_encoding = self._detect_encoding(content)
        
        # Normalize content to unicode
        try:
            content = content.encode(detected_encoding).decode('utf-8')
        except Exception:
            content = content  # Fallback to original content

        # Trim extremely large content
        if len(content) > 1_000_000:  # 1MB limit
            content = content[:1_000_000]

        # Advanced content type detection
        if self._is_json(content):
            return self._parse_json(url, content)
        elif self._is_html(content):
            return self._parse_html(url, content)
        elif self._is_xml(content):
            return self._parse_xml(url, content)
        else:
            return self._parse_text(url, content)
    
    def _detect_encoding(self, content: str) -> str:
        """
        Detect content encoding using chardet.
        
        :param content: Raw content
        :return: Detected encoding
        """
        try:
            result = chardet.detect(content.encode())
            return result['encoding'] or 'utf-8'
        except Exception:
            return 'utf-8'
    
    def _is_xml(self, content: str) -> bool:
        """
        Check if content is XML.
        
        :param content: Content to check
        :return: True if content is XML
        """
        return bool(re.search(r'<\?xml.*\?>', content))

    def _parse_xml(self, url: str, content: str) -> Dict:
        """
        Parse XML content with basic structure extraction.
        
        :param url: Source URL
        :param content: XML content
        :return: Parsed XML data
        """
        try:
            from xml.etree import ElementTree
            root = ElementTree.fromstring(content)
            
            return {
                'source_url': url,
                'type': 'xml',
                'root_tag': root.tag,
                'child_tags': [child.tag for child in root],
                'attribute_keys': list(root.attrib.keys()),
                'content_hash': hashlib.md5(content.encode('utf-8')).hexdigest(),
                'parsed_at': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'source_url': url,
                'type': 'xml',
                'error': f'XML parsing failed: {str(e)}'
            }
        
    def sanitize_text(self, text: str) -> str:
        """
        Sanitize text by removing control characters and excessive whitespace.
        
        :param text: Input text
        :return: Sanitized text
        """
        # Remove control characters
        text = re.sub(r'[\x00-\x1F\x7F]', '', text)
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def extract_entities(self, parsed_data: Dict) -> Dict[str, List[str]]:
        """
        Extract potential named entities from parsed text.
        
        :param parsed_data: Parsed data dictionary
        :return: Dictionary of extracted entities
        """
        try:
            import spacy
            nlp = spacy.load('en_core_web_sm')
        except ImportError:
            return {}

        # Extract text based on content type
        if parsed_data['type'] in ['html', 'text']:
            text = ' '.join(parsed_data.get('text_content', {}).get('paragraphs', []))
        elif parsed_data['type'] == 'json':
            text = json.dumps(parsed_data.get('raw_data', ''))
        else:
            return {}

        doc = nlp(text)
        
        return {
            'organizations': list(set(ent.text for ent in doc.ents if ent.label_ == 'ORG')),
            'persons': list(set(ent.text for ent in doc.ents if ent.label_ == 'PERSON')),
            'locations': list(set(ent.text for ent in doc.ents if ent.label_ == 'GPE'))
        }

    def _is_json(self, content: str) -> bool:
        """
        Check if content is JSON.
        
        :param content: Content to check
        :return: True if content is JSON, False otherwise
        """
        try:
            json.loads(content)
            return True
        except (json.JSONDecodeError, TypeError):
            return False

    def _is_html(self, content: str) -> bool:
        """
        Check if content is HTML.
        
        :param content: Content to check
        :return: True if content appears to be HTML
        """
        return bool(re.search(r'<\w+.*?>', content))

    def _parse_json(self, url: str, content: str) -> Dict:
        """
        Parse JSON content with advanced metadata extraction.
        
        :param url: Source URL
        :param content: JSON content
        :return: Parsed JSON data
        """
        try:
            data = json.loads(content)
            
            # Compute content hash for deduplication
            content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
            
            return {
                'source_url': url,
                'type': 'json',
                'content_hash': content_hash,
                'raw_data': data,
                'metadata': {
                    'keys': list(data.keys()) if isinstance(data, dict) else [],
                    'length': len(data) if isinstance(data, (list, dict)) else 1,
                    'data_type': type(data).__name__
                },
                'parsed_at': self._get_current_timestamp()
            }
        except json.JSONDecodeError:
            return {
                'source_url': url,
                'type': 'json',
                'error': 'Invalid JSON content',
                'raw_content': content
            }

    def _parse_html(self, url: str, content: str) -> Dict:
        """
        Advanced HTML parsing using BeautifulSoup.
        
        :param url: Source URL
        :param content: HTML content
        :return: Parsed HTML data
        """
        soup = BeautifulSoup(content, 'lxml')

        # Compute content hash for deduplication
        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()

        # Advanced extraction techniques
        return {
            'source_url': url,
            'parsed_domain': urllib.parse.urlparse(url).netloc,
            'type': 'html',
            'content_hash': content_hash,
            'metadata': {
                'titles': [title.get_text().strip() for title in soup.find_all(['h1', 'h2', 'h3'])],
                'links': [
                    {
                        'href': link.get('href', ''),
                        'text': link.get_text().strip(),
                        'is_internal': link.get('href', '').startswith('/')
                    } for link in soup.find_all('a', href=True)
                ],
                'images': [
                    {
                        'src': img.get('src', ''),
                        'alt': img.get('alt', '')
                    } for img in soup.find_all('img', src=True)
                ]
            },
            'text_content': {
                'paragraphs': [p.get_text().strip() for p in soup.find_all('p')],
                'word_count': len(soup.get_text().split()),
                'unique_words': len(set(soup.get_text().lower().split()))
            },
            'parsed_at': self._get_current_timestamp()
        }

    def _parse_text(self, url: str, content: str) -> Dict:
        """
        Parse plain text content.
        
        :param url: Source URL
        :param content: Text content
        :return: Parsed text data
        """
        # Compute content hash for deduplication
        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()

        # Text analysis
        words = content.split()
        unique_words = set(words)

        return {
            'source_url': url,
            'type': 'text',
            'content_hash': content_hash,
            'metadata': {
                'total_chars': len(content),
                'word_count': len(words),
                'unique_word_count': len(unique_words),
                'avg_word_length': sum(len(word) for word in words) / len(words) if words else 0
            },
            'text_sample': content[:500],  # First 500 characters
            'parsed_at': self._get_current_timestamp()
        }

    def _get_current_timestamp(self) -> str:
        """
        Get current timestamp for parsing metadata.
        
        :return: Current timestamp
        """
        from datetime import datetime
        return datetime.now().isoformat()

    def extract_keywords(self, parsed_data: Dict, top_n: int = 10) -> List[str]:
        """
        Extract keywords from parsed data.
        
        :param parsed_data: Parsed data dictionary
        :param top_n: Number of top keywords to return
        :return: List of top keywords
        """
        # Stopwords to filter out
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}

        # Extract text based on content type
        if parsed_data['type'] == 'html':
            text = ' '.join(parsed_data['text_content']['paragraphs'])
        elif parsed_data['type'] == 'text':
            text = parsed_data.get('text_sample', '')
        else:
            return []

        # Lowercase and split
        words = text.lower().split()
        
        # Count word frequencies
        word_freq = {}
        for word in words:
            # Filter out stopwords and short words
            if word not in stopwords and len(word) > 2:
                word_freq[word] = word_freq.get(word, 0) + 1

        # Return top N keywords sorted by frequency
        return sorted(word_freq, key=word_freq.get, reverse=True)[:top_n]

    def detect_language(self, parsed_data: Dict) -> str:
        """
        Detect language of parsed content.
        
        :param parsed_data: Parsed data dictionary
        :return: Detected language code
        """
        try:
            from langdetect import detect
            
            # Extract text based on content type
            if parsed_data['type'] == 'html':
                text = ' '.join(parsed_data['text_content']['paragraphs'])
            elif parsed_data['type'] == 'text':
                text = parsed_data.get('text_sample', '')
            else:
                return 'unknown'

            return detect(text)
        except ImportError:
            return 'language_detection_unavailable'