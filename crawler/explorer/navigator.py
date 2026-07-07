import asyncio
from typing import List, Set
from shared.logger import get_logger
from crawler.browser.browser_manager import BrowserManager
from crawler.extractor.dom_extractor import DOMExtractor
from crawler.explorer.graph_manager import GraphManager

logger = get_logger(__name__)


class Navigator:
    """Orchestrates the crawler's exploration strategy to build a state graph."""

    def __init__(
        self, browser: BrowserManager, extractor: DOMExtractor, graph: GraphManager
    ):
        self.browser = browser
        self.extractor = extractor
        self.graph = graph
        self.visited_urls: Set[str] = set()

    async def explore(self, start_url: str, max_depth: int = 2):
        """
        Explores the website starting from start_url.
        Uses a breadth-first search approach.
        """
        queue = [
            (start_url, 0, None, None)
        ]  # (url, depth, previous_state_id, action_details)

        context = await self.browser.new_context()
        page_manager = await self.browser.new_page(context)

        while queue:
            current_url, depth, prev_state_id, prev_action = queue.pop(0)

            if current_url in self.visited_urls or depth > max_depth:
                continue

            # Skip URLs that end with common file extensions to prevent downloads
            if (
                current_url.lower()
                .split("?")[0]
                .endswith(
                    (
                        ".pdf",
                        ".zip",
                        ".png",
                        ".jpg",
                        ".jpeg",
                        ".gif",
                        ".svg",
                        ".doc",
                        ".docx",
                        ".xls",
                        ".xlsx",
                        ".csv",
                        ".tar",
                        ".gz",
                    )
                )
            ):
                logger.info(f"Skipping file download URL: {current_url}")
                continue

            logger.info(f"Navigating to {current_url} (Depth: {depth})")
            try:
                await page_manager.navigate(current_url)
                await page_manager.wait_for_load_state()
            except Exception as e:
                if "Download is starting" in str(e):
                    logger.warning(
                        f"Skipped download URL during navigation: {current_url}"
                    )
                else:
                    logger.error(f"Navigation failed for {current_url}: {e}")
                continue

            self.visited_urls.add(current_url)

            # Extract DOM state
            page_data = await self.extractor.extract(page_manager.page)

            # Register state in graph
            current_state_id = self.graph.add_state(page_data)

            # Record edge if this was reached from a previous state
            if prev_state_id and prev_action:
                self.graph.add_interaction(
                    source_id=prev_state_id,
                    target_id=current_state_id,
                    action_type=prev_action["type"],
                    selector=prev_action["selector"],
                    label=prev_action["label"],
                )

            # Find interactive links to explore further
            # To avoid destructive actions, we only explore <a> links in this phase.
            if depth < max_depth:
                for comp in page_data.components:
                    # Look for links that stay on the same domain and aren't mailto/javascript
                    if comp.type == "a" and "href" in comp.attributes:
                        href = comp.attributes["href"]
                        if (
                            href
                            and href.startswith("http")
                            and current_url.split("/")[2] in href
                        ):
                            queue.append(
                                (
                                    href,
                                    depth + 1,
                                    current_state_id,
                                    {
                                        "type": "click",
                                        "selector": comp.css_selector,
                                        "label": comp.label,
                                    },
                                )
                            )
