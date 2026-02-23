import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException
import getpass

username = input("Enter username: ")
password = getpass.getpass("Enter password: ")
license_plate = input("Enter license plate: ")
date_input = input("Enter date (YYYY/MM/DD): ")

# Process the date and handle errors
try:
    date_obj = datetime.strptime(date_input, "%Y/%m/%d")
    date_base = date_obj.strftime("%Y-%m-%d")  # Just the date portion (YYYY-MM-DD)
    print(f"Looking for date: {date_base}")
except ValueError:
    print("Invalid date format. Please enter the date in 'YYYY/MM/DD' format.")
    exit()

#Selenium will open a browser and close once the action has been complete natively. This detatches that functionality so it stays open. 
options = Options()
options.add_experimental_option("detach", True)

# Initialize WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Navigate to website
driver.get("https://parking.crystalmountainresort.com/login/")
driver.maximize_window()

# Wait for the "Returning Users" button to be clickable and click it
try:
    # Locate the button using XPath
    button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[text()='Returning Users']"))
    )
    button.click()
    print("Clicked the 'Returning Users' button successfully!")
except Exception as e:
    print(f"Error: {e}")


# Wait for username input field and enter data
try:
    username_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Username']"))
    )
    username_input.send_keys(username)  # Replace "YourUsername" with the actual username 
    print("Entered username successfully!")
except Exception as e:
    print(f"Error entering username: {e}")

# Wait for password input field and enter data
try:
    password_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Password']"))
    )
    password_input.send_keys(password)  # Replace "YourPassword" with the actual password
    print("Entered password successfully!")
except Exception as e:
    print(f"Error entering password: {e}")

# Wait for "Sign In" button to be clickable and click it
try:
    sign_in_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[text()='Sign In']"))
    )
    sign_in_button.click()
    print("Clicked the 'Sign In' button successfully!")
except Exception as e:
    print(f"Error clicking 'Sign In': {e}")

# Optional: Pause to see the result
time.sleep(5)

try:
    dropdown = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "plate"))
    )
    select = Select(dropdown)

    # Handle license plate input
    if license_plate.strip():
        options = [option.text.strip().lower().replace(" ", "") for option in select.options]
        matched_option = None

        for option in select.options:
            if license_plate.strip().lower().replace(" ", "") in option.text.strip().lower().replace(" ", ""):
                matched_option = option.text
                break

        if matched_option:
            select.select_by_visible_text(matched_option)
            license_plate = matched_option  # Store the selected license plate
            print(f"Selected the dropdown value: {matched_option}")
        else:
            print("No matching license plate found.")
    else:
        print("No license plate entered. Here are the available options:")
        for option in select.options:
            print(option.text)
except Exception as e:
    print(f"Error selecting dropdown value: {e}")

# Wait for the "Add More Days" link and click it
try:
    add_more_days_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[text()='Add More Days' and @class='btn btn-primary']"))
    )
    add_more_days_link.click()
    print("Clicked the 'Add More Days' link successfully!")
except Exception as e:
    print(f"Error clicking 'Add More Days': {e}")


refresh_rate = 5  # Refresh every 5 seconds

while True:
    try:
        # Use starts-with to match any timestamp for the target date
        # This avoids hardcoding specific timezone offsets (T07:00, T08:00, etc.)
        calendar_day = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f"//div[starts-with(@data-date, '{date_base}')]"))
        )

        # Get the actual data-date value for logging
        actual_date = calendar_day.get_attribute("data-date")
        print(f"Found calendar element with data-date: {actual_date}")

        # Check if the date is marked as "available"
        if "fc-unavailable" not in calendar_day.get_attribute("class"):
            print(f"Date {actual_date} is available! Clicking the date...")
            calendar_day.click()  # Click on the available date
            break
        else:
            print(f"Date {actual_date} is unavailable. Refreshing the page in {refresh_rate} seconds...")
            time.sleep(refresh_rate)
            driver.refresh()
    except TimeoutException:
        print(f"Unable to locate the calendar date element for {date_base}. Retrying...")
        time.sleep(refresh_rate)  # Wait for the specified refresh rate before retrying
        driver.refresh()

# Locate and click the "Reserve Car Parking" button
try:
    reserve_button = WebDriverWait(driver, 3).until(
        EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'add2cart') and contains(., 'Reserve Car Parking')]"))
    )
    reserve_button.click()
    print("Clicked the 'Reserve Car Parking' button successfully!")
except Exception as e:
    print(f"Error clicking 'Reserve Car Parking' button: {e}")

# Bring the window to the front using JavaScript
driver.execute_script("window.focus();")

# Wait for the second dropdown to be available and select the same license plate
try:
    dropdown = WebDriverWait(driver, 3).until(
        EC.presence_of_element_located((By.ID, "plate"))
    )
    select = Select(dropdown)
    select.select_by_visible_text(license_plate)  # Use the same license plate from the first dropdown
    print("Selected the dropdown value successfully!")
except Exception as e:
    print(f"Error selecting dropdown value: {e}")


# Wait for the "Continue" button to be clickable and click it
try:
    continue_button = WebDriverWait(driver, 3).until(
        EC.element_to_be_clickable((By.ID, "btnCheckout"))
    )
    continue_button.click()
    print("Clicked the 'Continue' button successfully!")
except Exception as e:
    print(f"Error clicking 'Continue' button: {e}")

# Close browser
# driver.quit()