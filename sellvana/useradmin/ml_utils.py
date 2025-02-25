import torch
import torchvision.transforms as transforms
from torchvision import models
from PIL import Image
import google.generativeai as genai

# Configure Google Gemini API
genai.configure(api_key="AIzaSyDGrkXQovU8ls-GOL1A-oIPSDhLBiaLeQs")

# Load the pre-trained MobileNetV3 model
model = models.mobilenet_v3_large(pretrained=True)
model.eval()  # Set to evaluation mode

# Load ImageNet class labels
with open("C:\\Imp\\TYproject\\sellvana\\core\\imagenet_classes.txt", "r") as f:
    imagenet_classes = [line.strip() for line in f.readlines()]

# Image preprocessing
def preprocess_image(img_path):
    transform = transforms.Compose([
        transforms.Resize((224, 224)),  # Resize to MobileNetV3 input size
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    img = Image.open(img_path).convert("RGB")
    img = transform(img).unsqueeze(0)  # Add batch dimension
    return img

# Function to predict image class using MobileNetV3
def predict_image(img_path):
    try:
        img = preprocess_image(img_path)
        with torch.no_grad():
            outputs = model(img)  # Get predictions
            _, predicted_idx = torch.max(outputs, 1)  # Get the highest confidence index
            predicted_class = imagenet_classes[predicted_idx.item()]
            return predicted_class
    except Exception as e:
        return f"Prediction error: {e}"

# Function to generate tags using Google Gemini
def generate_tags(predicted_class):
    try:
        model = genai.GenerativeModel("gemini-pro")
        prompt = f"Generate 7 highly relevant one-word tags for an image of '{predicted_class}' that can be used in an eCommerce website's product description and tags. The first tag must be exactly '{predicted_class}', and the rest should be descriptive keywords."
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error generating tags: {e}"
    

def match_category_gemini(predicted_class, all_categories):
    try:
        # Convert category list to a readable format
        category_list = ", ".join(all_categories)

        prompt = f"""
        I have a predicted product class: "{predicted_class}".  
        Below is a list of available categories in my database:  
        {category_list}  

        Your task is to analyze the predicted product class and find the most relevant category from the given list.  
        The category should be the best possible match based on meaning and relevance.  

        Respond with only the category name that matches best. If no match is found, respond with "No matching category".
        """

        # Call Gemini API
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)

        # Extract the category name
        best_match = response.text.strip()
        return best_match if best_match else "No matching category"
    except Exception as e:
        return f"Error matching category: {e}"
    

def generate_description_gemini(predicted_class, tags_str):
    try:
        

        prompt = f"""
        Generate a compelling, SEO-friendly product description for a "{predicted_class}" to maximize visibility in an eCommerce platform.  
        - Highlight its **key features, benefits, and best use cases**.  
        - Ensure it's **engaging, persuasive, and optimized for recommendations**.  
        - Seamlessly incorporate the following relevant keywords: {tags_str}.  
        - Keep it concise (around 2-3 sentences) but **informative and appealing**.  
        - Avoid generic phrases; **make it unique and stand out**.  

        Respond with only the description text and nothing else.
        """

        # Call Gemini API
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)

        # Extract the category name
        description = response.text.strip()
        return description if description else "No description generated"
    except Exception as e:
        return f"Error generating description: {e}"