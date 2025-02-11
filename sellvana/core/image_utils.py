# import tensorflow as tf
# import numpy as np
# from tensorflow.keras.preprocessing import image
# from tensorflow.keras.applications.mobilenet_v3 import preprocess_input, MobileNetV3Small
# import os

# # Load the pre-trained modelly once
# model = MobileNetV3Small(weights="imagenet", include_top=False, pooling="avg")

# def extract_features(img_path):
#     if not os.path.exists(img_path):
#         return None

#     try:
#         img = image.load_img(img_path, target_size=(224, 224))
#         img_array = image.img_to_array(img)
#         img_array = np.expand_dims(img_array, axis=0)
#         img_array = preprocess_input(img_array)

#         features = model.predict(img_array)
#         return features.flatten().tolist()  # Convert to list for JSON storage
#     except Exception as e:
#         print(f"Feature extraction failed: {e}")
#         return None
