# Coding Standards

## Overview

This document defines the engineering standards for the Website Knowledge Extraction Engine (WKEE).

Every contributor (human or AI) must follow these standards.

---

## General Principles

- Readability over cleverness.
- Explicit is better than implicit.
- Prefer maintainability over short code.
- Every module should have a single responsibility.
- Avoid unnecessary abstraction.
- Follow SOLID principles.

---

## Language

Python 3.12

---

## Style Guide

PEP8

Maximum line length:

100 characters

Use Ruff formatting.

---

## Type Hints

All public functions must include complete type hints.

Example

```python
def crawl_page(url: str) -> PageData:
```

---

## Docstrings

Every public function must contain Google-style docstrings.

Example

```python
def extract_links(page):
    """
    Extract all navigable links from a webpage.

    Args:
        page: Playwright page object.

    Returns:
        List of extracted links.
    """
```

---

## Imports

Order

1. Standard Library
2. Third-party
3. Internal Modules

---

## Logging

Never use print().

Use structured logging.

Every exception should be logged with context.

---

## Exceptions

Do not catch broad Exception unless re-raising or logging.

Create custom exceptions for crawler-specific failures.

---

## Async

Use async whenever browser operations are involved.

Avoid blocking calls.

---

## Testing

Every public module requires tests.

Target coverage:

80%+

---

## Comments

Explain WHY.

Never explain obvious code.

---

## Naming

Classes:

PascalCase

Functions:

snake_case

Variables:

snake_case

Constants:

UPPER_CASE

Private:

_prefix

---

## Configuration

No hardcoded values.

Everything configurable via YAML or ENV.

---

## Dependencies

Only install packages when required.

Avoid duplicate libraries.

---

## Git

One logical change per commit.

Meaningful commit messages.

Example

feat(browser): add browser session manager

fix(forms): handle hidden input fields
