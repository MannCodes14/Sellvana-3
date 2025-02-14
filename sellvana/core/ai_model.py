import torch
import os
import numpy as np
import google.generativeai as genai  # Google Gemini API
from PIL import Image

# Set your Google Gemini API key (remove this if it's public)
genai.configure(api_key="AIzaSyDGrkXQovU8ls-GOL1A-oIPSDhLBiaLeQs")

# Load the trained YOLOv5 model
model = torch.hub.load('C:\\Users\\manns\\yolov5', 'custom', path='C:\\Users\\manns\\yolov5\\runs\\train\\41_classes_model27\\weights\\best.pt', source='local')

# Function to predict image class using YOLOv5
def predict_image(img_path):
    if not os.path.exists(img_path):
        return "Error: Image not found."

    try:
        # Run inference
        results = model(img_path)
        df = results.pandas().xyxy[0]  # Get results as a Pandas DataFrame

        if df.empty:
            return "No objects detected."

        # Get the most confident detection
        predicted_class = df.iloc[0]['name']  # Extract name of the detected object
        print(f"Predicted class: {predicted_class}")
        return predicted_class
    except Exception as e:
        print(f"Prediction error: {e}")
        return "Prediction error."

# Function to generate tags using Google Gemini
def generate_tags(predicted_class):
    try:
        model = genai.GenerativeModel("gemini-pro")
        prompt = f"Generate 3 most relevant tags for an image of a that can be in the description of an ecommerce website's products'{predicted_class}'."
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error generating tags: {e}")
        return "Error generating tags."

# Example usage
image_path = 'car1.jpg'
predicted_class = predict_image(image_path)

if "Error" not in predicted_class:
    tags = generate_tags(predicted_class)
    print(f"Generated tags: {tags}")
