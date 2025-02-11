import tensorflow as tf
from tensorflow.keras.preprocessing import image
import numpy as np
import google.generativeai as genai  # Import Google Gemini API
import os

# Set your Google Gemini API key
genai.configure(api_key="AIzaSyDGrkXQovU8ls-GOL1A-oIPSDhLBiaLeQs")

# Check GPU availability
print("Num GPUs Available:", len(tf.config.list_physical_devices('GPU')))

# Load MobileNetV3 model for efficiency
model = tf.keras.applications.MobileNetV3Small(weights='imagenet')

@tf.function
def predict_with_optimized_model(processed_image):
    return model(processed_image, training=False)

# Function to preprocess the input image
def preprocess_image(img_path):
    try:
        if not os.path.exists(img_path):
            raise FileNotFoundError(f"Error: File '{img_path}' not found.")
        img = image.load_img(img_path, target_size=(224, 224))
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = tf.keras.applications.mobilenet_v3.preprocess_input(x)
        return x
    except Exception as e:
        print(f"Image preprocessing failed: {e}")
        return None

# Function to predict the image class
def predict_image(img_path):
    processed_image = preprocess_image(img_path)
    if processed_image is None:
        return "Prediction failed due to preprocessing error."

    try:
        predictions = predict_with_optimized_model(processed_image)
        decoded_predictions = tf.keras.applications.mobilenet_v3.decode_predictions(predictions.numpy(), top=1)[0]
        print("Prediction successful.")
        return decoded_predictions[0][1]  # Return the predicted class name
    except Exception as e:
        print(f"Prediction error: {e}")
        return "Prediction error."

# Function to generate tags using Google Gemini
def generate_tags(predicted_class):
    try:
        model = genai.GenerativeModel("gemini-pro")
        prompt = f"Generate 2 most relevant tags for an image of a '{predicted_class}'."
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error generating tags: {e}")
        return "Error generating tags."

# Example usage
image_path = 'car1.jpg'
predicted_class = predict_image(image_path)
print(f"Predicted class: {predicted_class}")

if "Prediction error" not in predicted_class:
    tags = generate_tags(predicted_class)
    print(f"Generated tags: {tags}")
