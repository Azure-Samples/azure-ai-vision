
Run the Java project to get a processed portrait:

```console
$ gradlew run
Sample code for portrait processing with Azure Face API and Background Removal API.
Number of faces detected: 1
Face detected: width=150, height=194, left=258, top=80
Head pose: yaw=0.4, pitch=-1.1, roll=3.1
Quality: high
Blur: level=low, value=0.0
Mask: type=noMask, nose and mouth covered=false
End of the sample for portrait processing.
```

### Prerequisites

* Java JDK/JRE 11
* Face SDK: `pkg:maven/com.azure/azure-ai-vision-face`
* HTTP Client: `pkg:maven/org.apache.httpcomponents/httpclient`


### Keys and Endpoints

[Create a Face resource](https://portal.azure.com/#create/Microsoft.CognitiveServicesFace) in the Azure portal and obtain a key and endpoint URL to call face detection API, and [a Vision resource](https://portal.azure.com/#create/Microsoft.CognitiveServicesComputerVision) to call background removal API.

Set the keys and endponts as environment variables:

(For Windows)

```cmd
setx FACE_API_KEY <your_face_key>
setx FACE_ENDPOINT_URL <your_face_endpoint>
setx BACKGROUND_API_KEY <your_vision_key>
setx BACKGROUND_ENDPOINT_URL <your_vision_endpoint>
```

(For Linux)

```bash
export FACE_API_KEY <your_face_key>
export FACE_ENDPOINT_URL <your_face_endpoint>
export BACKGROUND_API_KEY <your_vision_key>
export BACKGROUND_ENDPOINT_URL <your_vision_endpoint>
```


### Customization

Modify these variables in the code sample if needed:

```java
// Image url for portrait processing sample
private static final String IMAGE_URL = "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-sample-data-files/master/Face/images/detection2.jpg";

// Margin ratio on face crop
private static final float TOP_MARGIN_MAX = 0.75F;
private static final float BOTTOM_MARGIN_MAX = 0.75F;
private static final float LEFT_MARGIN_MAX = 1.5F;
private static final float RIGHT_MARGIN_MAX = 1.5F;
```
