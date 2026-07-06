from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from shared.logger import get_logger

logger = get_logger(__name__)

class BrowserManager:
    def __init__(self):
        self.playwright = None
        self.browser: Browser = None

    async def start(self, headless=True):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=headless,
            args=["--disable-dev-shm-usage", "--no-sandbox"]
        )
        logger.info(f"Launched Chromium browser (headless={headless})")

    async def stop(self):
        if self.browser:
            await self.browser.close()
            self.browser = None
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None

    async def new_context(self) -> BrowserContext:
        return await self.browser.new_context(
            viewport={'width': 1280, 'height': 800}
        )

    async def new_page(self, context: BrowserContext):
        from .page_manager import PageManager
        page = await context.new_page()
        return PageManager(page)

    async def save_state(self, context: BrowserContext, path: str):
        await context.storage_state(path=path)
