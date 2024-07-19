
## Unified Face Collection

This repository contains a wrapper that demonstrates a unified interface for managing both face lists and person groups in the Azure Face API. It includes handling facial recognition and matching processes, such as creating, adding, retrieving, and deleting faces and persons within these collections.

### Key Features

* Provides a single interface to manage both face lists and person groups.
* Adds, removes, and searches for faces within the face collection.
* Loads and saves face mapping data to a JSON file, tracking face IDs in face lists and their associations with face IDs and person IDs in person groups.

### Steps Involved

* Initialization:
    * Initialize the unified face collection with the necessary parameters.
    * Load existing face mapping or create a new one if it doesn't exist.
* Create/delete Collection
    * Create/delete a large face list with a specific ID.
    * Create/delete a large person group with a specific ID.
* Add Face
    * Add the detected face to the large face list and get the face ID.
    * Add a new person to the large person group and associate the detected face with this person.
    * Update the face mapping with the new face and person IDs.
* Remove Face
    * Remove the face from the large face list using the face ID.
    * Remove the face from the large person group using the associated person ID and face ID.
    * Update the face mapping to reflect these changes.
* Remove Person
    * Remove the person from the large person group using the associated person ID or person name.
    * Update the face mapping to remove all associated face IDs linked to this person.
* Find Similar Faces/Persons
    * Search for similar faces within the large face list.
    * Serach for similar persons within the large person group.  
* Face Mapping Management
    * Load the face mapping from a JSON file during initialization.
    * Save the updated face mapping to the JSON file after modifying face data.



