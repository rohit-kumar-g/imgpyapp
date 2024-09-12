from flask import Flask, jsonify
from tasks import fetch_new_data  # Ensure this import is correct
import os
import json

app = Flask(__name__)

# Configuration
app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379/0',
    CELERY_RESULT_BACKEND='redis://localhost:6379/0'
)

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

if __name__ == '__main__':
    app.run(debug=True)
