
Run the Python script to get a processed portrait:

```console
$ curl -L -O https://github.com/danielgatis/rembg/releases/download/v0.0.0/BiRefNet-portrait-epoch_150.onnx
$ python3 program.py
Sample code for portrait processing with Azure Face API and Background Removal.
Number of faces detected: 1
Face detected: width=150, height=194, left=258, top=80
Head pose: yaw=0.4, pitch=-1.1, roll=3.1
Quality: high
Blur: level=low, value=0.0
Mask: type=noMask, nose and mouth covered=False
press ENTER to continue after viewing the portrait image.
End of the sample for portrait processing.
```

### Prerequisites

* Python 3.8+
* Face SDK: `python3 -m pip install azure-ai-vision-face`
* Pillow (PIL): `python3 -m pip install pillow`
* ONNX Runtime: `python3 -m pip install onnxruntime`


### Keys and Endpoints

[Create a Face resource](https://portal.azure.com/#create/Microsoft.CognitiveServicesFace) in the Azure portal and obtain a key and endpoint URL to call face detection API.

Set the keys and endponts as environment variables:

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


### Customization

Modify these variables in the code sample if needed:

```python
# Image url for portrait processing sample
IMAGE_URL = 'https://raw.githubusercontent.com/Azure-Samples/cognitive-services-sample-data-files/master/Face/images/detection2.jpg'

# Margin ratio on face crop
TOP_MARGIN_MAX = 0.75
BOTTOM_MARGIN_MAX = 0.75
LEFT_MARGIN_MAX = 1.5
RIGHT_MARGIN_MAX = 1.5
```
