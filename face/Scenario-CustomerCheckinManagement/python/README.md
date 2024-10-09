
# Introduction

This repository contains a Python script that demonstrates how to manage customer face enrollment, identification, and dynamic person group linking using Azure Face services. It streamlines the management of customers by leveraging dynamic person groups for both daily and location-specific tasks.
- The script automates the creation of customer profiles, face enrollment, and linking them to dynamic person groups without requiring a training step.
- It manages face identification across dynamic groups, ensuring that customers are properly referenced in both daily and location-based groups.

## Contents
| Notebook | Description | Type |  
|----------|-------------|------------|
| [Customer Checkin Management](customer_checkin_management.ipynb) | This script enrolls customer faces, identifies persons in daily and location-specific dynamic person groups, and links them by reference for simplified management. | Enrollment/Identification |

## Shared Functions

For convenience, commonly used functions in the notebook are consolidated in [shared_functions.py](shared_functions.py). Download this file before running any of the notebooks.

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