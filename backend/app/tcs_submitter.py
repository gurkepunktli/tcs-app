"""
TCS Benzin Website Submitter
Uses browser-use AI agent to automate price submission on benzin.tcs.ch
"""
import os
import json
import asyncio
from typing import Optional, Dict
from langchain_openai import ChatOpenAI
from browser_use import Agent
from playwright.async_api import async_playwright


class TCSSubmitter:
    def __init__(self, cookies: Optional[Dict] = None, username: str = None, password: str = None, headless: bool = True):
        """
        Initialize TCS Submitter with browser-use AI agent

        Args:
            cookies: Dict of cookies to inject (e.g., {'session': 'abc123', 'auth_token': 'xyz'})
            username: TCS username (optional, only if using login)
            password: TCS password (optional, only if using login)
            headless: Run browser in headless mode
        """
        self.cookies = cookies
        self.username = username
        self.password = password
        self.headless = headless
        self.browser = None
        self.context = None
        self.page = None
        self.playwright = None

        # Get OpenRouter API key from environment
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable not set")

        # Get model choice from environment (default to Claude 3.5 Sonnet)
        model_name = os.getenv('LLM_MODEL', 'anthropic/claude-3.5-sonnet')

        # Initialize LLM with OpenRouter
        self.llm = ChatOpenAI(
            model=model_name,
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )

    async def _init_browser(self):
        """Initialize Playwright browser"""
        self.playwright = await async_playwright().start()

        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
            ]
        )

        # Create context with permissions for geolocation
        self.context = await self.browser.new_context(
            permissions=['geolocation'],
            viewport={'width': 1920, 'height': 1080}
        )

        self.page = await self.context.new_page()

    async def _inject_cookies(self):
        """Inject cookies into the browser session"""
        if not self.cookies:
            return

        # Navigate to domain first
        await self.page.goto('https://benzin.tcs.ch')
        await asyncio.sleep(1)

        # Convert cookies to Playwright format
        playwright_cookies = []
        for name, value in self.cookies.items():
            cookie_dict = {
                'name': name,
                'value': value,
                'domain': '.tcs.ch',
                'path': '/',
            }
            playwright_cookies.append(cookie_dict)

        try:
            await self.context.add_cookies(playwright_cookies)
            print(f"Injected {len(playwright_cookies)} cookies")
        except Exception as e:
            print(f"Failed to inject cookies: {e}")

        # Refresh to apply cookies
        await self.page.reload()
        await asyncio.sleep(1)

    async def _set_geolocation(self, latitude: float, longitude: float, accuracy: float = 100):
        """Override browser geolocation"""
        await self.context.set_geolocation({
            "latitude": latitude,
            "longitude": longitude,
            "accuracy": accuracy
        })
        await self.context.grant_permissions(['geolocation'])
        print(f"Set geolocation to: {latitude}, {longitude}")

    async def login(self) -> bool:
        """
        Login to benzin.tcs.ch
        If cookies are provided, inject them instead of logging in
        Returns True if successful, False otherwise
        """
        try:
            if not self.browser:
                await self._init_browser()

            # If cookies are provided, use them instead of login
            if self.cookies:
                print("Using provided cookies for authentication")
                await self._inject_cookies()
                return True

            # Otherwise, perform traditional login
            if not self.username or not self.password:
                print("No cookies or credentials provided")
                return False

            # Navigate to login page
            await self.page.goto('https://benzin.tcs.ch')
            await asyncio.sleep(2)

            # TODO: Implement actual login steps if needed
            # Currently not needed if using cookies
            print(f"[STUB] Would login with user: {self.username}")
            print("NOTE: Traditional login not implemented - provide cookies instead")
            return False

        except Exception as e:
            print(f"Login failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    async def submit_prices(
        self,
        latitude: float,
        longitude: float,
        benzin_95: Optional[float] = None,
        benzin_98: Optional[float] = None,
        diesel: Optional[float] = None
    ) -> bool:
        """
        Submit fuel prices to TCS website using AI agent

        Args:
            latitude: GPS latitude
            longitude: GPS longitude
            benzin_95: Price for Benzin 95
            benzin_98: Price for Benzin 98
            diesel: Price for Diesel

        Returns:
            True if submission successful, False otherwise
        """
        try:
            if not self.browser:
                # Login first if not already done
                if not await self.login():
                    return False

            # Set geolocation to provided coordinates
            print(f"Setting GPS location to: {latitude}, {longitude}")
            await self._set_geolocation(latitude, longitude)

            # Navigate to the main page
            await self.page.goto('https://benzin.tcs.ch')
            await asyncio.sleep(3)

            # Build task description for AI agent
            price_updates = []
            if benzin_95:
                price_updates.append(f"Benzin 95 to {benzin_95} CHF")
            if benzin_98:
                price_updates.append(f"Benzin 98 to {benzin_98} CHF")
            if diesel:
                price_updates.append(f"Diesel to {diesel} CHF")

            if not price_updates:
                print("No prices to update")
                return False

            price_text = ", ".join(price_updates)

            task = f"""
            You are on the benzin.tcs.ch website. The browser's GPS location is already set to coordinates {latitude}, {longitude}.

            Your task:
            1. Find and click on the nearest gas station on the map (it should appear based on the GPS location)
            2. For this gas station, update the following fuel prices: {price_text}
            3. Click the "AKTUALISIEREN" (update) button for each fuel type
            4. Enter the new price in the dialog that appears
            5. Confirm/save the price update
            6. Repeat for all fuel types that need updating

            Important notes:
            - The website is in German/French
            - Look for "AKTUALISIEREN" buttons next to each fuel type
            - The map should show nearby stations based on GPS
            - Click on the first/nearest station marker on the map
            - Be careful to update the correct fuel types with the correct prices
            """

            print(f"Starting AI agent to submit prices: {price_text}")
            print(f"Location: {latitude}, {longitude}")

            # Create browser-use agent with our existing browser context
            # The context already has GPS coordinates and cookies set
            agent = Agent(
                task=task,
                llm=self.llm,
            )

            # Run the agent using our existing page that already has:
            # - GPS coordinates set via self.context.set_geolocation()
            # - TCS cookies injected
            # - Browser is already at https://benzin.tcs.ch
            result = await agent.run(page=self.page)

            print(f"AI agent completed with result: {result}")

            return True

        except Exception as e:
            print(f"Price submission failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    async def close(self):
        """Close the browser"""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        self.browser = None
        self.context = None
        self.page = None

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()


async def submit_to_tcs(
    latitude: float,
    longitude: float,
    prices: Dict[str, float],
    cookies: Optional[Dict] = None,
    username: str = None,
    password: str = None
) -> bool:
    """
    Convenience function to submit prices to TCS

    Args:
        latitude: GPS latitude
        longitude: GPS longitude
        prices: Dictionary with keys 'benzin_95', 'benzin_98', 'diesel'
        cookies: Dict of cookies for authentication (preferred method)
        username: TCS account username (fallback)
        password: TCS account password (fallback)

    Returns:
        True if successful, False otherwise
    """
    async with TCSSubmitter(cookies=cookies, username=username, password=password) as submitter:
        return await submitter.submit_prices(
            latitude=latitude,
            longitude=longitude,
            benzin_95=prices.get('benzin_95'),
            benzin_98=prices.get('benzin_98'),
            diesel=prices.get('diesel')
        )
