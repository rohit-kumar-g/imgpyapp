from flask import Flask, render_template, request, url_for, jsonify
from PIL import Image, ImageDraw, ImageFont
import os
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import json
import os
from celery_config import make_celery
from celery import Celery

app = Flask(__name__)

# Directory to save images
IMAGE_SAVE_DIR = os.path.join(os.path.dirname(__file__), 'static', 'images')

# Ensure the directory exists
if not os.path.exists(IMAGE_SAVE_DIR):
    os.makedirs(IMAGE_SAVE_DIR)

@app.route('/')
def home():
    return "Welcome to the homepage!"

@app.route('/about')
def about():
    return "About page"

@app.route('/contact')
def contact():
    return "Contact page"

@app.route('/img', methods=['GET', 'POST'])
def index():

    def delete_files_in_folder(folder_path):
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)

    # Delete existing images before creating a new one
    delete_files_in_folder(IMAGE_SAVE_DIR)

    if request.method == 'POST':
        company = request.form['company']
        job = request.form['job']
        type_ = request.form['type']

        # Define image dimensions
        width, height = 1080, 1920

        # Load background images
        img_folder = os.path.join(os.path.dirname(__file__), 'img')
        background_images = [f for f in os.listdir(img_folder) if f.endswith('.png')]
        if not background_images:
            return jsonify({"message": "No background images found in the img folder."}), 500

        # Choose a random background image
        background_image_path = os.path.join(img_folder, random.choice(background_images))

        try:
            background_img = Image.open(background_image_path).resize((width, height))
        except IOError:
            return jsonify({"message": "Error loading background image."}), 500

        # Create a copy of the background image for editing
        img = background_img.copy()

        # Draw rectangle for text area with a border
        draw = ImageDraw.Draw(img)
        text_area_x, text_area_y = 50, 50
        text_area_width, text_area_height = 980, 1820
        draw.rectangle([(text_area_x, text_area_y), (text_area_x + text_area_width, text_area_y + text_area_height)], outline=(255, 253, 208), width=10)  # Border color

        # Load a stylish font
        font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'Roboto-Regular.ttf')

        def get_dynamic_font(text, max_width, max_font_size=72, min_font_size=20):
            try:
                font = ImageFont.truetype(font_path, max_font_size)
            except IOError:
                return jsonify({"message": "Font file not found."}), 500

            font_size = max_font_size
            while font_size > min_font_size:
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                if text_width <= max_width:
                    return font
                font_size -= 2
                font = ImageFont.truetype(font_path, font_size)
            return font  # Return the smallest font if none fits

        # Maximum allowed width for text areas
        max_text_width = 720

        # Draw first text (Company) at center
        font = get_dynamic_font(company, max_text_width)
        company_size = draw.textbbox((0, 0), company, font=font)[2:]
        company_x = (width - company_size[0]) / 2
        draw.text((company_x, 910), f"{company}", fill=(41, 48 ,66), font=font)

        # Draw second text (Job) at center
        font = get_dynamic_font(job, max_text_width)
        job_size = draw.textbbox((0, 0), job, font=font)[2:]
        job_x = (width - job_size[0]) / 2
        draw.text((job_x, 1060), f"{job}", fill=(41, 48 ,66), font=font)

        # Draw third text (Type) at center
        font = get_dynamic_font(type_, max_text_width)
        type_size = draw.textbbox((0, 0), type_, font=font)[2:]
        type_x = (width - type_size[0]) / 2
        draw.text((type_x, 1230), f"{type_}", fill=(41, 48, 66), font=font)

        # Save the image to the server
        image_filename = f'thumbnail_{random.randint(10000, 99999)}.png'  # Generate a random filename
        image_path = os.path.join(IMAGE_SAVE_DIR, image_filename)
        img.save(image_path)

        # Generate the download link for the saved image
        download_url = url_for('static', filename=f'images/{image_filename}', _external=True)

        # Return the download link and status message
        return jsonify({
            "message": "Image created successfully.",
            "status": 200,
            "download_link": download_url
        }), 200

    return render_template('index.html')




