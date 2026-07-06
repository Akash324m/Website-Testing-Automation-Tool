import pytest
from unittest.mock import AsyncMock, MagicMock
from crawler.extractor.dom_extractor import DOMExtractor
from crawler.extractor.models import PageData

@pytest.fixture
def mock_page():
    page = AsyncMock()
    page.url = "https://test.com"
    
    # Mock evaluate to return a predefined JSON response matching the JS script output
    page.evaluate.return_value = {
        "url": "https://test.com",
        "title": "Test Extractor",
        "components": [
            {
                "type": "button",
                "role": "button",
                "label": "Click Me",
                "css_selector": "button#submit",
                "xpath": "",
                "attributes": {"id": "submit"}
            }
        ],
        "forms": [
            {
                "id": "login-form",
                "action": "/login",
                "method": "POST",
                "inputs": [
                    {
                        "type": "input",
                        "role": "input",
                        "label": "username",
                        "css_selector": "input#user",
                        "xpath": "",
                        "attributes": {"type": "text"}
                    }
                ],
                "buttons": [
                    {
                        "type": "button",
                        "role": "submit",
                        "label": "Login",
                        "css_selector": "button#login-btn",
                        "xpath": "",
                        "attributes": {}
                    }
                ]
            }
        ]
    }
    
    page.content.return_value = "<html><body></body></html>"
    return page

@pytest.mark.asyncio
async def test_dom_extractor(mock_page):
    extractor = DOMExtractor()
    page_data: PageData = await extractor.extract(mock_page)
    
    assert page_data.url == "https://test.com"
    assert page_data.title == "Test Extractor"
    assert len(page_data.components) == 1
    assert page_data.components[0].type == "button"
    assert page_data.components[0].label == "Click Me"
    
    assert len(page_data.forms) == 1
    assert page_data.forms[0].id == "login-form"
    assert page_data.forms[0].action == "/login"
    assert len(page_data.forms[0].inputs) == 1
    assert page_data.forms[0].inputs[0].label == "username"
    assert len(page_data.forms[0].buttons) == 1
    assert page_data.forms[0].buttons[0].label == "Login"
