import requests, time
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
    
def check_operation_status(subscription_key, operation_location):
    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key,
        'X-MS-AZSDK-Telemetry': 'sample=enroll-faces-person-directory'
    }
    
    while True:
        response = requests.get(operation_location, headers=headers)
        response.raise_for_status()
        
        status = response.json()
        if status.get('status') in ['succeeded', 'failed']:
            if status.get('status') == 'succeeded':
                return True
            else:
                return False
        
        time.sleep(5) 

# Function to add face to a person    
def add_person_face(subscription_key, endpoint, image_path, person_id, injection_header=None):
    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key,
        'Content-Type': 'application/octet-stream',
        'X-MS-AZSDK-Telemetry': injection_header
    }
    params = {
        'detectionModel': 'detection_03'
    }
        
    faces = detect_faces(subscription_key, endpoint, image_path)
    if len(faces) == 0:
        return "No faces detected in the image."
    elif len(faces) > 1:
        image_width, image_height = get_image_dimensions(image_path)
        # If multiple faces are detected, use the first face (largest face) for adding to the target
        print(f"Multiple faces detected. Using the first face (largest face) for adding to the target.")
        face_rectangle = enlarge_bounding_box(faces[0]['faceRectangle'], image_width, image_height)
        params['targetFace'] = f"{face_rectangle['left']},{face_rectangle['top']},{face_rectangle['width']},{face_rectangle['height']}"
    else:
        print(f"One face detected. Adding to the target.")

    add_face_url = endpoint + f"/face/v1.0-preview/persons/{person_id}/recognitionModels/recognition_04/persistedFaces"
    with open(image_path, 'rb') as image_data:
        response = requests.post(add_face_url, params=params, headers=headers, data=image_data)
        if response.status_code == 202:
            operation_location = response.headers.get('Operation-Location')
            if operation_location:
                if check_operation_status(subscription_key, operation_location):
                    persisted_face_id = response.json()['persistedFaceId']
                    return persisted_face_id
                else:
                    return "Failed to add face."
            else:
                print("No Operation-Location header found in the response.")
        else:
            return f"Failed to add face: {response.json()}"
        
# Function to create a new person
def create_person(subscription_key, endpoint, person_name, injection_header=None):
    url = f"{endpoint}/face/v1.1-preview.1/persons"
    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key,
        'Content-Type': 'application/json',
        'X-MS-AZSDK-Telemetry': injection_header
    }
    data = {
        "name": person_name,
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()

        if response.status_code == 202:
            operation_location = response.headers.get('Operation-Location')
            if operation_location:
                if check_operation_status(subscription_key, operation_location):
                    person_id = response.json()['personId']
                    return person_id
                else:
                    print ("Failed to create person.")
                    return None
            else:
                print("No Operation-Location header found in the response.")
                return None
        else:
            print(f"Failed to create person: {response.json()}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

# Function to identify faces in an image
def identify_faces(subscription_key, endpoint, image_path, person_ids, injection_header=None):
    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key,
        'Content-Type': 'application/octet-stream',
        'X-MS-AZSDK-Telemetry': injection_header
    }
    faces = detect_faces(subscription_key, endpoint, image_path)
    if len(faces) > 0:
        face_id = faces[0]['faceId']
    else:
        print("No faces detected in the image.")
        return
    
    identify_url = endpoint + "/face/v1.0-preview/identify"
    headers['Content-Type'] = 'application/json'
    body = {
        'faceIds': [face_id],
        'personIds': person_ids,
        'maxNumOfCandidatesReturned': 1,
        'confidenceThreshold': 0.5
    }
    response = requests.post(identify_url, headers=headers, json=body)
    response.raise_for_status()
    results = response.json()
    for i, result in enumerate(results):
        if len(result['candidates']) > 0:
            candidate = result['candidates'][0]
            person_id = candidate['personId']
            confidence = candidate['confidence']
            print(f"Face {i+1} identified as person_id: {person_id} with confidence: {confidence}")
        else:
            print(f"Face {i+1} not identified.")