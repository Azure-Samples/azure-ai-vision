
## Unified Face Collection

This repository contains a wrapper that demonstrates a unified interface for managing both face lists and person groups in the Azure Face API. It includes handling facial recognition and matching processes, such as creating, adding, retrieving, and deleting faces and persons within these collections.

### Key Features

* Provides a single interface to manage both face lists and person groups.
* Adds, removes, and searches for faces within the face collection.
* Saves face mapping data on the cloud, tracking face IDs in face lists and their associations with face IDs and person IDs in person groups.

### Steps Involved

* Initialization:
    * Initialize the unified face collection with the necessary parameters.
* Create/Delete Collections with a Unified ID
    * Create both a large face list and a large person group with a single unified ID.
    * Delete both the large face list and the large person group with the same unified ID.
* Add Face
    * Add the detected face to the large face list and get the face ID.
    * Add a new person to the large person group, associate the detected face with this person, and get the face ID and person ID.
    * Update the face mapping with the face ID from the large face list to the face ID and person ID in the large person group.
    * Return the face ID from the large face list and person ID from the large person group.
* Remove Face
    * Remove the face from the large face list using the face ID.
    * Find the corresponding large person group's face ID and person ID from the mapping data.
    * Remove the face from the large person group using the face ID and person ID.
    * Update the face mapping to reflect these changes.
* Remove Person
    * Remove the person from the large person group using the person ID or person name.
    * Update the face mapping to remove all associated face IDs linked to this person.
* Find Similar Faces/Persons
    * Search for similar faces within the large face list.
    * Search for similar persons within the large person group.
* List Faces/Persons
    * List all faces in the large face list
    * List all persons in the large person group
* Face Mapping Management
    * Update face mapping on the cloud after modifying face data.



