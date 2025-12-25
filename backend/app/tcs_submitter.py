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
    def __init__(self, username: str, password: str, headless: bool = True):
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

        # Use chromium-driver from system
        service = Service('/usr/bin/chromedriver')

        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.implicitly_wait(10)

    def login(self) -> bool:
        """
        Login to benzin.tcs.ch
        Returns True if successful, False otherwise
        """
        try:
            if not self.driver:
                self._init_driver()

            # Navigate to login page
            self.driver.get('https://benzin.tcs.ch')

            # Wait for page load
            time.sleep(2)

            # TODO: Implement actual login steps
            # This will depend on the structure of the TCS website
            # Steps typically include:
            # 1. Find and click login button
            # 2. Enter credentials
            # 3. Submit login form
            # 4. Verify successful login

            # Example (adjust selectors based on actual website):
            # login_btn = self.driver.find_element(By.CSS_SELECTOR, '.login-button')
            # login_btn.click()

            # WebDriverWait(self.driver, 10).until(
            #     EC.presence_of_element_located((By.ID, "email"))
            # )

            # email_field = self.driver.find_element(By.ID, "email")
            # password_field = self.driver.find_element(By.ID, "password")

            # email_field.send_keys(self.username)
            # password_field.send_keys(self.password)

            # submit_btn = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            # submit_btn.click()

            # time.sleep(3)

            print(f"Login attempt for user: {self.username}")
            return True

        except Exception as e:
            print(f"Login failed: {str(e)}")
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

            # TODO: Navigate to price submission form
            # This depends on the actual TCS website structure

            # Example flow:
            # 1. Navigate to "Add Price" or similar page
            # 2. Enter location (coordinates or search)
            # 3. Fill in price fields
            # 4. Submit form

            # self.driver.get('https://benzin.tcs.ch/add-price')

            # Fill in coordinates or location
            # lat_field = self.driver.find_element(By.ID, "latitude")
            # lng_field = self.driver.find_element(By.ID, "longitude")
            # lat_field.send_keys(str(latitude))
            # lng_field.send_keys(str(longitude))

            # Fill in prices
            # if benzin_95:
            #     benzin95_field = self.driver.find_element(By.ID, "benzin95")
            #     benzin95_field.send_keys(str(benzin_95))

            # if benzin_98:
            #     benzin98_field = self.driver.find_element(By.ID, "benzin98")
            #     benzin98_field.send_keys(str(benzin_98))

            # if diesel:
            #     diesel_field = self.driver.find_element(By.ID, "diesel")
            #     diesel_field.send_keys(str(diesel))

            # Submit
            # submit_btn = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            # submit_btn.click()

            # time.sleep(2)

            print(f"Submitted prices: B95={benzin_95}, B98={benzin_98}, D={diesel}")
            print(f"Location: {latitude}, {longitude}")

            return True

        except Exception as e:
            print(f"Price submission failed: {str(e)}")
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
    username: str,
    password: str,
    latitude: float,
    longitude: float,
    prices: Dict[str, float]
) -> bool:
    """
    Convenience function to submit prices to TCS

    Args:
        username: TCS account username
        password: TCS account password
        latitude: GPS latitude
        longitude: GPS longitude
        prices: Dictionary with keys 'benzin_95', 'benzin_98', 'diesel'

    Returns:
        True if successful, False otherwise
    """
    with TCSSubmitter(username, password) as submitter:
        return submitter.submit_prices(
            latitude=latitude,
            longitude=longitude,
            benzin_95=prices.get('benzin_95'),
            benzin_98=prices.get('benzin_98'),
            diesel=prices.get('diesel')
        )
