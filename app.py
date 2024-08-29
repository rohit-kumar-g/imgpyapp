from flask import Flask, render_template, request, url_for, jsonify
from PIL import Image, ImageDraw, ImageFont
import os
import random

app = Flask(__name__)

# Directory to save images
IMAGE_SAVE_DIR = os.path.join(os.path.dirname(__file__), 'static', 'images')

# Ensure the directory exists
if not os.path.exists(IMAGE_SAVE_DIR):
    os.makedirs(IMAGE_SAVE_DIR)

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

if __name__ == '__main__':
    app.run(debug=True)
