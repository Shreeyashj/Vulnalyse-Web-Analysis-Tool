from flask import Flask, request, render_template, jsonify
import joblib
import os
from flask_cors import CORS
import logging

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Absolute paths for the model and vectorizer
model_path = r'C:\Users\DevRahul\Desktop\Automated Vurnablity Assisment tool\Cyber-Security-Hackathon-Pishing-Detection-main\phishing_model.pkl'
vectorizer_path = r'C:\Users\DevRahul\Desktop\Automated Vurnablity Assisment tool\Cyber-Security-Hackathon-Pishing-Detection-main\vectorizer.pkl'

# Check if the model and vectorizer exist
if not os.path.exists(model_path):
    logging.error(f"Model file '{model_path}' does not exist.")
    raise FileNotFoundError(f"The model file '{model_path}' does not exist.")
if not os.path.exists(vectorizer_path):
    logging.error(f"Vectorizer file '{vectorizer_path}' does not exist.")
    raise FileNotFoundError(f"The vectorizer file '{vectorizer_path}' does not exist.")

# Load the model and vectorizer with exception handling
try:
    loaded_model = joblib.load(model_path)
    vectorizer = joblib.load(vectorizer_path)
    logging.debug("Model and vectorizer loaded successfully.")
except Exception as e:
    logging.error(f"Error loading model or vectorizer: {e}")
    raise e

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        url = request.form.get('url')  # Get the URL from the form
        if not url:
            logging.error("No URL provided.")
            return render_template('result.html', prediction="No URL provided.")
        
        features = vectorizer.transform([url])  # Vectorize the input URL
        prediction = loaded_model.predict(features)  # Get model prediction
        result = "Phishing" if prediction[0].lower() == 'phishing' else "Legitimate"
        
        logging.debug(f"Prediction for URL {url}: {result}")
        return render_template('result.html', prediction=result)
    
    except Exception as e:
        logging.error(f"Error in prediction: {e}")
        return render_template('result.html', prediction="Error during prediction.")

@app.route('/check-url', methods=['POST'])
def check_url():
    try:
        data = request.get_json()  # Get URL data from the POST request
        url = data.get('url')
        if not url:
            logging.error("No URL provided in JSON.")
            return jsonify({'error': 'No URL provided.'}), 400
        
        features = vectorizer.transform([url])  # Vectorize the input URL
        prediction = loaded_model.predict(features)  # Get model prediction
        result = "Phishing" if prediction[0].lower() == 'phishing' else "Legitimate"
        
        logging.debug(f"URL checked: {url}, Result: {result}")
        return jsonify({'isPhishing': result == "Phishing"})
    
    except Exception as e:
        logging.error(f"Error checking URL: {e}")
        return jsonify({'error': 'Error during URL check.'}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)