# # Set up Chrome options for headless mode
# chrome_options = Options()
# chrome_options.add_argument("--headless")
# chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--disable-dev-shm-usage")

# # Path to ChromeDriver
# CHROMEDRIVER_PATH = 'chromedriver.exe'

# @app.route('/getitems', methods=['GET'])
# def get_items():
#     # Initialize Chrome WebDriver in headless mode
#     driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=chrome_options)

#     # URL of the YouTube search results page
#     url = "https://www.youtube.com/results?search_query=how+to+4000+watch+time"

#     # Open the URL
#     driver.get(url)

#     # Wait for elements to load (increase if necessary)
#     driver.implicitly_wait(10)

#     # Find all elements with the tag 'yt-formatted-string'
#     yt_formatted_strings = driver.find_elements(By.TAG_NAME, 'yt-formatted-string')

#     # Extract the text from each 'yt-formatted-string' element
#     scraped_texts = [element.text for element in yt_formatted_strings]

#     # Close the WebDriver
#     driver.quit()

#     # Return the result as JSON
#     return jsonify(scraped_texts)






# # Configuration
# app.config.update(
#     CELERY_BROKER_URL='redis://localhost:6379/0',
#     CELERY_RESULT_BACKEND='redis://localhost:6379/0'
# )

# # Initialize Celery
# celery = make_celery(app)

# # Set up Chrome options for headless mode
# chrome_options = Options()
# chrome_options.add_argument("--headless")
# chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--disable-dev-shm-usage")

# # Path to ChromeDriver
# CHROMEDRIVER_PATH = 'chromedriver.exe'

# # File to store the last result
# RESULTS_FILE = 'results.json'

# @app.route('/getitemsttt', methods=['GET'])
# def get_itemsttt():
#     # Check if results file exists and read the previous results
#     if os.path.exists(RESULTS_FILE):
#         with open(RESULTS_FILE, 'r', encoding='utf-8') as file:
#             old_results = json.load(file)
#     else:
#         old_results = []

#     # Trigger the background task to fetch new data
#     fetch_new_data.delay()

#     # Return the old result immediately
#     return jsonify({'old_results': old_results})


    # #####################################

# @celery.task
# def fetch_new_data():
#     # Initialize Chrome WebDriver in headless mode
#     driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH), options=chrome_options)

#     # URL of the YouTube search results page
#     url = "https://www.youtube.com/results?search_query=how+to+4000+watch+time"

#     # Open the URL
#     driver.get(url)

#     # Wait for elements to load (increase if necessary)
#     driver.implicitly_wait(10)

#     # Find all elements with the tag 'yt-formatted-string'
#     yt_formatted_strings = driver.find_elements(By.TAG_NAME, 'yt-formatted-string')

#     # Extract the text from each 'yt-formatted-string' element
#     scraped_texts = [element.text for element in yt_formatted_strings]

#     # Close the WebDriver
#     driver.quit()

#     # Save the new results to the file
#     with open(RESULTS_FILE, 'w', encoding='utf-8') as file:
#         json.dump(scraped_texts, file, ensure_ascii=False, indent=4)



# from flask import Flask, jsonify
from task import fetch_new_data  # Import the Celery task

# app = Flask(__name__)

# Configuration
app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379/0',
    CELERY_RESULT_BACKEND='redis://localhost:6379/0'
)

# Define a route that triggers the task
@app.route('/getitems', methods=['GET'])
def get_items():
    # Check if results file exists and read the previous results
    if os.path.exists('results.json'):
        with open('results.json', 'r', encoding='utf-8') as file:
            old_results = json.load(file)
    else:
        old_results = []

    # Trigger the background task to fetch new data
    fetch_new_data.delay()

    # Return the old result immediately
    return jsonify({'old_results': old_results})

# if __name__ == '__main__':
#     app.run(debug=True)




if __name__ == '__main__':
    app.run(debug=True)
