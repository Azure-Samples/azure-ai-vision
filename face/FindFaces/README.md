
## Find Faces

This sample demonstrates how to create and manage face collections, add faces, and verify faces within images using the Azure Face API.

### Key Features

* Learn how to use the Azure Face API to detect faces and retrieve bounding box and face ID.
* Create and manage face collections, including face lists and person groups.
* Add detected faces to collections more successfully and reduce errors.
* Verify faces by comparing detected faces or face IDs with existing images/collections.

### Steps Involved

* Find Faces in an Image
    * Detect faces in a source image.
    * Verify if the detected face can be found in a search image using face ID or person ID.
* Find Faces in a Face Collection
    * Detect faces in an image.
    * Verify if the detected face matches any face in a given face collection (face list or person group) using face ID.
* Create a Face Collection
    * Detect all faces in an image.
    * Create and populate a face list or person group with the detected faces.
* Add a Face to a Face Collection
    * Detect faces in an image.
    * Add the largest detected face to a face collection (face list, large face list, person group, large person group, or person directory).