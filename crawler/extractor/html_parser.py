from bs4 import BeautifulSoup
from typing import Dict, List
from shared.logger import get_logger
from .models import PageData

logger = get_logger(__name__)

class HTMLParser:
    """
    Parses HTML content using BeautifulSoup and lxml for static analysis.
    Useful for extracting metadata, head elements, and text when full DOM
    interactions aren't required.
    """

    def __init__(self, html_content: str, url: str):
        """
        Initializes the parser with HTML content.
        
        Args:
            html_content: The raw HTML string.
            url: The URL of the page.
        """
        self.html = html_content
        self.url = url
        self.soup = BeautifulSoup(self.html, 'lxml')

    def extract_metadata(self) -> Dict[str, str]:
        """
        Extracts meta tags from the head.
        
        Returns:
            A dictionary of meta names/properties and their content.
        """
        metadata = {}
        for meta in self.soup.find_all('meta'):
            name = meta.get('name') or meta.get('property')
            content = meta.get('content')
            if name and content:
                metadata[name] = content
        return metadata

    def extract_title(self) -> str:
        """Extracts the page title."""
        title_tag = self.soup.find('title')
        return title_tag.get_text(strip=True) if title_tag else ""

    def extract_headings(self) -> List[str]:
        """Extracts all headings (h1-h6) from the page."""
        headings = []
        for h in self.soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            text = h.get_text(separator=' ', strip=True)
            if text:
                headings.append(text)
        return headings

    def parse_basic_page_data(self) -> PageData:
        """
        Parses basic page data (URL, Title, Metadata, Headings) statically.
        
        Returns:
            A PageData object populated with static data.
        """
        return PageData(
            url=self.url,
            title=self.extract_title(),
            metadata=self.extract_metadata(),
            headings=self.extract_headings(),
            raw_html=self.html
        )
