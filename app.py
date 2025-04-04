from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
import requests
import re

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# External API URLs
SPAM_API_URL = "https://spambackend2.onrender.com/api/check_spam"
VIRUS_SCAN_API_URL = "https://virusscanbackendtrail.onrender.com/scan"

def contains_url(message):
    """Check if the message contains a URL"""
    url_pattern = r"https?://[^\s]+"
    urls = re.findall(url_pattern, message)
    return urls  # Returns a list of URLs (empty if none)

def check_spam_text(message):
    """Send text message to Spam Detection API"""
    response = requests.post(SPAM_API_URL, json={"rawdata": message})
    if response.status_code == 200:
        return response.json().get("answer", "spam")  # Default to spam if no response
    return "spam"

def check_url_safety(url):
    """Send URL to Virus Scan API"""
    response = requests.post(VIRUS_SCAN_API_URL, json={"url": url})
    if response.status_code == 200:
        return response.json().get("status", "Spam")  # Default to Spam if no response
    return "Spam"

@app.route("/analyze", methods=["POST"])
def analyze_message():
    """Main API to analyze the message"""
    data = request.get_json()
    message = data.get("message", "")

    if not message:
        return jsonify({"error": "Message is required"}), 400

    urls = contains_url(message)

    if urls:
        # If URL exists, check both text and URL
        text_result = check_spam_text(message)
        url_result = check_url_safety(urls[0])  # Check first URL only
        final_result = "Spam" if text_result == "spam" or url_result == "Spam" else "Ham"
    else:
        # If no URL, just check the message text
        final_result = check_spam_text(message)

    return jsonify({"result": final_result})

if __name__ == "__main__":
    app.run(debug=True)
