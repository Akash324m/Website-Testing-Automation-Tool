from typing import Any, Dict
from playwright.async_api import Page
from shared.logger import get_logger
from .models import PageData, SemanticComponent, Form

logger = get_logger(__name__)

# The injected script traverses the DOM, grabbing bounding boxes,
# and filtering out non-interactive or invisible elements.
JS_EXTRACTION_SCRIPT = """
() => {
    function isVisible(elem) {
        if (!elem || elem.nodeType !== 1) return false;
        const style = window.getComputedStyle(elem);
        if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') return false;
        const rect = elem.getBoundingClientRect();
        if (rect.width === 0 || rect.height === 0) return false;
        return true;
    }

    function getCssSelector(el) {
        if (el.tagName.toLowerCase() == "html") return "html";
        let str = el.tagName.toLowerCase();
        str += (el.id != "") ? "#" + el.id : "";
        if (el.className) {
            let classes = el.className.trim().split(/\\s+/);
            for (let i = 0; i < classes.length; i++) {
                str += "." + classes[i];
            }
        }
        return str;
    }

    const components = [];
    const interactiveSelectors = 'a, button, input, select, textarea, [role="button"], [role="link"], [tabindex]:not([tabindex="-1"])';
    
    document.querySelectorAll(interactiveSelectors).forEach((el) => {
        if (!isVisible(el)) return;
        
        let type = el.tagName.toLowerCase();
        let role = el.getAttribute('role') || type;
        let label = el.innerText || el.value || el.getAttribute('aria-label') || el.getAttribute('placeholder') || '';
        
        // Exclude generic hidden inputs
        if (type === 'input' && el.type === 'hidden') return;
        
        const rect = el.getBoundingClientRect();
        
        components.push({
            type: type,
            role: role,
            label: label.trim().substring(0, 100),
            css_selector: getCssSelector(el),
            xpath: '', // Simplified for now, can implement robust xpath later
            attributes: {
                id: el.id || '',
                name: el.name || '',
                type: el.type || '',
                href: el.href || ''
            }
        });
    });

    const forms = [];
    document.querySelectorAll('form').forEach((f) => {
        if (!isVisible(f)) return;
        
        let formId = f.id || f.name || getCssSelector(f);
        let action = f.getAttribute('action') || '';
        let method = f.getAttribute('method') || 'GET';
        
        let inputs = [];
        let buttons = [];
        
        f.querySelectorAll('input, select, textarea').forEach((inp) => {
            if (isVisible(inp) && inp.type !== 'hidden') {
                inputs.push({
                    type: inp.tagName.toLowerCase(),
                    label: inp.getAttribute('name') || inp.id || '',
                    role: 'input',
                    css_selector: getCssSelector(inp),
                    xpath: '',
                    attributes: {type: inp.type || ''}
                });
            }
        });
        
        f.querySelectorAll('button, input[type="submit"]').forEach((btn) => {
            if (isVisible(btn)) {
                buttons.push({
                    type: 'button',
                    label: btn.innerText || btn.value || 'Submit',
                    role: 'submit',
                    css_selector: getCssSelector(btn),
                    xpath: '',
                    attributes: {}
                });
            }
        });
        
        forms.push({
            id: formId,
            action: action,
            method: method,
            inputs: inputs,
            buttons: buttons
        });
    });

    return {
        url: window.location.href,
        title: document.title,
        components: components,
        forms: forms
    };
}
"""

class DOMExtractor:
    """
    Extracts semantic knowledge from a Playwright Page using
    JavaScript injection and DOM API.
    """

    def __init__(self):
        pass

    async def extract(self, page: Page) -> PageData:
        """
        Extracts DOM structures, forms, and components from the given page.
        
        Args:
            page: Playwright Page instance.
            
        Returns:
            A populated PageData object.
        """
        logger.info(f"Extracting DOM for {page.url}")
        
        try:
            # Inject JS to extract layout and interactive elements
            result = await page.evaluate(JS_EXTRACTION_SCRIPT)
            
            # Map JS result into Python models
            components = []
            for c in result.get('components', []):
                components.append(SemanticComponent(
                    type=c['type'],
                    role=c['role'],
                    label=c['label'],
                    css_selector=c['css_selector'],
                    xpath=c['xpath'],
                    attributes=c['attributes']
                ))
                
            forms = []
            for f in result.get('forms', []):
                inputs = []
                for i in f['inputs']:
                    inputs.append(SemanticComponent(**i))
                buttons = []
                for b in f['buttons']:
                    buttons.append(SemanticComponent(**b))
                    
                forms.append(Form(
                    id=f['id'],
                    action=f['action'],
                    method=f['method'],
                    inputs=inputs,
                    buttons=buttons
                ))
                
            # Get raw HTML for static processing if needed later
            raw_html = await page.content()
            
            page_data = PageData(
                url=result.get('url', page.url),
                title=result.get('title', ''),
                components=components,
                forms=forms,
                raw_html=raw_html
            )
            
            logger.info(f"Extracted {len(components)} components and {len(forms)} forms.")
            return page_data
            
        except Exception as e:
            logger.error(f"Failed to extract DOM from {page.url}: {str(e)}")
            raise
