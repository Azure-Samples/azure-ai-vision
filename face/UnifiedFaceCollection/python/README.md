
# Introduction

The Unified Face Collection system is designed to streamline and unify the management of facial recognition and identification tasks by integrating Azure Face API's Large Face List and Large Person Group functionalities into a single, cohesive framework. This system aims to provide a comprehensive and unified solution for creating, training, and maintaining face collections, enhancing the efficiency of facial recognition processes in applications such as security, authentication, and user identification.

## Contents
| Notebook | Description |
|----------|-------------|
| [Example usage](example_usage.ipynb) | Jupyter Notebook providing an overview and usage examples for the Unified Face Collection system.|
| [Unified face collection](unified_face_collection.py) | Python script defining the `UnifiedFaceCollection` class, which encapsulates the core functionalities for managing face collections using Azure's Face API. |

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