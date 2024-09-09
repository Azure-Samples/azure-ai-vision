
## Portrait Processing

The sample demonstrates how to make a portrait image out of an original image by using Azure Face API and Background Removal, as illustrated below:

| Input Image | Output Portrait | (Intermediate) Output Matting |
| :-: | :-: | :-: |
| ![detection2.jpg](https://raw.githubusercontent.com/Azure-Samples/cognitive-services-sample-data-files/master/Face/images/detection2.jpg) | ![portrait.png](portrait.png) | ![matting.bmp](matting.bmp) |


### Key Features

* Learn how to call face detection API via SDK and retrieve facial attirbutes such us bounding box, head pose, blur level, quality, etc.
* Optimize network lantency by down-scaling and compressing input image as JPEG stream.
* Leverage ONNX Runtime to run the BiRefNet image segmentation model and apply alpha channel locally.


### Steps Involved

1. Download an image from web URL. Resize and compress as JPEG memory stream.
2. Detect faces in the stream, and read the returned facial attributes. Optionally, check whether the face quality is suitable for portrait processing.
3. Crop the face out from the image, and request for foreground matting of the focused area.
4. Compose the transparent background portrait using the alpha matting and the face crop.


### References

* https://github.com/ZhengPeng7/BiRefNet
* https://github.com/danielgatis/rembg
