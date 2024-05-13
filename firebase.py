import cv2
import numpy as np
import firebase_admin
from firebase_admin import credentials, storage
from flask import Flask, request, jsonify
from datetime import datetime, timedelta

app = Flask(__name__)

# Initialize Firebase Admin SDK
cred = credentials.Certificate(r"C:\Users\lenovo\Downloads\joe2\key.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': 'sa3edny-b7978.appspot.com'
})

# Create a storage client
client = storage.bucket("sa3edny-b7978.appspot.com")

# Function to download image from Firebase Storage
def download_image_from_storage(image_name):
    blob = client.blob(image_name)
    image_data = blob.download_as_string()
    nparr = np.frombuffer(image_data, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return image

def detect_bands(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    bands = [cv2.boundingRect(contour) for contour in contours]
    return bands

def apply_gaussian_blur(image):
    blurred_image = cv2.GaussianBlur(image, (5, 5), 0)
    return blurred_image

def detect_bands_in_images(image1, image2):
    try:
        image1_blurred = apply_gaussian_blur(image1)
        image2_blurred = apply_gaussian_blur(image2)

        bands1 = detect_bands(image1_blurred)
        bands2 = detect_bands(image2_blurred)

        return bands1, bands2
    except Exception as e:
        print("Error:", e)
        return None, None

def calculate_matching_score(bands1, bands2):
    matched_coordinates = 0

    for band1 in bands1:
        y1, height1 = band1[1], band1[3]
        
        for band2 in bands2:
            y2, height2 = band2[1], band2[3]
            
            if abs(y1 - y2) <= 5 and abs(height1 - height2) <= 5:
                matched_coordinates += 1
                break

    matching_score = matched_coordinates / len(bands1)
    
    return matching_score

# Paths to the input images in Firebase Storage
image_name1 = "m22.png"
image_name2 = "os2.png"

# Download images from Firebase Storage
image1 = download_image_from_storage(image_name1)
image2 = download_image_from_storage(image_name2)

# Detect bands in the images


# Calculate the matching score



# Flask route to display image and calculate matching score
@app.route('/calculate_and_display_matching_score', methods=['GET'])
def calculate_and_display_matching_score():
    bands1, bands2 = detect_bands_in_images(image1, image2)
    matching_score = calculate_matching_score(bands1, bands2)
    return jsonify({'Matching Score': matching_score})

if __name__ == '__main__':
    app.run(debug=True)