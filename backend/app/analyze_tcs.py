"""
Helper script to analyze benzin.tcs.ch structure
Run this to explore the website and find the correct selectors

Usage:
    python analyze_tcs.py --no-headless  # Run with visible browser
    python analyze_tcs.py                # Run headless
"""
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
import json


def analyze_site(headless=True):
    """Analyze benzin.tcs.ch to find selectors and flow"""

    chrome_options = Options()
    if headless:
        chrome_options.add_argument('--headless')

    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')

    service = Service('/usr/bin/chromedriver')
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        print("=" * 60)
        print("Analyzing benzin.tcs.ch")
        print("=" * 60)

        # Navigate to site
        driver.get('https://benzin.tcs.ch')
        print(f"\n1. Loaded: {driver.current_url}")
        print(f"   Title: {driver.title}")

        # Wait for React app to load
        time.sleep(5)

        # Get page source length
        page_source = driver.page_source
        print(f"\n2. Page source length: {len(page_source)} characters")

        # Find all buttons
        buttons = driver.find_elements(By.TAG_NAME, 'button')
        print(f"\n3. Found {len(buttons)} buttons:")
        for i, btn in enumerate(buttons[:10]):  # Show first 10
            text = btn.text.strip()
            classes = btn.get_attribute('class')
            data_testid = btn.get_attribute('data-testid')
            if text or data_testid:
                print(f"   [{i}] Text: '{text}' | data-testid: '{data_testid}' | class: '{classes}'")

        # Find all links
        links = driver.find_elements(By.TAG_NAME, 'a')
        print(f"\n4. Found {len(links)} links:")
        for i, link in enumerate(links[:10]):  # Show first 10
            text = link.text.strip()
            href = link.get_attribute('href')
            if text or href:
                print(f"   [{i}] Text: '{text}' | href: '{href}'")

        # Find all input fields
        inputs = driver.find_elements(By.TAG_NAME, 'input')
        print(f"\n5. Found {len(inputs)} input fields:")
        for i, inp in enumerate(inputs[:10]):  # Show first 10
            name = inp.get_attribute('name')
            input_type = inp.get_attribute('type')
            placeholder = inp.get_attribute('placeholder')
            print(f"   [{i}] type: '{input_type}' | name: '{name}' | placeholder: '{placeholder}'")

        # Look for login-related elements
        print("\n6. Looking for login elements...")
        login_keywords = ['login', 'anmelden', 'sign', 'auth', 'einloggen']
        for keyword in login_keywords:
            elements = driver.find_elements(By.XPATH, f"//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{keyword}')]")
            if elements:
                print(f"   Found {len(elements)} elements with '{keyword}'")
                for elem in elements[:3]:
                    print(f"      Tag: {elem.tag_name}, Text: '{elem.text[:50]}'")

        # Look for price-related elements
        print("\n7. Looking for price submission elements...")
        price_keywords = ['preis', 'price', 'melden', 'add', 'hinzufügen', 'submit']
        for keyword in price_keywords:
            elements = driver.find_elements(By.XPATH, f"//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{keyword}')]")
            if elements:
                print(f"   Found {len(elements)} elements with '{keyword}'")
                for elem in elements[:3]:
                    print(f"      Tag: {elem.tag_name}, Text: '{elem.text[:50]}'")

        # Check for React dev attributes
        print("\n8. React/Dev attributes:")
        react_root = driver.find_elements(By.ID, 'root')
        if react_root:
            print("   Found React root element (#root)")

        app_element = driver.find_elements(By.ID, 'app')
        if app_element:
            print("   Found app element (#app)")

        # Save page source for inspection
        with open('/tmp/benzin_tcs_page_source.html', 'w', encoding='utf-8') as f:
            f.write(page_source)
        print("\n9. Saved page source to: /tmp/benzin_tcs_page_source.html")

        # Take screenshot
        driver.save_screenshot('/tmp/benzin_tcs_screenshot.png')
        print("10. Saved screenshot to: /tmp/benzin_tcs_screenshot.png")

        # Check console logs (if available)
        print("\n11. Browser console logs:")
        try:
            logs = driver.get_log('browser')
            for log in logs[:10]:
                print(f"   {log['level']}: {log['message'][:100]}")
        except:
            print("   (Console logs not available)")

        # Wait for manual inspection if not headless
        if not headless:
            print("\n" + "=" * 60)
            print("Browser window is open for manual inspection")
            print("Close the browser window to continue...")
            print("=" * 60)
            input("Press Enter when done...")

    finally:
        driver.quit()
        print("\n" + "=" * 60)
        print("Analysis complete!")
        print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Analyze benzin.tcs.ch structure')
    parser.add_argument('--no-headless', action='store_true', help='Run with visible browser')
    args = parser.parse_args()

    analyze_site(headless=not args.no_headless)
