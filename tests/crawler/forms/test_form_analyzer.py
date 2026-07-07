import pytest
from crawler.extractor.models import PageData, Form, SemanticComponent
from crawler.forms.analyzer import FormAnalyzer

def test_form_analyzer():
    # Mock extracted raw form
    raw_inputs = [
        SemanticComponent(
            type="input", role="input", label="Username Label", css_selector="input#username", xpath="",
            attributes={"type": "text", "required": "true", "maxlength": "20"}
        ),
        SemanticComponent(
            type="input", role="input", label="Password Label", css_selector="input#password", xpath="",
            attributes={"type": "password"}
        )
    ]
    raw_buttons = [
        SemanticComponent(
            type="button", role="submit", label="Sign In", css_selector="button#submit", xpath="",
            attributes={}
        )
    ]
    raw_form = Form(id="login-form", action="/login", method="POST", inputs=raw_inputs, buttons=raw_buttons)
    
    page_data = PageData(url="http://test.com/login", title="Login", components=[], forms=[raw_form])
    
    analyzer = FormAnalyzer(page_data)
    semantic_forms = analyzer.analyze_forms()
    
    assert len(semantic_forms) == 1
    sf = semantic_forms[0]
    
    assert sf.intent == "Login"
    assert len(sf.fields) == 2
    
    assert sf.fields[0].tag_name == "input"
    assert sf.fields[0].validation.input_type == "text"
    assert sf.fields[0].validation.required is True
    assert sf.fields[0].validation.max_length == 20
    assert sf.fields[0].logical_label == "Username Label"
    
    assert sf.fields[1].tag_name == "input"
    assert sf.fields[1].validation.input_type == "password"
    assert sf.fields[1].validation.required is False
