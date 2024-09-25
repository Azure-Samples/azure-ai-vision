
# Introduction

This repository provides sample Jupyter notebooks showcasing the usage of the Dynamic Person Group in the Azure Face service for face enrollment and tagging.
- The face enrollment process covers creating a person, adding faces to a person, and forming a dynamic person group.
- For tagging, the notebooks illustrate how to tag faces within a dynamic person group or from a specific list of persons.

## Contents
| Notebook | Description | Type |  
|----------|-------------|------------|
| [Enroll persons with single face](enroll_single_face_per_person.ipynb) | The application enrolls one face for each person from a directory of images, with each image containing a different person. | Enrollment |
| [Enroll persons with multiple faces](enroll_multiple_faces_per_person.ipynb) | The application enrolls multiple faces for each person from a directory where each subfolder represents a different person. | Enrollment |
| [Tag faces](tag_faces.ipynb) |  The application tags faces against a dynamic person group/a specific list of persons | Tagging |

## Shared Functions

For convenience, commonly used functions across these notebooks are consolidated in [shared_functions.py](shared_functions.py). Download this file before running any of the notebooks.

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