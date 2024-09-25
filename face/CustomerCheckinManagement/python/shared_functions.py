import requests, time
from PIL import Image
from azure.core.credentials import AzureKeyCredential
from azure.ai.vision.face import FaceClient
from azure.ai.vision.face.models import FaceDetectionModel, FaceRecognitionModel, FaceAttributeTypeRecognition04, QualityForRecognition

def detect_faces(subscription_key, endpoint, image_path, injection_header=None):
    with FaceClient(endpoint, AzureKeyCredential(subscription_key), headers = {"X-MS-AZSDK-Telemetry": injection_header}) as face_client:
        with open(image_path, 'rb') as image_data:
            detected_faces = face_client.detect(
                    image_content=image_data.read(),
                    detection_model=FaceDetectionModel.DETECTION_03,
                    recognition_model=FaceRecognitionModel.RECOGNITION_04,
                    return_face_id=True,
                    return_face_attributes=[FaceAttributeTypeRecognition04.QUALITY_FOR_RECOGNITION]
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
    
def check_operation_status(subscription_key, operation_location, injection_header=None):
    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key,
        'X-MS-AZSDK-Telemetry': injection_header,
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
def add_person_face(subscription_key, endpoint, image_path, person_id, injection_header=None, quality_filter=False):
    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key,
        'Content-Type': 'application/octet-stream',
        'X-MS-AZSDK-Telemetry': injection_header
    }
    params = {
        'detectionModel': 'detection_03'
    }
        
    faces = detect_faces(subscription_key, endpoint, image_path, injection_header)
    if len(faces) == 0:
        print("No faces detected in the image.")
        return None
    else:
        if quality_filter and faces[0].face_attributes.quality_for_recognition == QualityForRecognition.LOW:
            print("Face quality is too low. Please use a different image.")
            return None

    if len(faces) > 1:
        image_width, image_height = get_image_dimensions(image_path)
        # If multiple faces are detected, use the first face (largest face) for adding to the target
        print(f"Multiple faces detected. Using the first face (largest face) for adding to the target.")
        face_rectangle = enlarge_bounding_box(faces[0]['faceRectangle'], image_width, image_height)
        params['targetFace'] = f"{face_rectangle['left']},{face_rectangle['top']},{face_rectangle['width']},{face_rectangle['height']}"
    else:
        print(f"One face detected. Adding to the target.")

    add_face_url = endpoint + f"/face/v1.1-preview.1/persons/{person_id}/recognitionModels/recognition_04/persistedFaces"
    with open(image_path, 'rb') as image_data:
        response = requests.post(add_face_url, params=params, headers=headers, data=image_data)
        if response.status_code == 202:
            operation_location = response.headers.get('Operation-Location')
            if operation_location:
                if check_operation_status(subscription_key, operation_location, injection_header):
                    persisted_face_id = response.json()['persistedFaceId']
                    return persisted_face_id
                else:
                    print ("Failed to add face.")
                    return None
            else:
                print("No Operation-Location header found in the response.")
                return None
        else:
            print(f"Failed to add face: {response.json()}")
            return None
        
# Function to create a new person
def create_person(subscription_key, endpoint, person_name = None, injection_header=None):
    create_person_url = f"{endpoint}/face/v1.1-preview.1/persons"
    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key,
        'Content-Type': 'application/json',
        'X-MS-AZSDK-Telemetry': injection_header
    }
    data = {
        "name": person_name,
    }
    try:
        response = requests.post(create_person_url, headers=headers, json=data)
        response.raise_for_status()

        if response.status_code == 202:
            operation_location = response.headers.get('Operation-Location')
            if operation_location:
                if check_operation_status(subscription_key, operation_location, injection_header):
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

