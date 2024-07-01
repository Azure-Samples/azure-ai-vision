# -*- coding: utf-8 -*-

import os
import requests
import io
from PIL import Image
from azure.ai.vision.face import FaceClient
from azure.ai.vision.face.models import FaceDetectionModel, FaceRecognitionModel, FaceAttributeTypeDetection03, FaceAttributeTypeRecognition04
from azure.core.credentials import AzureKeyCredential

# This key for Face API.
FACE_KEY = os.environ["FACE_API_KEY"]
# The endpoint URL for Face API.
FACE_ENDPOINT = os.environ["FACE_ENDPOINT_URL"]
# This key for Background Removal API.
BACKGROUND_API_KEY = os.environ["BACKGROUND_API_KEY"]
# The endpoint URL for Background Removal.
BACKGROUND_ENDPOINT = os.environ["BACKGROUND_ENDPOINT_URL"]
# API version for Background Removal
BACKGROUND_REMOVAL_API_VERSION = "2023-02-01-preview"
# Foreground matting mode for Background Removal API
FOREGROUND_MATTING_MODE = "foregroundMatting"
# Image url for portrait processing sample
IMAGE_URL = 'https://raw.githubusercontent.com/Azure-Samples/cognitive-services-sample-data-files/master/Face/images/detection2.jpg'
# Maximum image size
MAX_IMAGE_SIZE = 1920
# JPEG quality
JPEG_QUALITY = 95
# Detection model option
DETECTION_MODEL = FaceDetectionModel.DETECTION_03
# Recognition model option
RECO_MODEL = FaceRecognitionModel.RECOGNITION_04
# Face attribute options
FACE_ATTRIBUTES = [FaceAttributeTypeDetection03.BLUR, FaceAttributeTypeDetection03.HEAD_POSE, FaceAttributeTypeDetection03.MASK, FaceAttributeTypeRecognition04.QUALITY_FOR_RECOGNITION]
# Margin ratio on face crop
TOP_MARGIN_MAX = 0.75
BOTTOM_MARGIN_MAX = 0.75
LEFT_MARGIN_MAX = 1.5
RIGHT_MARGIN_MAX = 1.5

print("Sample code for portrait processing with Azure Face API and Background Removal API.")

# Read image from URL
response = None
try:
    response = requests.get(IMAGE_URL, stream=True)
    response.raise_for_status()
except requests.RequestException as e:
    # If the image download fails, the sample will exit.
    print(f"Image download error: {e}")
    print(f"End of the sample for portrait processing.")
    exit()

with Image.open(response.raw) as image:
    # Resize image and compress with JPEG to reduce overall latency.
    width, height = image.size   
    resized_width = width
    resized_height = height
    if width > MAX_IMAGE_SIZE or height > MAX_IMAGE_SIZE:
        if width > height:
            resized_width = min(width, MAX_IMAGE_SIZE)
            resized_height = int(height * (resized_width / width))
        else:
            resized_height = min(height, MAX_IMAGE_SIZE)
            resized_width = int(width * (resized_height / height))
    image = image.resize((resized_width, resized_height), Image.LANCZOS)
    image = image.convert('RGB') 
    image_memory_stream = io.BytesIO() 
    image.save(image_memory_stream, format='jpeg', quality=JPEG_QUALITY)

    # Detect faces in the image
    detected_faces = []
    image_memory_stream.seek(0)
    try:
        with FaceClient(endpoint=FACE_ENDPOINT, credential=AzureKeyCredential(FACE_KEY), headers={"X-MS-AZSDK-Telemetry": "sample=portrait-processing"}) as face_client:
            detected_faces = face_client.detect(
                image_memory_stream,
                detection_model=DETECTION_MODEL,
                recognition_model=RECO_MODEL,
                return_face_id=False,
                return_face_attributes=FACE_ATTRIBUTES,
                return_face_landmarks=True
            )
    except Exception as e:
        print(f"Detection error: {e}")
    image_memory_stream.close()

    # Check portrait related attributes and propose crop rectangle for background removal
    # Please note that the face attributes can be used to filter out low-quality images for portrait processing.
    number_of_faces = len(detected_faces)
    crop_left, crop_top, crop_right, crop_bottom = 0, 0, 0, 0
    print (f"Number of faces detected: {number_of_faces}")

    if number_of_faces > 0:
        # Use the first face as an example
        face = detected_faces[0]

        # Face rectangle
        face_width = face.face_rectangle.width
        face_height = face.face_rectangle.height
        face_left = face.face_rectangle.left
        face_top = face.face_rectangle.top
        print(f"Face detected: width={face_width}, height={face_height}, left={face_left}, top={face_top}")

        # Head pose
        yaw = face.face_attributes.head_pose.yaw
        pitch = face.face_attributes.head_pose.pitch
        roll = face.face_attributes.head_pose.roll
        print(f"Head pose: yaw={yaw}, pitch={pitch}, roll={roll}")

        # Quality
        quality = face.face_attributes.quality_for_recognition
        print(f"Quality: {quality}")

        # Blur
        blur_level = face.face_attributes.blur.blur_level
        blur_value = face.face_attributes.blur.value
        print(f"Blur: level={blur_level}, value={blur_value}")

        # Mask
        mask_type = face.face_attributes.mask.type
        mask_nose_and_mouth_covered = face.face_attributes.mask.nose_and_mouth_covered
        print(f"Mask: type={mask_type}, nose and mouth covered={mask_nose_and_mouth_covered}")

        # Calculate crop for background removal
        image_width, image_height = image.size
        left_margin = face_left - face_width * LEFT_MARGIN_MAX
        top_margin = face_top - face_height * TOP_MARGIN_MAX
        right_margin = face_left + face_width + face_width * RIGHT_MARGIN_MAX
        bottom_margin = face_top + face_height + face_height * BOTTOM_MARGIN_MAX

        crop_left= max(int(left_margin),0)
        crop_top = max(int(top_margin),0)
        crop_right = min(int(right_margin),image_width)
        crop_bottom = min(int(bottom_margin),image_height)
    else:
        print("No face detected.")

    if number_of_faces != 0:
        # crop the face
        image = image.crop((crop_left, crop_top, crop_right, crop_bottom))
        crop_memory_stream = io.BytesIO()
        image.save(crop_memory_stream, format='jpeg', quality=JPEG_QUALITY)
        
        # remove the background
        url = f"{BACKGROUND_ENDPOINT}computervision/imageanalysis:segment?api-version={BACKGROUND_REMOVAL_API_VERSION}&mode={FOREGROUND_MATTING_MODE}"
        headers = {
            'Content-Type': 'application/octet-stream',
            'Ocp-Apim-Subscription-Key': BACKGROUND_API_KEY
        }
        crop_memory_stream.seek(0)
        response = None
        try:
            response = requests.post(url, data=crop_memory_stream, headers=headers)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Background removal error: {e}")
        
        # merge the image with the foreground matting
        if response is not None:
            foreground_matting_image = Image.open(io.BytesIO(response.content))
            foreground_matting_image = foreground_matting_image.convert('L')
            image.putalpha(foreground_matting_image)
            image.show()
            wait = input("press ENTER to continue after viewing the portrait image.")
            foreground_matting_image.close()
        else:
            print("Background removal failed. No portrait image is generated.")

        crop_memory_stream.close()
    else:
        print("No face is detect. No portrait image is generated.")

print("End of the sample for portrait processing.")
