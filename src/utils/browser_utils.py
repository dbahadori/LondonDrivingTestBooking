import os
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class BrowserUtils:
    def __init__(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--window-size=1920x1080")

        # Disable images to save data
        prefs = {
            "profile.managed_default_content_settings.images": 2  # Disable images
        }
        self.chrome_options.add_experimental_option("prefs", prefs)

        # Set up WebDriver
        if os.getenv('AIRFLOW__CORE__EXECUTOR'):
            self.driver = webdriver.Chrome(service=Service('/usr/local/bin/chromedriver'), options=self.chrome_options)
        else:
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.chrome_options)

    def close_popup(self, popup_class: str = 'swal2-popup', confirm_btn_text: str = 'تایید'):
        """Check if a popup exists and close it if present."""
        try:
            # Wait for the popup element to be present
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, f"//*[contains(@class, '{popup_class}')]"))
            )

            # Look for the "تایید" button in the popup
            confirm_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f"//*[text()='{confirm_btn_text}']"))
            )
            confirm_button.click()
            logging.info("Popup closed.")
        except Exception as e:
            logging.warning(f"No popup detected or failed to close: {e}")

    def get_element(self, locator_type, locator_value, wait_time=10):
        """
        Retrieve an element based on the provided locator type and value.

        Parameters:
        - locator_type: Type of locator (e.g., By.CLASS_NAME, By.XPATH, etc.)
        - locator_value: The value for the locator.
        - wait_time: Time to wait for the element to be present.

        Returns:
        - WebElement if found, else None.
        """
        try:
            element = WebDriverWait(self.driver, wait_time).until(
                EC.presence_of_element_located((locator_type, locator_value))
            )
            return element
        except Exception as e:
            logging.error(f"Error while retrieving element {locator_value}: {e}")
            return None

    def get_fund_manager_label(self):
        """Retrieve the fund manager label element."""
        fund_info_container = self.get_element(By.CLASS_NAME, 'fund-info-container')
        if fund_info_container:
            manager_label = self.get_element(By.XPATH,
                                             ".//div[contains(@class, 'row fund-info')]/div/span[contains(text(), 'مدیر صندوق')]",
                                             wait_time=5)
            if manager_label:
                return manager_label.find_element(By.XPATH, 'parent::div/following-sibling::div/h4')
        logging.warning("Fund manager label not found; returning None.")
        return None
    def navigate_to_url(self, url):
        """Navigate to the specified URL."""
        self.driver.get(url)
    def get_driver(self):
        """Return the initialized WebDriver."""
        return self.driver

    def quit_driver(self):
        """Quit the WebDriver."""
        self.driver.quit()
