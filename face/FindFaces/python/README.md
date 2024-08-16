
# Introduction

This repository contains sample Jupyter notebooks demonstrating how to use Azure Face service to create and manage face collections, add faces to collections, and find faces within images and collections. These samples are designed to help you get started with integrating Azure AI face recognition capabilities into your applications.

## Contents
| Name | Notebook | Description | Input Type(s) | Category |
|------|----------|-------------|---------------|----------|
| Find faces in an image | [Find faces in an image](find_faces_in_image.ipynb) | The application detects a face in a source image or uses a face ID or person ID to verify if it can be found in the search image. | Image, Face ID, Person ID | End-to-End Scenario |
| Find faces in a face collection | [Create a face collection](create_face_collection.ipynb) | The application detects all faces in an image and then creates and populates a face list or person group. | Image |End-to-End Scenario  |
| | [Find faces in a face collection](find_faces_in_collection.ipynb) | The application detects a face in an image or uses a face ID to verify if it matches any face in a given face collection (face list or person group). | Image, Face ID |  |
| Add face | [Add a face to a face collection](add_face_to_collection.ipynb) |  The application adds a face to a face collection, selecting the largest face if multiple faces are detected in the image. | Image | Collection Management |


## Installation
Install all Python modules and packages listed in the [requirements.txt](requirements.txt) file using the below command.

```python
pip install -r requirements.txt
```

### For getting started:
[Create a Face resource](https://portal.azure.com/#create/Microsoft.CognitiveServicesFace) in the Azure portal and obtain a key and endpoint URL to call face detection API. Set the keys and endponts as environment variables:

(For Windows)

```cmd
setx FACE_API_KEY <your_face_key>
setx FACE_ENDPOINT_URL <your_face_endpoint>
```

(For Linux)

```bash
export FACE_API_KEY <your_face_key>
export FACE_ENDPOINT_URL <your_face_endpoint>
```


## Requirements
Python 3.8+ <br>
Jupyter Notebook 6.5.2


## Usage

Each notebook is self-contained and includes instructions specific to its scenario. Simply open a notebook in Jupyter and follow the steps outlined within it.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft 
trademarks or logos is subject to and must follow 
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.