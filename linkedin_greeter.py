import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException

# -----------------------------------------------------------
# LinkedIn Auto Greeting Bot
# -----------------------------------------------------------
# This script:
# 1. Opens Chrome
# 2. Lets the user log in manually (30 sec window)
# 3. Navigates to My Network → Catch up
# 4. Sends greetings automatically to all available contacts
#
# IMPORTANT:
# - Do NOT run too fast. LinkedIn bans aggressive automation.
# - This is for educational/demo purposes only.
# -----------------------------------------------------------


# -----------------------------
# CONFIGURATION
# -----------------------------
LOGIN_WAIT_TIME = 30
PAGE_LOAD_WAIT = 10
ACTION_DELAY = 3

CATCHUP_URL = "https://www.linkedin.com/mynetwork/catch-up/all/"


# -----------------------------
# XPATH SELECTORS (may change if LinkedIn updates UI)
# -----------------------------
CARD_XPATH = "//li[contains(@class, 'mn-community-summary__entity-info') or contains(@class, 'mn-person-info')]"
NAME_XPATH = ".//a[contains(@class,'mn-person-info__link')]//span[@aria-hidden='true']"
BUTTON_XPATH = ".//button[contains(@class,'artdeco-button') and not(contains(@class,'artdeco-button--muted'))]"

MESSAGE_BOX_XPATH = "//div[contains(@class,'msg-form__contenteditable')]"
SEND_BUTTON_XPATH = "//button[contains(@class,'msg-form__send-button')]"
CLOSE_BUTTON_XPATH = "//button[contains(@aria-label,'Dismiss') or contains(@aria-label,'Close')]"


# -----------------------------
# Open Chrome (no driver needed)
# -----------------------------
def open_browser():
    print("[INFO] Starting Chrome browser...")

    options = Options()
    options.add_argument("--start-maximized")

    # Selenium 4.25+ supports automatic driver download
    driver = webdriver.Chrome(options=options)
    return driver


# -----------------------------
# MAIN GREETING FUNCTION
# -----------------------------
def run_bot():
    print("\n[INFO] LinkedIn Auto Greeting Bot Starting...\n")

    driver = open_browser()
    driver.get("https://www.linkedin.com/login")

    print(f"[INFO] Please login manually. Waiting {LOGIN_WAIT_TIME} seconds...")
    time.sleep(LOGIN_WAIT_TIME)

    print("[INFO] Navigating to Catch-Up page...")
    driver.get(CATCHUP_URL)
    time.sleep(PAGE_LOAD_WAIT)

    print("[INFO] Scanning for profile cards...")
    cards = driver.find_elements(By.XPATH, CARD_XPATH)

    if not cards:
        print("[ERROR] No cards found. LinkedIn UI may have changed.")
        return

    print(f"[INFO] Found {len(cards)} items. Processing...\n")

    sent_count = 0

    for i, card in enumerate(cards, start=1):
        try:
            print(f"[INFO] Processing card {i}/{len(cards)}")

            # extract name
            try:
                name_el = card.find_element(By.XPATH, NAME_XPATH)
                name = name_el.text.strip()
            except NoSuchElementException:
                print("[WARN] Name not found. Skipping card.")
                continue

            # extract greeting button
            try:
                greet_button = card.find_element(By.XPATH, BUTTON_XPATH)
            except NoSuchElementException:
                print(f"[WARN] No greeting button found for {name}. Skipping...")
                continue

            # scroll into view
            driver.execute_script("arguments[0].scrollIntoView(true);", greet_button)
            time.sleep(1)

            # click greeting button
            try:
                greet_button.click()
            except ElementClickInterceptedException:
                print("[WARN] Click intercepted. Skipping...")
                continue

            print(f"[INFO] Opening message box for {name}")
            time.sleep(ACTION_DELAY)

            # find message box
            message_box = driver.find_element(By.XPATH, MESSAGE_BOX_XPATH)

            # append custom text
            message_box.send_keys(f" {name}!")  # simple personalization

            # send message
            send_btn = driver.find_element(By.XPATH, SEND_BUTTON_XPATH)
            send_btn.click()

            print(f"[SUCCESS] Message sent to {name}")
            sent_count += 1
            time.sleep(ACTION_DELAY)

            # close message popup
            try:
                close_btn = driver.find_element(By.XPATH, CLOSE_BUTTON_XPATH)
                close_btn.click()
            except:
                pass

            time.sleep(ACTION_DELAY)

        except Exception as e:
            print(f"[ERROR] Unexpected issue: {e}")
            continue

    print("\n--------------------------------------------------")
    print(f"[INFO] Completed. Total messages sent: {sent_count}")
    print("--------------------------------------------------")

    print("[INFO] Browser will close in 10 seconds...")
    time.sleep(10)
    driver.quit()


# -----------------------------
# Entry Point
# -----------------------------
if __name__ == "__main__":
    run_bot()
