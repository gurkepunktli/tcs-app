"""
TCS Benzin Website Submitter
Logs into benzin.tcs.ch and submits fuel prices via Chrome Headless
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import os
import time
from typing import Optional, Dict


class TCSSubmitter:
    def __init__(self, cookies: Optional[Dict] = None, username: str = None, password: str = None, headless: bool = True):
        """
        Initialize TCS Submitter

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
        self.driver = None

    def _init_driver(self):
        """Initialize Chrome WebDriver"""
        chrome_options = Options()

        if self.headless:
            chrome_options.add_argument('--headless')

        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')

        # Allow geolocation override
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.geolocation": 1
        })

        # Use chromium-driver from system
        service = Service('/usr/bin/chromedriver')

        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.implicitly_wait(10)

    def _set_geolocation(self, latitude: float, longitude: float, accuracy: float = 100):
        """Override browser geolocation via Chrome DevTools Protocol"""
        self.driver.execute_cdp_cmd("Emulation.setGeolocationOverride", {
            "latitude": latitude,
            "longitude": longitude,
            "accuracy": accuracy
        })

    def _inject_cookies(self):
        """Inject cookies into the browser session"""
        if not self.cookies:
            return

        # Navigate to domain first
        self.driver.get('https://benzin.tcs.ch')
        time.sleep(1)

        # Add each cookie
        for name, value in self.cookies.items():
            cookie_dict = {
                'name': name,
                'value': value,
                'domain': '.tcs.ch',  # Allow for subdomains
            }
            try:
                self.driver.add_cookie(cookie_dict)
                print(f"Injected cookie: {name}")
            except Exception as e:
                print(f"Failed to inject cookie {name}: {e}")

        # Refresh to apply cookies
        self.driver.refresh()
        time.sleep(1)

    def login(self) -> bool:
        """
        Login to benzin.tcs.ch
        If cookies are provided, inject them instead of logging in
        Returns True if successful, False otherwise
        """
        try:
            if not self.driver:
                self._init_driver()

            # If cookies are provided, use them instead of login
            if self.cookies:
                print("Using provided cookies for authentication")
                self._inject_cookies()
                return True

            # Otherwise, perform traditional login
            if not self.username or not self.password:
                print("No cookies or credentials provided")
                return False

            # Navigate to login page
            self.driver.get('https://benzin.tcs.ch')
            time.sleep(2)

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

    def submit_prices(
        self,
        latitude: float,
        longitude: float,
        benzin_95: Optional[float] = None,
        benzin_98: Optional[float] = None,
        diesel: Optional[float] = None
    ) -> bool:
        """
        Submit fuel prices to TCS website

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
            if not self.driver:
                # Login first if not already done
                if not self.login():
                    return False

            # Set geolocation to provided coordinates
            print(f"Setting GPS location to: {latitude}, {longitude}")
            self._set_geolocation(latitude, longitude)

            # TODO: Analyze benzin.tcs.ch to find the actual selectors
            # Below is a TEMPLATE structure that needs to be filled with real selectors

            # Navigate to the main page
            self.driver.get('https://benzin.tcs.ch')
            time.sleep(2)

            # TODO: Find the "Add Price" or "Preis melden" button
            # Example:
            # add_price_btn = WebDriverWait(self.driver, 10).until(
            #     EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="add-price-button"]'))
            # )
            # add_price_btn.click()

            # TODO: Wait for location/station selection
            # The site might use GPS to find nearby stations
            # Then user selects a station from a list or map

            # TODO: Fill in price fields
            # if benzin_95:
            #     benzin95_input = WebDriverWait(self.driver, 10).until(
            #         EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="benzin95"]'))
            #     )
            #     benzin95_input.clear()
            #     benzin95_input.send_keys(str(benzin_95))

            # if benzin_98:
            #     benzin98_input = self.driver.find_element(By.CSS_SELECTOR, 'input[name="benzin98"]')
            #     benzin98_input.clear()
            #     benzin98_input.send_keys(str(benzin_98))

            # if diesel:
            #     diesel_input = self.driver.find_element(By.CSS_SELECTOR, 'input[name="diesel"]')
            #     diesel_input.clear()
            #     diesel_input.send_keys(str(diesel))

            # TODO: Submit the form
            # submit_btn = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            # submit_btn.click()

            # Wait for confirmation
            # time.sleep(2)

            print(f"[STUB] Would submit prices: B95={benzin_95}, B98={benzin_98}, D={diesel}")
            print(f"[STUB] Location: {latitude}, {longitude}")
            print("NOTE: Actual submission is not implemented - needs real selectors from benzin.tcs.ch")

            return True

        except Exception as e:
            print(f"Price submission failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            self.driver = None

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


def submit_to_tcs(
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
    with TCSSubmitter(cookies=cookies, username=username, password=password) as submitter:
        return submitter.submit_prices(
            latitude=latitude,
            longitude=longitude,
            benzin_95=prices.get('benzin_95'),
            benzin_98=prices.get('benzin_98'),
            diesel=prices.get('diesel')
        )
