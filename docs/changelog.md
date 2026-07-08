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
- Added `crawler/explorer/models.py` defining structured `StateNode` and `InteractionEdge` dataclasses.
- Added `crawler/explorer/graph_manager.py` using NetworkX to map the crawler's state machine.
- Added `crawler/explorer/navigator.py` to orchestrate breadth-first DOM extraction and safe link navigation.
- Wrote unit tests for `GraphManager` and `Navigator`.
- Created `examples/demo_explorer.py` to demonstrate exploration and graph generation.
- Added `crawler/workflow/models.py` defining `Workflow` and `WorkflowStep`.
- Added `crawler/workflow/extractor.py` to heuristically extract task paths from the NetworkX graph.
- Wrote unit tests for `WorkflowExtractor`.
- Updated `examples/demo_explorer.py` to output extracted `workflows.json`.
- Updated `crawler/extractor/dom_extractor.py` JS payload to capture `<label>` relationships, input validation rules (`required`, `min`, `max`, `pattern`, `maxlength`), and `<select>` options.
- Added `crawler/duplicate_detection/dom_hasher.py` to compute structural hashes of DOM, stripping dynamic IDs and classes.
- Added `crawler/duplicate_detection/url_normalizer.py` to identify dynamic path segments in clustered URLs and replace them with `{id}`.
- Added `crawler/duplicate_detection/cluster_manager.py` to manage `TemplateCluster`s and map page data to template IDs.
- Integrated `ClusterManager` into `GraphManager` and `Navigator`, fundamentally changing the graph to connect templates instead of raw URLs.
- Wrote unit tests for duplicate detection logic.
- Created `examples/demo_duplicate.py` to demonstrate URL normalization and template clustering of product pages.
- Added `crawler/embeddings/vector_store.py` for FAISS indexing.
- Added `crawler/embeddings/embedder.py` for semantic inference using `sentence-transformers`.
- Added `crawler/embeddings/indexer.py` to bridge the crawler and embeddings modules by formatting states, workflows, and forms into descriptive strings.
- Created `examples/demo_embeddings.py` which successfully finds the "Login" page when searching for "I need to access my account".
- Added `crawler/vision/screenshotter.py` to manage capturing screenshots via Playwright.
- Added `crawler/vision/llm_client.py` containing a `MockVisionLLMClient` to simulate Vision LLM advice without requiring API keys.
- Added `crawler/vision/recovery_agent.py` to orchestrate screenshot capturing and prompting the LLM when the crawler is stuck.
- Wrote unit tests for the vision recovery logic.
- Created `examples/demo_vision.py` to demonstrate the Vision Recovery Agent in action.
- Added `crawler/cache/state_cache.py` to implement incremental crawling by caching DOM hashes.
- Updated `crawler/explorer/navigator.py` to check the cache before registering states, skipping unchanged pages.
- Wrote unit tests for incremental cache logic.
- Created `examples/demo_incremental.py` to demonstrate skipping un-changed DOM structures despite dynamic IDs.
- Added `crawler/agent/graph.py` to construct the LangGraph workflow (`retrieve_target` -> `plan_path` -> `execute_path`).
- Added `crawler/agent/executor.py` to wrap the LangGraph agent for easy execution of natural language goals.
- Exposed `get_shortest_path` in `crawler/explorer/graph_manager.py` using `networkx.shortest_path`.
- Wrote unit tests in `tests/crawler/agent/test_agent.py` to verify the state transitions of the LangGraph execution agent.
- Created `examples/demo_agent.py` which mocks a knowledge index and successfully executes a multi-step goal ("Download food license").

### Changed
- Replaced `selenium` with `playwright` in `requirements.txt`.
- Set up Project Structure including directories for config, crawler, agent, etc.
