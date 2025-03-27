import asyncio
import contextlib
import logging
import os
import platform

import zendriver
from bs4 import BeautifulSoup
from inscriptis import get_text

from .internal.exceptions import (
    InvalidCredentials,
    MissingCredentials,
    MissingInitialization,
    ServerDown,
)
from .internal.objects import Response
from .internal.selectors import DeepSeekSelectors


class DeepSeek:
    def __init__(
        self,
        email: str,
        password: str,
        chat_id: str | None = None,
        headless: bool = True,
        verbose: bool = False,
        chrome_args: list[str] | None = None,
        attempt_cf_bypass: bool = True,
    ) -> None:
        """
        DeepSeek API automation class.

        Args:
            email (str): User email for DeepSeek login.
            password (str): User password for DeepSeek login.
            chat_id (Optional[str]): Specific chat session ID.
            headless (bool): Whether to run browser in headless mode.
            verbose (bool): Enable detailed logging output.
            chrome_args (Optional[List[str]]): Additional arguments for Chrome.
            attempt_cf_bypass (bool): Whether to bypass Cloudflare protection.

        Raises:
            MissingCredentials: If email or password is missing.
        """
        if not email or not password:
            raise MissingCredentials("Email and password are required for login.")

        self.email = email
        self.password = password
        self.chat_id = chat_id
        self.headless = headless
        self.verbose = verbose
        self.chrome_args = chrome_args or []
        self.attempt_cf_bypass = attempt_cf_bypass

        self._initialized = False
        self._deepthink_enabled = False
        self._search_enabled = False
        self.selectors = DeepSeekSelectors()

        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """Sets up the internal logger."""
        logger = logging.getLogger("DeepSeek")
        logger.setLevel(logging.DEBUG if self.verbose else logging.INFO)

        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s"))
        logger.addHandler(handler)
        return logger

    async def __aenter__(self):
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def initialize(self) -> None:
        """
        Initializes browser session and logs in to DeepSeek.

        Raises:
            MissingInitialization: When dependencies or environment is not set up correctly.
        """
        if platform.system() == "Linux" and "DISPLAY" not in os.environ:
            self.logger.debug("Starting virtual display...")
            try:
                from pyvirtualdisplay import Display

                self.display = Display()
                self.display.start()
            except ModuleNotFoundError as e:
                raise MissingInitialization("Install PyVirtualDisplay: `pip install pyvirtualdisplay`") from e
            except FileNotFoundError as e:
                raise MissingInitialization("Install Xvfb: `sudo apt install xvfb`") from e

        self.browser = await zendriver.start(chrome_args=self.chrome_args, headless=self.headless)
        await self.browser.get("https://chat.deepseek.com/")

        if self.attempt_cf_bypass:
            self.logger.debug("Attempting Cloudflare verification...")
            with contextlib.suppress(Exception):
                await self.browser.main_tab.verify_cf()

        self._initialized = True
        asyncio.create_task(self._keep_alive())
        await self._login()

    async def _keep_alive(self):
        """Keeps browser session alive by periodic actions."""
        while self._initialized:
            await asyncio.sleep(300)
            await self.browser.main_tab.reload()

    async def _login(self):
        """Handles DeepSeek login using email and password."""
        self.logger.debug("Logging in...")
        tab = self.browser.main_tab
        await (await tab.select(self.selectors.login.email_input)).send_keys(self.email)
        await (await tab.select(self.selectors.login.password_input)).send_keys(self.password)

        if self.attempt_cf_bypass:
            await (await tab.select(self.selectors.login.confirm_checkbox)).click()

        await (await tab.select(self.selectors.login.login_button)).click()

        try:
            await tab.wait_for(self.selectors.interactions.textbox, timeout=10)
            self.logger.info("Successfully logged into DeepSeek.")
        except Exception as e:
            raise InvalidCredentials("Login failed, check your credentials.") from e

    async def send_message(
        self,
        message: str,
        slow_mode: bool = False,
        deepthink: bool = False,
        search: bool = False,
        timeout: int = 60,
        slow_mode_delay: float = 0.25,
    ) -> Response | None:
        """
        Sends a message to DeepSeek and retrieves the response.

        Args:
            message (str): Message text to send.
            slow_mode (bool): Send message slowly, char by char.
            deepthink (bool): Activate DeepThink feature.
            search (bool): Activate search feature.
            timeout (int): Max wait time for response.
            slow_mode_delay (float): Delay between chars in slow mode.

        Returns:
            Optional[Response]: The DeepSeek response or None if timed out.
        """
        if not self._initialized:
            raise MissingInitialization("Call `initialize()` before sending messages.")

        tab = self.browser.main_tab
        textbox = await tab.select(self.selectors.interactions.textbox)

        self.logger.debug(f"Sending message: {message}")
        if slow_mode:
            for char in message:
                await textbox.send_keys(char)
                await asyncio.sleep(slow_mode_delay)
        else:
            await textbox.send_keys(message)

        send_options = await tab.select(self.selectors.interactions.send_options_parent)
        if deepthink != self._deepthink_enabled:
            await send_options.children[0].click()
            self._deepthink_enabled = deepthink
        if search != self._search_enabled:
            await send_options.children[1].click()
            self._search_enabled = search

        await (await tab.select(self.selectors.interactions.send_button)).click()
        return await self._get_response(timeout)

    async def _get_response(self, timeout: int) -> Response | None:
        """Waits and retrieves response from DeepSeek."""
        tab = self.browser.main_tab
        try:
            await tab.wait_for(self.selectors.backend.response_generating, timeout=timeout)
            await tab.wait_for(self.selectors.backend.response_generated, timeout=timeout)

            responses = await tab.select_all(self.selectors.backend.response_generated)
            latest_response = responses[-1]

            soup = BeautifulSoup(repr(latest_response), "html.parser")
            markdown = "\n\n".join(get_text(str(block)).strip() for block in soup.select(".ds-markdown--block"))

            if "server is busy" in markdown.lower():
                raise ServerDown("Server busy, try again later.")

            return Response(text=markdown)
        except asyncio.TimeoutError:
            self.logger.error("Timed out waiting for response.")
            return None

    async def close(self) -> None:
        """
        Cleans up resources and closes browser.
        """
        self._initialized = False
        if hasattr(self, "browser"):
            await self.browser.stop()
        if hasattr(self, "display"):
            self.display.stop()

    @staticmethod
    def run_sync(coro: asyncio.coroutines) -> any:
        """Runs asynchronous coroutine synchronously."""
        return asyncio.get_event_loop().run_until_complete(coro)

    def send_message_sync(self, *args, **kwargs) -> Response | None:
        """Synchronous wrapper for `send_message`."""
        return self.run_sync(self.send_message(*args, **kwargs))

    def initialize_sync(self):
        """Synchronous wrapper for `initialize`."""
        self.run_sync(self.initialize())

    def close_sync(self):
        """
        Synchronous wrapper for `close`.
        """
        self.run_sync(self.close())
