import json
from PIL import Image
from azure.core.credentials import AzureKeyCredential
from azure.ai.vision.face import FaceClient, FaceAdministrationClient
from azure.ai.vision.face.models import FaceDetectionModel, FaceRecognitionModel

class UnifiedFaceCollection:
    def __init__(self, subscription_key, endpoint, face_collection_id, injection_header):
        self.face_client = FaceClient(endpoint, AzureKeyCredential(subscription_key), headers = {"X-MS-AZSDK-Telemetry": injection_header})
        self.face_admin_client = FaceAdministrationClient(endpoint, AzureKeyCredential(subscription_key), headers = {"X-MS-AZSDK-Telemetry": injection_header})
        self.face_collection_id = face_collection_id
        self.large_face_list_id = face_collection_id + "_face_list"
        self.large_person_group_id = face_collection_id + "_person_group"
        self.create_collections()

    def detect_faces(self, image_path):
        with open(image_path, 'rb') as image_data:
            detected_faces = self.face_client.detect(
                    image_content=image_data.read(),
                    detection_model=FaceDetectionModel.DETECTION03,
                    recognition_model=FaceRecognitionModel.RECOGNITION04,
                    return_face_id=True,
            )
        return detected_faces

    def enlarge_bounding_box(self, face_rectangle, image_width, image_height, enlargement_factor=1.2):
        left = max(0, face_rectangle['left'] - (face_rectangle['width'] * (enlargement_factor - 1) / 2))
        top = max(0, face_rectangle['top'] - (face_rectangle['height'] * (enlargement_factor - 1) / 2))
        width = min(image_width - left, face_rectangle['width'] * enlargement_factor)
        height = min(image_height - top, face_rectangle['height'] * enlargement_factor)
        return {'left': int(left), 'top': int(top), 'width': int(width), 'height': int(height)}

    def get_image_dimensions(self, image_path):
        with Image.open(image_path) as img:
            return img.width, img.height

    def create_collections(self):
        # Create Large Face List
        try :
            self.face_admin_client.large_face_list.get(self.large_face_list_id)
            print(f"Large Face List: {self.large_face_list_id} already exists.")
        except Exception:
            print(f"Creating Large Face List: {self.large_face_list_id}")
            self.face_admin_client.large_face_list.create(
                self.large_face_list_id,
                name=self.face_collection_id + " Face List",
                recognition_model=FaceRecognitionModel.RECOGNITION04
            )
        
        # Create Large Person Group
        try :
            self.face_admin_client.large_person_group.get(self.large_person_group_id)
            print(f"Large Person Group: {self.large_person_group_id} already exists.")
        except Exception:
            print(f"Creating Large Person Group: {self.large_person_group_id}")
            self.face_admin_client.large_person_group.create(
                self.large_person_group_id,
                name=self.face_collection_id + " Person Group",
                recognition_model=FaceRecognitionModel.RECOGNITION04
            )

    def add_face(self, image_path, person_name=None):
        faces = self.detect_faces(image_path)
        target_face = None
        if len(faces) == 0:
            return "No faces detected in the image."
        elif len(faces) > 1:
            image_width, image_height = self.get_image_dimensions(image_path)
            print(f"Multiple faces detected. Using the first face (largest face) for adding to the collection.")
            face_rectangle = self.enlarge_bounding_box(faces[0]['faceRectangle'], image_width, image_height)
            target_face = [face_rectangle['left'],face_rectangle['top'],face_rectangle['width'], face_rectangle['height']]
        else:
            print(f"One face detected. Adding to the collection.")
        
        # Add face to Large Face List
        with open(image_path, 'rb') as image:
            persisted_face_id = self.face_admin_client.large_face_list.add_face(
                self.large_face_list_id,
                image,
                target_face=target_face,
                detection_model=FaceDetectionModel.DETECTION03,
                user_data=person_name
            ).persisted_face_id

        if person_name:
            # Check if person exists
            person = self.get_person_by_name(person_name)
            if person is None:
                # Create a new person if not exists
                person = self.face_admin_client.large_person_group.create_person(
                    self.large_person_group_id,
                    name=person_name
                )
            person_id = person.person_id

            # Add face to the created or existing person
            with open(image_path, 'rb') as image:
                person_persisted_face_id = self.face_admin_client.large_person_group.add_face(
                    self.large_person_group_id,
                    person_id,
                    image,
                    target_face=target_face,
                    detection_model=FaceDetectionModel.DETECTION03,
                ).persisted_face_id

                # Update the userData field with the mapping in the Large Face List
                user_data_face_list = {
                    "personId": person_id,
                    "personPersistedFaceId": person_persisted_face_id
                }
                user_data_face_list_json = json.dumps(user_data_face_list)
                self.face_admin_client.large_face_list.update_face(
                    self.large_face_list_id,
                    persisted_face_id,
                    user_data=user_data_face_list_json
                )

                # Update the userData field with the mapping in the Large Person Group
                user_data_large_person_group = {
                    "persistedFaceId": persisted_face_id
                }
                user_data_large_person_group_json = json.dumps(user_data_large_person_group)
                self.face_admin_client.large_person_group.update_face(
                    self.large_person_group_id,
                    person_id,
                    person_persisted_face_id,
                    user_data=user_data_large_person_group_json
                )

                return {
                    "face_list": {
                        "persistedFaceId": persisted_face_id,
                    },
                    "person_group": {
                        "personId": person_id,
                    }
                }

        return {"face_list": { "persistedFaceId": persisted_face_id }}

    def remove_face(self, persisted_face_id):
        face_data  = self.face_admin_client.large_face_list.get_face(
            large_face_list_id=self.large_face_list_id,
            persisted_face_id=persisted_face_id
        )
        user_data = getattr(face_data, 'user_data', None)
        if not user_data:
            return False

        user_data_dict = json.loads(user_data)
        person_id = user_data_dict.get("personId")
        person_persisted_face_id = user_data_dict.get("personPersistedFaceId")

        if person_id and person_persisted_face_id:
            # Remove face from Large Person Group
            self.face_admin_client.large_person_group.delete_face(
                large_person_group_id=self.large_person_group_id,
                person_id=person_id,
                persisted_face_id=person_persisted_face_id
            )

            # Check if the person has any faces left
            person_data = self.face_admin_client.large_person_group.get_person(
                large_person_group_id=self.large_person_group_id,
                person_id=person_id
            )
            if not person_data.get("persistedFaceIds"):
                # Delete the person if no faces are left
                print(f"Deleting the person as no faces are left.")
                self.face_admin_client.large_person_group.delete_person(
                    large_person_group_id=self.large_person_group_id,
                    person_id=person_id
                )

        # Remove face from Large Face List
        self.face_admin_client.large_face_list.delete_face(
            large_face_list_id=self.large_face_list_id,
            persisted_face_id=persisted_face_id
        )

        return True

    def remove_person(self, person_identifier, delete_faces=False):
        # Determine if the identifier is a name or an ID
        person_id = None
        if isinstance(person_identifier, str) and len(person_identifier) == 36:
            person_id = person_identifier
        else:
            person = self.get_person_by_name(person_identifier)
            if person:
                person_id = person.person_id
            else:
                return False

        # Retrieve the person's faces from the person group
        person_faces = self.face_admin_client.large_person_group.get_person(
            large_person_group_id=self.large_person_group_id,
            person_id=person_id
        )
        # Update userData in the Large Face List
        for person_persisted_face_id in person_faces.persisted_face_ids:
            # Retrieve userData from the face in the person group
            face_data = self.face_admin_client.large_person_group.get_face(
                large_person_group_id=self.large_person_group_id,
                person_id=person_id,
                persisted_face_id=person_persisted_face_id
            )
            user_data = getattr(face_data, 'user_data', None)
            if user_data:
                user_data_dict = json.loads(user_data)
                persisted_face_id = user_data_dict.get("persistedFaceId")

                if delete_faces:
                    # Delete the face from the Large Face List
                    self.face_admin_client.large_face_list.delete_face(
                        large_face_list_id=self.large_face_list_id,
                        persisted_face_id=persisted_face_id
                    )
                else:
                    # Update userData for the face in the Large Face List
                    user_data_face_list = {
                        "personId": None,
                        "personPersistedFaceId": None
                    }
                    user_data_face_list_json = json.dumps(user_data_face_list)
                    self.face_admin_client.large_face_list.update_face(
                        self.large_face_list_id,
                        persisted_face_id,
                        user_data=user_data_face_list_json
                    )

        # Remove the person from the person group
        self.face_admin_client.large_person_group.delete_person(
            large_person_group_id=self.large_person_group_id,
            person_id=person_id
        )

        return True

    def get_person_by_name(self, person_name):
        persons = self.face_admin_client.large_person_group.get_persons(self.large_person_group_id)
        for person in persons:
            if person.name == person_name:
                return person
        return None

    def train(self):
        # Train the Large Face List
        poller_face_list = self.face_admin_client.large_face_list.begin_train(
            large_face_list_id=self.large_face_list_id,
            polling_interval=5,
        )
        poller_face_list.wait()
        print(f"The face list {self.large_face_list_id} is trained successfully.")

        # Train the Large Person Group
        poller_person_group = self.face_admin_client.large_person_group.begin_train(
            large_person_group_id=self.large_person_group_id,
            polling_interval=5,
        )
        poller_person_group.wait()
        print(f"The person group {self.large_person_group_id} is trained successfully.")
        
        return True

    def find_face(self, image_path, search_type='face'):
        # Detect face in the image
        detected_faces = self.detect_faces(image_path)
        face_ids = [face['faceId'] for face in detected_faces]
        if not face_ids:
            return []

        normalized_results = []
        if search_type == 'person':
            # Find similar persons in the Large Person Group
            identify_results = self.face_client.identify_from_large_person_group(
                face_ids=[face_ids[0]],
                large_person_group_id=self.large_person_group_id
            )

            for result in identify_results:
                for candidate in result.get('candidates', []):
                    normalized_results.append({
                        'personId': candidate.person_id,
                        'confidence': candidate.confidence
                    })
            return normalized_results
        else:
            # Find similar faces in the Large Face List
            similar_faces_results = self.face_client.find_similar_from_large_face_list(
                face_id=face_ids[0],
                large_face_list_id=self.large_face_list_id
            )
            for result in similar_faces_results:
                normalized_results.append({
                    'faceId': result.persisted_face_id,
                    'confidence': result.confidence
                })
            return normalized_results

    def delete_collection(self):
        self.face_admin_client.large_face_list.delete(self.large_face_list_id)
        self.face_admin_client.large_person_group.delete(self.large_person_group_id)
        return

    def list_faces(self):
        faces = []
        data = self.face_admin_client.large_face_list.get_faces(self.large_face_list_id)
        for face in data:
            faces.append({
                'persistedFaceId': face.persisted_face_id,
                'personId': json.loads(face.user_data).get('personId', None)
            })

        return faces

    def list_persons(self):
        persons = []
        data = self.face_admin_client.large_person_group.get_persons(self.large_person_group_id)
        for person in data:
            persons.append({
                'personId': person.person_id,
                'name': person.name,
            })

        return persons

    def list_all(self):
        faces = self.list_faces()
        persons = self.list_persons()
        return {
            "faces": faces,
            "persons": persons
        }
