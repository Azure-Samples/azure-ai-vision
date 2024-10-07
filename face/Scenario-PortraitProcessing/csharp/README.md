
Run the C# project to get a processed portrait:

```console
$ curl -L -O https://github.com/danielgatis/rembg/releases/download/v0.0.0/BiRefNet-portrait-epoch_150.onnx
$ dotnet run
Sample code for portrait processing with Azure Face API and Background Removal.
Number of faces detected: 1
Face detected: width=150, height=194, left=258, top=80
Head pose: yaw=0.6, pitch=-1.6, roll=3.4
Quality: high
Blur: level=low, value=0
Mask: type=noMask, nose and mouth covered=False
End of the sample for portrait processing.
```

### Prerequisites

* .NET for Windows
* Face SDK: `dotnet add package Azure.AI.Vision.Face --prerelease`
* Image Processing: `dotnet add package System.Drawing.Common`
* ONNX Runtime: `dotnet add package Microsoft.ML.OnnxRuntime`


### Keys and Endpoints

[Create a Face resource](https://portal.azure.com/#create/Microsoft.CognitiveServicesFace) in the Azure portal and obtain a key and endpoint URL to call face detection API.

Set the keys and endponts as environment variables:

```cmd
setx FACE_API_KEY <your_face_key>
setx FACE_ENDPOINT_URL <your_face_endpoint>
```

After you add the environment variables, you may need to restart any running programs that will read the environment variables, including the console window.


### Customization

Modify these variables in the code sample if needed:

```cs
// Image url for portrait processing sample
const string IMAGE_URL = "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-sample-data-files/master/Face/images/detection2.jpg";

// Margin ratio on face crop
const float TOP_MARGIN_MAX = 0.75F;
const float BOTTOM_MARGIN_MAX = 0.75F;
const float LEFT_MARGIN_MAX = 1.5F;
const float RIGHT_MARGIN_MAX = 1.5F;
```
