
## Find Faces

This sample demonstrates how to create and manage face collections, add faces, and verify faces within images using the Azure Face API.

### Key Features

* Learn how to use the Azure Face API to detect faces, retrieve bounding box and face ID.
* Create and manage face collections, including large face lists and large person groups.
* Add detected faces to collections more successfully and reduce errors.
* Verify faces by comparing detected faces or face IDs with existing images/collections.

### Steps Involved

* Find Faces in an Image
    * The input can be an image, face ID, or person ID.
    * If the input is an image: Detect the face in the source image first, then verify if the detected face can be found in a search image.
    * If the input is face ID or person ID: Verify directly if the face ID or person ID can be found in the search image.
* Find Faces in a Face Collection
    * Create a Face Collection
        * Detect all faces in an image.
        * Create and populate a large face list or large person group with the detected faces.
    * Find Faces
        * The input can be an image or face ID
        * If the input is an image: Detect the face in the source image first, then verify if the detected face matches any face/person in a given face collection (large face list or large person group).
        * If the input is face ID: Verify directly if the person ID matches any face/person in a given face collection (large face list or large person group).
* Add a Face to a Face Collection
    * Detect faces in an image.
    * Add the largest detected face to a face collection (large face list or large person group).