import pytest
from crawler.extractor.html_parser import HTMLParser

def test_html_parser_extracts_metadata():
    html = """
    <html>
        <head>
            <title>Test Page</title>
            <meta name="description" content="A test page" />
            <meta property="og:title" content="Test Page OG" />
        </head>
        <body>
            <h1>Main Heading</h1>
            <h2>Sub Heading</h2>
        </body>
    </html>
    """
    
    parser = HTMLParser(html_content=html, url="https://test.com")
    data = parser.parse_basic_page_data()
    
    assert data.title == "Test Page"
    assert data.url == "https://test.com"
    assert data.metadata.get("description") == "A test page"
    assert data.metadata.get("og:title") == "Test Page OG"
    assert "Main Heading" in data.headings
    assert "Sub Heading" in data.headings
