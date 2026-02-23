import time
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException

from bot.driver_manager import setup_driver


def login(driver, username, password, log):
    """
    Handle the login process.

    Args:
        driver: Selenium WebDriver instance
        username: Account username
        password: Account password
        log: Logging callback function
    """
    # Navigate to website
    log("Navigating to login page...", "info")
    driver.get("https://parking.crystalmountainresort.com/login/")
    driver.maximize_window()

    # Click "Returning Users" button
    try:
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[text()='Returning Users']"))
        )
        button.click()
        log("Clicked 'Returning Users' button", "info")
    except Exception as e:
        raise Exception(f"Failed to click 'Returning Users' button: {e}")

    # Enter username
    try:
        username_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Username']"))
        )
        username_input.send_keys(username)
        log("Entered username", "info")
    except Exception as e:
        raise Exception(f"Failed to enter username: {e}")

    # Enter password
    try:
        password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Password']"))
        )
        password_input.send_keys(password)
        log("Entered password", "info")
    except Exception as e:
        raise Exception(f"Failed to enter password: {e}")

    # Click "Sign In" button
    try:
        sign_in_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[text()='Sign In']"))
        )
        sign_in_button.click()
        log("Signed in successfully", "info")
    except Exception as e:
        raise Exception(f"Failed to sign in: {e}")

    # Wait for page to load
    time.sleep(5)


def select_license_plate(driver, license_plate, log):
    """
    Select license plate from dropdown with fuzzy matching.

    Args:
        driver: Selenium WebDriver instance
        license_plate: License plate number to select
        log: Logging callback function

    Returns:
        str: The matched license plate value
    """
    try:
        dropdown = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "plate"))
        )
        select = Select(dropdown)

        # Handle license plate input with fuzzy matching
        if license_plate.strip():
            matched_option = None

            for option in select.options:
                if license_plate.strip().lower().replace(" ", "") in option.text.strip().lower().replace(" ", ""):
                    matched_option = option.text
                    break

            if matched_option:
                select.select_by_visible_text(matched_option)
                log(f"Selected license plate: {matched_option}", "info")
                return matched_option
            else:
                raise Exception("No matching license plate found in dropdown")
        else:
            raise Exception("License plate cannot be empty")
    except Exception as e:
        raise Exception(f"Failed to select license plate: {e}")


def click_add_more_days(driver, log):
    """
    Click the 'Add More Days' link to navigate to calendar.

    Args:
        driver: Selenium WebDriver instance
        log: Logging callback function
    """
    try:
        add_more_days_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[text()='Add More Days' and @class='btn btn-primary']"))
        )
        add_more_days_link.click()
        log("Navigated to calendar view", "info")
    except Exception as e:
        raise Exception(f"Failed to click 'Add More Days': {e}")


def poll_for_availability(driver, date_base, log, refresh_rate=5):
    """
    Poll the calendar for date availability.

    Args:
        driver: Selenium WebDriver instance
        date_base: Base date string in YYYY-MM-DD format
        log: Logging callback function
        refresh_rate: Seconds between refresh attempts (default: 5)
    """
    log(f"Polling for availability on {date_base}...", "polling")

    while True:
        try:
            # Use starts-with to match any timestamp for the target date
            calendar_day = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, f"//div[starts-with(@data-date, '{date_base}')]"))
            )

            # Get the actual data-date value for logging
            actual_date = calendar_day.get_attribute("data-date")
            log(f"Found calendar element: {actual_date}", "info")

            # Check if the date is marked as "available"
            if "fc-unavailable" not in calendar_day.get_attribute("class"):
                log(f"Date {actual_date} is available! Clicking...", "success")
                calendar_day.click()
                break
            else:
                log(f"Date unavailable. Checking again in {refresh_rate}s...", "polling")
                time.sleep(refresh_rate)
                driver.refresh()
        except TimeoutException:
            log(f"Unable to locate date element. Retrying in {refresh_rate}s...", "polling")
            time.sleep(refresh_rate)
            driver.refresh()


def complete_reservation(driver, license_plate, log):
    """
    Complete the reservation and checkout process.

    Args:
        driver: Selenium WebDriver instance
        license_plate: License plate value to select in final dropdown
        log: Logging callback function
    """
    # Click "Reserve Car Parking" button
    try:
        reserve_button = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'add2cart') and contains(., 'Reserve Car Parking')]"))
        )
        reserve_button.click()
        log("Clicked 'Reserve Car Parking' button", "info")
    except Exception as e:
        raise Exception(f"Failed to click 'Reserve Car Parking' button: {e}")

    # Bring window to front
    driver.execute_script("window.focus();")

    # Select license plate in second dropdown
    try:
        dropdown = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.ID, "plate"))
        )
        select = Select(dropdown)
        select.select_by_visible_text(license_plate)
        log("Selected license plate in checkout", "info")
    except Exception as e:
        raise Exception(f"Failed to select license plate in checkout: {e}")

    # Click "Continue" button
    try:
        continue_button = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.ID, "btnCheckout"))
        )
        continue_button.click()
        log("Clicked 'Continue' button", "info")
    except Exception as e:
        raise Exception(f"Failed to click 'Continue' button: {e}")


def run_reservation(username, password, license_plate, date_str, progress_callback=None):
    """
    Main reservation function that coordinates the entire workflow.

    Args:
        username: Account username
        password: Account password
        license_plate: License plate number
        date_str: Date in YYYY/MM/DD format
        progress_callback: Optional callback function(message, status) for status updates

    Returns:
        dict: {"success": bool, "message": str}
    """
    def log(message, status="info"):
        """Internal logging function that calls progress callback if provided"""
        if progress_callback:
            progress_callback(message, status)
        print(f"[{status.upper()}] {message}")

    driver = None

    try:
        # Validate and process date
        log("Validating date format...", "info")
        try:
            date_obj = datetime.strptime(date_str, "%Y/%m/%d")
            date_base = date_obj.strftime("%Y-%m-%d")
            log(f"Looking for date: {date_base}", "info")
        except ValueError:
            raise Exception("Invalid date format. Please use YYYY/MM/DD format.")

        # Initialize driver
        log("Initializing browser...", "info")
        driver = setup_driver()

        # Login phase
        login(driver, username, password, log)

        # License plate selection
        matched_plate = select_license_plate(driver, license_plate, log)

        # Navigate to calendar
        click_add_more_days(driver, log)

        # Poll for availability
        poll_for_availability(driver, date_base, log)

        # Complete reservation
        complete_reservation(driver, matched_plate, log)

        log("Reservation completed successfully!", "success")
        return {"success": True, "message": "Reservation completed successfully!"}

    except Exception as e:
        error_msg = str(e)
        log(f"Error: {error_msg}", "error")
        return {"success": False, "message": error_msg}

    finally:
        if driver:
            log("Closing browser...", "info")
            driver.quit()
