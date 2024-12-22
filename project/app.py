from flask import Flask, jsonify, send_file
from apscheduler.schedulers.background import BackgroundScheduler
from scraper import scrape_properties
import os

app = Flask(__name__)

# Directory to store the Excel files
DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Variable to store the latest generated file
latest_file = None

# Function to update the latest file
def scheduled_scraping():
    global latest_file
    latest_file = scrape_properties()
    print(f"Excel file generated: {latest_file}")

# Scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(scheduled_scraping, "cron", hour=0, minute=0)  # Run daily at midnight
scheduler.start()

# API Endpoint to Download the Latest Excel File
@app.route("/download", methods=["GET"])
def download_excel():
    global latest_file
    if latest_file and os.path.exists(latest_file):
        return send_file(latest_file, as_attachment=True)
    return jsonify({"error": "No file available"}), 404

# API Endpoint to Check Status
@app.route("/status", methods=["GET"])
def status():
    return jsonify({"status": "running", "latest_file": latest_file})

# API Endpoint to Manually Run the Scraper
@app.route("/run-scraper", methods=["POST"])
def run_scraper():
    global latest_file
    try:
        latest_file = scrape_properties()
        return jsonify({"message": "Scraper executed successfully", "file": latest_file}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Main entry point
if __name__ == "__main__":
    app.run(debug=True)
