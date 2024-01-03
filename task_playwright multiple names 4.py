import asyncio
import json
from playwright.async_api import async_playwright
import logging
import os

# Read login details from JSON file
with open("C:\SHABARINATH\SD\multiple.json") as f:
    credentials = json.load(f)
    login_url = credentials.get('login_url')
    username = credentials.get('username')
    password = credentials.get('password')
    search_parameters = credentials.get('search_parameter')

# Set the desired viewport size
viewport_size = {'width': 1920, 'height': 1080}

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def handle_download(download, search_parameter):
    # Create a subdirectory for each search parameter
    download_directory = os.path.abspath(f'./{search_parameter}')
    os.makedirs(download_directory, exist_ok=True)

    # Specify the path where you want to save the downloaded file
    file_path = os.path.join(download_directory, download.suggested_filename)
    await download.save_as(file_path)
    logger.info(f"File downloaded to: {file_path}")

async def main():
    async with async_playwright() as p:
        # Launch the browser in non-headless mode
        browser = await p.chromium.launch(headless=False)

        # Create a new browser context
        context = await browser.new_context()

        try:
            # Open a new page
            page = await context.new_page()

            # Intercept download events
            for search_parameter in search_parameters:
                page.on('download', lambda download: handle_download(download, search_parameter))

            # Set the viewport size
            await page.set_viewport_size(viewport_size)

            # Navigate to the login page
            await page.goto(login_url)

            # Fill in the login form fields
            await page.fill('input[name="username"]', username)
            await page.fill('input[name="password"]', password)

            # Click the submit button
            await page.click('//button[@type="submit"]')

            # Wait for the dashboard URL to be present in the current URL
            await page.wait_for_url('dashboard', timeout=10000)

            for search_parameter in search_parameters:
                # Click on the "Candidate Search" link
                await page.click('text=Candidate Search')

                # Fill in the input field for the "Candidate Name/Email"
                await page.fill('input[name="candidateName"]', search_parameter)

                # Click the search button using Playwright's wait functionality
                await page.click('button:has-text("Search")')

                # Wait for a brief moment to allow the page to update
                await asyncio.sleep(1)

                # Get all buttons with the specified class
                download_buttons = await page.query_selector_all('//button[contains(@class, "MuiButtonBase-root MuiIconButton-root MuiIconButton-sizeMedium css-1yxmbwk")]')

                # Iterate over each button and click
                for index, button in enumerate(download_buttons, start=1):
                    # Click on the button
                    await button.click()

                    # Wait for a brief moment to allow the page to update
                    await asyncio.sleep(1)

                    # You can print or log information about the clicked button
                    print(f"Clicked button {index} with class css-1yxmbwk for search parameter: {search_parameter}")

        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
        finally:
            # Close the browser context
            await context.close()

# Run the main function
asyncio.run(main())
