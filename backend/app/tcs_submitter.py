"""
TCS Benzin Website Submitter
Uses browser-use AI agent to automate price submission on benzin.tcs.ch
"""
import os
import json
import asyncio
from typing import Optional, Dict
from browser_use import Agent, BrowserSession
from langchain_openai import ChatOpenAI
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

        # Initialize LLM with OpenRouter for browser-use compatibility
        # Use langchain_openai.ChatOpenAI with OpenRouter endpoint
        self.llm = ChatOpenAI(
            openai_api_base='https://openrouter.ai/api/v1',
            openai_api_key=api_key,
            model_name=model_name,
            temperature=0.0,
            max_tokens=4096,
            model_kwargs={"tool_choice": "auto"}
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
        Login to benzin.tcs.ch using Browser-Use AI agent
        Handles Azure B2C login flow automatically
        Returns True if successful, False otherwise
        """
        try:
            # If cookies are provided, use them instead of login
            if self.cookies:
                print("Using provided cookies for authentication")
                if not self.browser:
                    await self._init_browser()
                await self._inject_cookies()
                return True

            # Otherwise, perform AI-powered login with Azure B2C
            if not self.username or not self.password:
                print("No cookies or credentials provided")
                return False

            print(f"Logging in with username: {self.username}")

            # Use Browser-Use AI agent to handle Azure B2C login
            login_task = f"""
            Navigate to https://benzin.tcs.ch and log in to the TCS website.

            Steps:
            1. Go to benzin.tcs.ch
            2. Find and click the "Anmelden" or "Login" button
            3. You will be redirected to an Azure B2C login page (touringclubsuisseb2c.b2clogin.com)
            4. Enter the email address: {self.username}
            5. Enter the password: {self.password}
            6. Click the login/submit button
            7. Wait for successful login and redirect back to benzin.tcs.ch

            Important:
            - The login form may be in German, French, or Italian
            - Look for fields labeled "E-Mail", "Email", "Benutzername" or similar
            - Password field may be labeled "Passwort", "Password", "Kennwort" or similar
            - After successful login, you should be redirected back to the main page
            - Verify that you see your account name or a "Abmelden" (logout) button

            Stop when you can confirm you are logged in successfully.
            """

            # Create browser-use BrowserSession
            # Set headless=True for Docker environments to avoid display issues
            browser_session = BrowserSession(
                headless=True,  # Always use headless in Docker
                disable_security=True,
            )

            agent = Agent(
                task=login_task,
                llm=self.llm,
                browser_session=browser_session,
            )

            result = await agent.run()
            print(f"Login agent result: {result}")

            await browser_session.close()

            print("Login completed by AI agent")
            return True

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
            # Login first if not already done
            if not self.cookies and not await self.login():
                return False

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
            Navigate to benzin.tcs.ch and submit fuel prices for a gas station.

            Your task:
            1. Go to https://benzin.tcs.ch
            2. If not logged in, the browser should already have session cookies
            3. The map should show nearby gas stations based on GPS location
            4. Find and click on the nearest gas station on the map at coordinates {latitude}, {longitude}
            5. For this gas station, update the following fuel prices: {price_text}
            6. Click the "AKTUALISIEREN" (update) button for each fuel type
            7. Enter the new price in the dialog that appears
            8. Confirm/save the price update
            9. Repeat for all fuel types that need updating

            Important notes:
            - The website is in German/French
            - Look for "AKTUALISIEREN" buttons next to each fuel type
            - Click on the first/nearest station marker on the map
            - Be careful to update the correct fuel types with the correct prices
            - The GPS location should show stations near: {latitude}, {longitude}
            """

            print(f"Starting AI agent to submit prices: {price_text}")
            print(f"Location: {latitude}, {longitude}")

            # Create browser-use BrowserSession with geolocation
            # Set headless=True for Docker environments to avoid display issues
            browser_session = BrowserSession(
                headless=True,  # Always use headless in Docker
                disable_security=True,
                geolocation={'latitude': latitude, 'longitude': longitude},
            )

            agent = Agent(
                task=task,
                llm=self.llm,
                browser_session=browser_session,
            )

            result = await agent.run()

            print(f"AI agent completed with result: {result}")

            await browser_session.close()

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
