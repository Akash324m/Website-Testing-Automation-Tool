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
        if (!el || el.nodeType !== 1) return "";
        let path = [];
        while (el && el.nodeType === Node.ELEMENT_NODE) {
            let selector = el.tagName.toLowerCase();
            if (selector === "html") {
                path.unshift(selector);
                break;
            }
            if (el.id) {
                selector += '#' + el.id;
                path.unshift(selector);
                break;
            } else {
                let sib = el, nth = 1;
                while (sib = sib.previousElementSibling) {
                    if (sib.tagName.toLowerCase() == selector) nth++;
                }
                if (nth !== 1 || el.nextElementSibling) {
                    // It's safer to always add nth-of-type if it has siblings of same type, 
                    // or just always if no ID is present and we want exact paths.
                    let siblingCount = 0;
                    let s = el.parentNode.firstElementChild;
                    while(s) { if(s.tagName === el.tagName) siblingCount++; s = s.nextElementSibling; }
                    if (siblingCount > 1) {
                        selector += `:nth-of-type(${nth})`;
                    }
                }
            }
            path.unshift(selector);
            el = el.parentNode;
        }
        return path.join(" > ");
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
        
        // Helper to find label text for an input
        function findLabelText(inp) {
            if (inp.id) {
                let lbl = document.querySelector(`label[for="${inp.id}"]`);
                if (lbl) return lbl.innerText.trim();
            }
            let parentLbl = inp.closest('label');
            if (parentLbl) return parentLbl.innerText.trim();
            return inp.getAttribute('aria-label') || inp.getAttribute('placeholder') || inp.getAttribute('name') || inp.id || '';
        }
        
        // Extract inputs, selects, and textareas
        f.querySelectorAll('input, select, textarea').forEach((inp) => {
            if (isVisible(inp) && inp.type !== 'hidden') {
                let tagName = inp.tagName.toLowerCase();
                let attrs = {
                    type: inp.type || '',
                    required: inp.hasAttribute('required') ? 'true' : 'false',
                    min: inp.getAttribute('min') || '',
                    max: inp.getAttribute('max') || '',
                    pattern: inp.getAttribute('pattern') || '',
                    maxlength: inp.getAttribute('maxlength') || ''
                };
                
                // If it's a select, grab the options
                if (tagName === 'select') {
                    let options = Array.from(inp.options).map(opt => opt.value + "::" + opt.text);
                    attrs['options'] = options.join('|');
                }
                
                inputs.push({
                    type: tagName,
                    label: findLabelText(inp),
                    role: 'input',
                    css_selector: getCssSelector(inp),
                    xpath: '',
                    attributes: attrs
                });
            }
        });
        
        // Extract buttons
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
