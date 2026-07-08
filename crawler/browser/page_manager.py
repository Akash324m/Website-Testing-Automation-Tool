from playwright.async_api import Page
from shared.logger import get_logger

logger = get_logger(__name__)

class PageManager:
    def __init__(self, page: Page):
        self.page = page
        self.page.on("dialog", self.handle_dialog)
        self.page.on("console", self.handle_console)

    async def handle_dialog(self, dialog):
        logger.info(f"Auto-dismissing dialog: {dialog.message}")
        await dialog.dismiss()

    async def handle_console(self, msg):
        if msg.type == "error":
            logger.error(f"Page console error: {msg.text}")

    async def navigate(self, url: str):
        logger.info(f"Navigating to {url}")
        await self.page.goto(url, wait_until="networkidle")

    async def wait_for_load_state(self):
        await self.page.wait_for_load_state("networkidle")

    async def take_screenshot(self, path: str):
        await self.page.screenshot(path=path)

    async def click(self, selector: str):
        await self.page.click(selector)
        
    async def fill(self, selector: str, value: str):
        await self.page.fill(selector, value)
