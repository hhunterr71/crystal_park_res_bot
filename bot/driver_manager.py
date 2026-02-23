import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


def setup_driver():
    """
    Setup Chrome driver for browser automation.
    Configures headless mode for cloud deployment.

    Returns:
        webdriver.Chrome: Configured Chrome driver instance
    """
    options = Options()

    # Headless mode for cloud environments
    options.add_argument('--headless')

    # Required for Docker/cloud environments
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')

    # Set window size for consistent rendering
    options.add_argument('--window-size=1920,1080')

    # Use Chrome binary from environment variable if set (for cloud deployments)
    if os.getenv('CHROME_BIN'):
        options.binary_location = os.getenv('CHROME_BIN')

    # Initialize driver
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    return driver
