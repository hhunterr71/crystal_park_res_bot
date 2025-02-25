import time
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

# Process the date to desired format
from datetime import datetime
try:
    date_processed = datetime.strptime(date_input, "%Y/%m/%d").strftime("%Y-%m-%dT08:00:00.000Z")
    ##print(f"Processed date: {date_processed}")
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

# Wait for the dropdown to be available and select the desired value
# try:
#     dropdown = WebDriverWait(driver, 10).until(
#         EC.presence_of_element_located((By.ID, "plate"))
#     )
#     select = Select(dropdown)
#     select.select_by_value("32831")  
#     # select.select_by_visible_text("Cgs444") #If the dropdown should be selected by visible text instead of value, you can use:
#     print("Selected the dropdown value successfully!")
# except Exception as e:
#     print(f"Error selecting dropdown value: {e}")

# Wait for the dropdown to be available and select the desired value
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

# Specify the desired date
# desired_date = "2025-02-01T08:00:00.000Z"
refresh_rate = 5  # Refresh every 5 seconds

while True:
    try:
        # Locate the calendar date element
        calendar_day = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f"//div[@data-date='{date_processed}']"))
        )
        
        # Check if the date is marked as "available"
        if "fc-unavailable" not in calendar_day.get_attribute("class"):
            print(f"Date {date_processed} is available! Clicking the date...")
            calendar_day.click()  # Click on the available date
            break
        else:
            print(f"Date {date_processed} is unavailable. Refreshing the page in {refresh_rate} seconds...")
            time.sleep(refresh_rate)
            driver.refresh()
    except TimeoutException:
        print("Unable to locate the calendar date element. Retrying...")
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


# # Close browser
# driver.quit()