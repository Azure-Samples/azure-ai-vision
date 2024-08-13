from PIL import Image
from azure.core.credentials import AzureKeyCredential
from azure.ai.vision.face import FaceClient
from azure.ai.vision.face.models import FaceDetectionModel, FaceRecognitionModel

def detect_faces(subscription_key, endpoint, image_path, injection_header=None):
    with FaceClient(endpoint, AzureKeyCredential(subscription_key), headers = {"X-MS-AZSDK-Telemetry": injection_header}) as face_client:
        with open(image_path, 'rb') as image_data:
            detected_faces = face_client.detect(
                    image_content=image_data.read(),
                    detection_model=FaceDetectionModel.DETECTION_03,
                    recognition_model=FaceRecognitionModel.RECOGNITION_04,
                    return_face_id=True,
                )
        return detected_faces
    
def enlarge_bounding_box(face_rectangle, image_width, image_height, enlargement_factor=1.2):
    left = max(0, face_rectangle['left'] - (face_rectangle['width'] * (enlargement_factor - 1) / 2))
    top = max(0, face_rectangle['top'] - (face_rectangle['height'] * (enlargement_factor - 1) / 2))
    width = min(image_width - left, face_rectangle['width'] * enlargement_factor)
    height = min(image_height - top, face_rectangle['height'] * enlargement_factor)
    return {'left': int(left), 'top': int(top), 'width': int(width), 'height': int(height)}

def get_image_dimensions(image_path):
    with Image.open(image_path) as img:
        return img.width, img.height