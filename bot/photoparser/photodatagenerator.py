from playwright.sync_api import sync_playwright
import logging
import os
from typing import Optional


# Log configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def run(playwright) -> Optional[str]:
    """Main function that returns path to downloaded Excel file"""
    browser_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    user_data_dir = os.path.join(os.getcwd(), "user_dataa")
    download_path = os.path.join(os.getcwd(), "downloads")
    os.makedirs(download_path, exist_ok=True)

    context = playwright.chromium.launch_persistent_context(
        user_data_dir=user_data_dir,
        headless=True,
        executable_path=browser_path,
        args=[
            '--disable-blink-features=AutomationControlled',
            '--disable-infobars',
            '--start-maximized'
        ],
        viewport=None,
        ignore_https_errors=True,
        downloads_path=download_path,
    )

    try:
        page = context.new_page()

        # Login process
        page.goto("https://smartup.online/login.html", wait_until="networkidle")
        page.fill('#login', 'Jamshidbek@falcon')
        page.fill('#password', '571++632')
        with page.expect_navigation(wait_until="networkidle"):
            page.click('#sign_in')

        # Handle session buttons
        max_retries = 3
        buttons = []
        for attempt in range(max_retries):
            try:
                logger.info(f"Looking for session buttons (attempt {attempt + 1})...")
                buttons = page.query_selector_all('[ng-click^="closeSession"]')
                if buttons:
                    break
            except Exception as e:
                if attempt == max_retries - 1:
                    raise

        def click_button(button, index):
            try:
                button.click()
                logger.info(f"✅ Session button {index + 1} clicked")
                return True
            except Exception as e:
                logger.warning(f"⚠️ Failed to click session button {index + 1}: {e}")
                return False

        for i, button in enumerate(buttons):
            click_button(button, i)

        page.goto(
            "https://smartup.online/#/!53rqgijui/anor/mr/product/inventory_list", 
            wait_until="networkidle"
        )

        page.wait_for_selector('.dropdown-toggle.no-after')
        page.click('.dropdown-toggle.no-after')
        page.wait_for_timeout(1000)  # sync sleep alternative

        logger.info("Clicking Excel download button...")
        with page.expect_download() as download_info:
            page.click('[ng-click="exportExcel()"]')

        download = download_info.value
        final_path = os.path.join(download_path, download.suggested_filename)
        download.save_as(final_path)
        
        import pandas as pd
        df = pd.read_excel(final_path)
        filtered_df = df[df.iloc[:, 3].notna()]
        filtered_df.to_excel(final_path, index=False)

        return final_path  

    except Exception as e:
        logger.error(f"❌ Critical error: {e}")
        page.screenshot(path='error_screenshot.png')
        logger.info("📸 Screenshot saved as error_screenshot.png")
        return None

    finally:
        context.close()

def main() -> Optional[str]:
    with sync_playwright() as playwright:
        return run(playwright)

# if __name__ == "__main__":
#     result = main()
#     if result:
#         logger.info(f"Successfully downloaded file: {result}")
#     else:
#         logger.error("Failed to download file")