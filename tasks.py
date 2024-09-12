from celery import Celery
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import json
import os

# Path to ChromeDriver
CHROMEDRIVER_PATH = 'chromedriver.exe'
RESULTS_FILE = 'results.json'

# Set up Chrome options for headless mode
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Initialize Celery
celery = Celery('tasks', broker='redis://localhost:6379/0')

@celery.task
def fetch_new_data():
    # Initialize Chrome WebDriver in headless mode
    driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=chrome_options)

    # URL of the YouTube search results page
    url = "https://www.youtube.com/results?search_query=how+to+4000+watch+time"

    # Open the URL
    driver.get(url)

    # Wait for elements to load (increase if necessary)
    driver.implicitly_wait(10)

    # Find all elements with the tag 'yt-formatted-string'
    yt_formatted_strings = driver.find_elements(By.TAG_NAME, 'yt-formatted-string')

    # Extract the text from each 'yt-formatted-string' element
    scraped_texts = [element.text for element in yt_formatted_strings]

    # Close the WebDriver
    driver.quit()

    # Save the new results to the file
    with open(RESULTS_FILE, 'w', encoding='utf-8') as file:
        json.dump(scraped_texts, file, ensure_ascii=False, indent=4)
