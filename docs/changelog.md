# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] - 2026-07-06

### Added
- Created `shared/logger.py` with `structlog` setup for JSON and console logging.
- Created `shared/config.py` to parse YAML configurations.
- Added `crawler/browser/browser_manager.py` to manage Playwright browser instances and context lifecycle.
- Added `crawler/browser/page_manager.py` to wrap Playwright pages with automated dialog handling, screenshots, and navigation.
- Added custom exceptions in `crawler/browser/exceptions.py`.
- Wrote initial unit tests for `BrowserManager` and `PageManager`.
- Added `crawler/extractor/models.py` defining structured `PageData` and `SemanticComponent` dataclasses.
- Added `crawler/extractor/html_parser.py` using BeautifulSoup for fast, static metadata parsing.
- Added `crawler/extractor/dom_extractor.py` which injects a Javascript payload for high-performance DOM traversal and bounding box calculation.
- Wrote unit tests for `HTMLParser` and `DOMExtractor`.
- Created `examples/demo_extractor.py` to demonstrate DOM extraction saving to `pages.json`.

### Changed
- Replaced `selenium` with `playwright` in `requirements.txt`.
- Set up Project Structure including directories for config, crawler, agent, etc.
