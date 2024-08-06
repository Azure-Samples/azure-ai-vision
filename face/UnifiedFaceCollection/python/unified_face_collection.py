import requests
import sys
import os
import time
import json

project_root = os.path.abspath(os.path.join(os.getcwd(), "../../"))
if project_root not in sys.path:
    sys.path.append(project_root)
from PersonDirectoryOperations.python.shared_functions import detect_faces, enlarge_bounding_box, get_image_dimensions

class UnifiedFaceCollection:
    def __init__(self, subscription_key, endpoint, face_collection_id, injection_header):
        self.subscription_key = subscription_key
        self.endpoint = endpoint
        self.face_api_url = f"{self.endpoint}/face/v1.0"
        self.face_collection_id = face_collection_id
        self.large_face_list_id = face_collection_id + "_face_list"
        self.large_person_group_id = face_collection_id + "_person_group"
        self.injection_header = injection_header
        self.headers = {
            'Ocp-Apim-Subscription-Key': self.subscription_key,
            'Content-Type': 'application/json',
            'X-MS-AZSDK-Telemetry': injection_header
        }
        self.create_collections()

    def create_collections(self):
        # Create Large Face List
        face_list_url = f"{self.face_api_url}/largefacelists/{self.large_face_list_id}"
        face_list_response = requests.put(face_list_url, headers=self.headers, json={"name": self.face_collection_id + " Face List", "recognitionModel": "recognition_04"})
        if face_list_response.status_code == 200:
            print(f"Face list {self.large_face_list_id} created successfully.")
        else:
            print(face_list_response.json())
        
        # Create Large Person Group
        person_group_url = f"{self.face_api_url}/largepersongroups/{self.large_person_group_id}"
        person_group_response = requests.put(person_group_url, headers=self.headers, json={"name": self.face_collection_id + " Person Group", "recognitionModel": "recognition_04"})
        if person_group_response.status_code == 200:
            print(f"Person group {self.large_person_group_id} created successfully.")
        else:
            print(person_group_response.json())

    def add_face(self, image_path, person_name=None):
        add_face_headers = {
            'Ocp-Apim-Subscription-Key': self.subscription_key,
            'Content-Type': 'application/octet-stream',
            'X-MS-AZSDK-Telemetry': self.injection_header
        }
        params = {
            'detectionModel': 'detection_03'
        }
        
        faces = detect_faces(self.subscription_key, self.endpoint, image_path, self.injection_header)
        if len(faces) == 0:
            return "No faces detected in the image."
        elif len(faces) > 1:
            image_width, image_height = get_image_dimensions(image_path)
            print(f"Multiple faces detected. Using the first face (largest face) for adding to the collection.")
            face_rectangle = enlarge_bounding_box(faces[0]['faceRectangle'], image_width, image_height)
            params['targetFace'] = f"{face_rectangle['left']},{face_rectangle['top']},{face_rectangle['width']},{face_rectangle['height']}"
        else:
            print(f"One face detected. Adding to the collection.")
        
        # Add face to Large Face List
        face_list_url = f"{self.face_api_url}/largefacelists/{self.large_face_list_id}/persistedfaces"
        with open(image_path, 'rb') as image:
            face_list_response = requests.post(face_list_url, params=params, headers=add_face_headers, data=image)
            if face_list_response.status_code != 200:
                return []
        face_list_result = face_list_response.json()
        persisted_face_id = face_list_result['persistedFaceId']

        if person_name:
            # Check if person exists
            person = self.get_person_by_name(person_name)
            if person is None:
                # Create a new person if not exists
                person = self.create_person(person_name)
            person_id = person['personId']

            # Add face to the created or existing person
            with open(image_path, 'rb') as image:
                person_face_url = f"{self.face_api_url}/largepersongroups/{self.large_person_group_id}/persons/{person['personId']}/persistedfaces"
                person_face_response = requests.post(person_face_url, params=params, headers=add_face_headers, data=image)
            
            if person_face_response.status_code == 200:
                person_face_result = person_face_response.json()
                person_persisted_face_id = person_face_result['persistedFaceId']
                # Update the userData field with the mapping in the Large Face List
                user_data_face_list = {
                    "personId": person_id,
                    "personPersistedFaceId": person_persisted_face_id
                }
                user_data_face_list_json = json.dumps(user_data_face_list)

                update_url_face_list = f"{self.face_api_url}/largefacelists/{self.large_face_list_id}/persistedfaces/{persisted_face_id}"
                update_body_face_list = {
                    "userData": user_data_face_list_json
                }
                update_response_face_list = requests.patch(update_url_face_list, headers=self.headers, json=update_body_face_list)
                if update_response_face_list.status_code != 200:
                    print("Failed to update userData for the face in the Large Face List.")
                    return []

                # Update the userData field with the mapping in the Large Person Group
                user_data_large_person_group = {
                    "persistedFaceId": persisted_face_id
                }
                user_data_large_person_group_json = json.dumps(user_data_large_person_group)

                update_url_large_person_group = f"{self.face_api_url}/largepersongroups/{self.large_person_group_id}/persons/{person_id}/persistedfaces/{person_persisted_face_id}"
                update_body_large_person_group = {
                    "userData": user_data_large_person_group_json
                }
                update_response_large_person_group = requests.patch(update_url_large_person_group, headers=self.headers, json=update_body_large_person_group)
                if update_response_large_person_group.status_code != 200:
                    print("Failed to update userData for the face in the Large Person Group.")
                    return []

                return {
                    "face_list": {
                        "persistedFaceId": persisted_face_id,
                    },
                    "person_group": {
                        "personId": person_id,
                    }
                }
            else:
                return []
        
        return {"face_list": { "persistedFaceId": face_list_result['persistedFaceId'] }}

    def remove_face(self, persisted_face_id):
        face_list_url = f"{self.face_api_url}/largefacelists/{self.large_face_list_id}/persistedfaces/{persisted_face_id}"
        face_list_response = requests.get(face_list_url, headers=self.headers)
        if face_list_response.status_code != 200:
            return False

        face_data = face_list_response.json()
        user_data = face_data.get("userData")
        if not user_data:
            return False

        user_data_dict = json.loads(user_data)
        person_id = user_data_dict.get("personId")
        person_persisted_face_id = user_data_dict.get("personPersistedFaceId")

        if person_id and person_persisted_face_id:
            # Remove face from Large Person Group
            person_face_url = f"{self.face_api_url}/largepersongroups/{self.large_person_group_id}/persons/{person_id}/persistedfaces/{person_persisted_face_id}"
            person_face_response = requests.delete(person_face_url, headers=self.headers)
            if person_face_response.status_code != 200:
                return False

        # Remove face from Large Face List
        face_list_delete_response = requests.delete(face_list_url, headers=self.headers)
        if face_list_delete_response.status_code != 200:
            return False

        return True

    def remove_person(self, person_identifier):
        # Determine if the identifier is a name or an ID
        person_id = None
        if isinstance(person_identifier, str) and len(person_identifier) == 36:
            person_id = person_identifier
        else:
            person = self.get_person_by_name(person_identifier)
            if person:
                person_id = person['personId']
            else:
                return False

        # Retrieve the person's faces from the person group
        person_faces_url = f"{self.face_api_url}/largepersongroups/{self.large_person_group_id}/persons/{person_id}"
        person_faces_response = requests.get(person_faces_url, headers=self.headers)
        if person_faces_response.status_code != 200:
            return False

        person_faces = person_faces_response.json()

        # Update userData in the Large Face List
        for person_persisted_face_id in person_faces['persistedFaceIds']:
            # Retrieve userData from the face in the person group
            person_face_url = f"{self.face_api_url}/largepersongroups/{self.large_person_group_id}/persons/{person_id}/persistedfaces/{person_persisted_face_id}"
            person_face_response = requests.get(person_face_url, headers=self.headers)
            if person_face_response.status_code != 200:
                continue

            face_data = person_face_response.json()
            user_data = face_data.get("userData")
            if user_data:
                user_data_dict = json.loads(user_data)
                persisted_face_id = user_data_dict.get("persistedFaceId")

                # Update userData for the face in the Large Face List
                face_list_face_url = f"{self.face_api_url}/largefacelists/{self.large_face_list_id}/persistedfaces/{persisted_face_id}"
                user_data_face_list = {
                    "personId": None,
                    "personPersistedFaceId": None
                }
                user_data_face_list_json = json.dumps(user_data_face_list)
                update_body_face_list = {
                    "userData": user_data_face_list_json
                }
                update_response_face_list = requests.patch(face_list_face_url, headers=self.headers, json=update_body_face_list)
                if update_response_face_list.status_code != 200:
                    print("Failed to update userData for the face in the Large Face List.")
                    return False

        # Remove the person from the person group
        delete_person_url = f"{self.face_api_url}/largepersongroups/{self.large_person_group_id}/persons/{person_id}"
        delete_person_response = requests.delete(delete_person_url, headers=self.headers)

        if delete_person_response.status_code != 200:
            return False

        return True

    def create_person(self, person_name):
        person_group_url = f"{self.face_api_url}/largepersongroups/{self.large_person_group_id}/persons"
        person_response = requests.post(person_group_url, headers=self.headers, json={"name": person_name})
        return person_response.json()

    def get_person_by_name(self, person_name):
        persons_url = f"{self.face_api_url}/largepersongroups/{self.large_person_group_id}/persons"
        persons_response = requests.get(persons_url, headers=self.headers)
        persons = persons_response.json()
        for person in persons:
            if person['name'] == person_name:
                return person
        return None

    def train(self):
        # Train the Large Face List
        face_list_train_url = f"{self.face_api_url}/largefacelists/{self.large_face_list_id}/train"
        face_list_train_response = requests.post(face_list_train_url, headers=self.headers)
        
        if face_list_train_response.status_code != 202:
            print("Failed to initiate training for Large Face List")
            return False

        # Train the Large Person Group
        person_group_train_url = f"{self.face_api_url}/largepersongroups/{self.large_person_group_id}/train"
        person_group_train_response = requests.post(person_group_train_url, headers=self.headers)
        
        if person_group_train_response.status_code != 202:
            print("Failed to initiate training for Large Person Group")
            return False

        # Check training status for Large Face List
        face_list_status_url = f"{self.face_api_url}/largefacelists/{self.large_face_list_id}/training"
        while True:
            face_list_status_response = requests.get(face_list_status_url, headers=self.headers)
            face_list_status = face_list_status_response.json()
            if face_list_status['status'] == 'succeeded':
                break
            elif face_list_status['status'] == 'failed':
                print("Large Face List training failed")
                return False
            time.sleep(1)
        
        # Check training status for Large Person Group
        person_group_status_url = f"{self.face_api_url}/largepersongroups/{self.large_person_group_id}/training"
        while True:
            person_group_status_response = requests.get(person_group_status_url, headers=self.headers)
            person_group_status = person_group_status_response.json()
            if person_group_status['status'] == 'succeeded':
                break
            elif person_group_status['status'] == 'failed':
                print("Large Person Group training failed")
                return False
            time.sleep(1)
        
        return True

    def find_face(self, image_path, search_type='face'):
        # Detect face in the image
        detected_faces = detect_faces(self.subscription_key, self.endpoint, image_path, self.injection_header)
        face_ids = [face['faceId'] for face in detected_faces]
        if not face_ids:
            return []

        normalized_results = []
        if search_type == 'person':
            # Find similar persons in the Large Person Group
            identify_url = f"{self.face_api_url}/identify"
            identify_data = {
                'faceId': face_ids[0],
                'largePersonGroupId': self.large_person_group_id,
                'maxNumOfCandidatesReturned': 10,
            }
            identify_response = requests.post(identify_url, headers=self.headers, json=identify_data)
            if identify_response.status_code == 200:
                results = identify_response.json()
                for result in results:
                    for candidate in result.get('candidates', []):
                        normalized_results.append({
                            'personId': candidate['personId'],
                            'confidence': candidate['confidence']
                        })
                return normalized_results
            else:
                return []
        else:
            # Find similar faces in the Large Face List
            similar_faces_url = f"{self.face_api_url}/findsimilars"
            similar_faces_data = {
                'faceId': face_ids[0],
                'largeFaceListId': self.large_face_list_id,
                'maxNumOfCandidatesReturned': 10,
            }
            similar_faces_response = requests.post(similar_faces_url, headers=self.headers, json=similar_faces_data)
            if similar_faces_response.status_code == 200:
                results = similar_faces_response.json()
                for result in results:
                    normalized_results.append({
                        'faceId': result['persistedFaceId'],
                        'confidence': result['confidence']
                    })
                return normalized_results
            else:
                return []

    def delete_collection(self):
        # Delete the Large Face List
        face_list_url = f"{self.face_api_url}/largefacelists/{self.large_face_list_id}"
        face_list_response = requests.delete(face_list_url, headers=self.headers)
        
        if face_list_response.status_code == 200:
            print(f"Successfully deleted Large Face List: {self.large_face_list_id}")
        else:
            print(f"Failed to delete Large Face List: {face_list_response.json()}")
        
        # Delete the Large Person Group
        person_group_url = f"{self.face_api_url}/largepersongroups/{self.large_person_group_id}"
        person_group_response = requests.delete(person_group_url, headers=self.headers)
        
        if person_group_response.status_code == 200:
            print(f"Successfully deleted Large Person Group: {self.large_person_group_id}")
        else:
            print(f"Failed to delete Large Person Group: {person_group_response.json()}")

        return face_list_response.status_code == 200 and person_group_response.status_code == 200