# Function to delete a person
def delete_person(subscription_key, endpoint, person_id, injection_header=None):
    delete_person_url = f"{endpoint}/face/v1.1-preview.1/persons/{person_id}"
    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key,
        'X-MS-AZSDK-Telemetry': injection_header
    }
    try:
        response = requests.delete(delete_person_url, headers=headers)
        response.raise_for_status()

        if response.status_code == 202:
            operation_location = response.headers.get('Operation-Location')
            if operation_location:
                if check_operation_status(subscription_key, operation_location, injection_header):
                    return True
                else:
                    print ("Failed to delete person.")
                    return False
            else:
                print("No Operation-Location header found in the response.")
                return False
        else:
            print(f"Failed to delete person: {response.json()}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return False

# Function to identify faces in an image
def identify_faces(subscription_key, endpoint, face_id, dynamic_person_group_id=None, injection_header=None):
    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key,
        'Content-Type': 'application/json',
        'X-MS-AZSDK-Telemetry': injection_header
    }

    identify_url = endpoint + "/face/v1.1-preview.1/identify"
    body = {
        'faceIds': [face_id],
        'maxNumOfCandidatesReturned': 1,
        'confidenceThreshold': 0.5
    }

    if dynamic_person_group_id:
        body['dynamicPersonGroupId'] = dynamic_person_group_id
    else:
        body['personIds'] = '*'

    response = requests.post(identify_url, headers=headers, json=body)
    response.raise_for_status()
    results = response.json()

    if len(results) > 0:
        return results[0]['candidates'][0]['personId']
    else:
        return None

# Function to create a dynamic person group
def create_dynamic_person_group(subscription_key, endpoint, dynamic_person_group_id, injection_header=None):
    create_DPG_url = f"{endpoint}/face/v1.1-preview.1/dynamicpersongroups/{dynamic_person_group_id}"
    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key,
        'Content-Type': 'application/json',
        'X-MS-AZSDK-Telemetry': injection_header
    }
    body = {
        "name": "Example DynamicPersonGroup",
        "userData": "User defined data",
    }
    try:
        response = requests.put(create_DPG_url, headers=headers, json=body)
        response.raise_for_status()

        if response.status_code == 200:
            return True
        else:
            print(f"Failed to create dynamic person group: {response.json()}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return False

# Function to delete a dynamic person group
def delete_dynamic_person_group(subscription_key, endpoint, dynamic_person_group_id, injection_header=None):
    delete_DPG_url = f"{endpoint}/face/v1.1-preview.1/dynamicpersongroups/{dynamic_person_group_id}"
    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key,
        'X-MS-AZSDK-Telemetry': injection_header
    }
    try:
        response = requests.delete(delete_DPG_url, headers=headers)
        response.raise_for_status()

        if response.status_code == 202:
            operation_location = response.headers.get('Operation-Location')
            if operation_location:
                if check_operation_status(subscription_key, operation_location, injection_header):
                    return True
                else:
                    print ("Failed to delete dynamic person group.")
                    return False
            else:
                print("No Operation-Location header found in the response.")
                return False
        else:
            print(f"Failed to delete dynamic person group: {response.json()}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return False
    
# Function to check if a dynamic person group exists
def check_dynamic_person_group_exists(subscription_key, endpoint, dynamic_person_group_id, injection_header=None):
    check_DPG_url = f"{endpoint}/face/v1.1-preview.1/dynamicpersongroups/{dynamic_person_group_id}"
    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key,
        'X-MS-AZSDK-Telemetry': injection_header
    }
    try:
        response = requests.get(check_DPG_url, headers=headers)
        response.raise_for_status()
        if response.status_code == 200:
            return True
        else:
            print("Dynamic person group does not exist.")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return False
    
# Function to link a person to a dynamic person group
def link_person_to_dynamic_person_group(subscription_key, endpoint, dynamic_person_group_id, person_id, injection_header=None):
    link_DPG_url = f"{endpoint}/face/v1.1-preview.1/dynamicpersongroups/{dynamic_person_group_id}"
    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key,
        'Content-Type': 'application/json',
        'X-MS-AZSDK-Telemetry': injection_header
    }
    body = {
        "name": "Example DynamicPersonGroup",
        "userData": "User defined data",
        "addPersonIds": [person_id]
    }
    try:
        response = requests.patch(link_DPG_url, headers=headers, json=body)
        response.raise_for_status()

        if response.status_code == 202:
            operation_location = response.headers.get('Operation-Location')
            if operation_location:
                if check_operation_status(subscription_key, operation_location, injection_header):
                    return True
                else:
                    print ("Failed to create dynamic person group.")
                    return False
            else:
                print("No Operation-Location header found in the response.")
                return False
        else:
            print(f"Failed to create dynamic person group: {response.json()}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return False