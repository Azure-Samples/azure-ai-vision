
## Clinic Checkin Management

The script is designed to automate the management of patient face detection, identification, and enrollment in a clinic system that uses Azure's Dynamic Person Groups. The goal is to ensure that each patient's face is efficiently recognized and linked to both daily and clinic-specific dynamic person groups, improving the accuracy of face identification and reducing redundancies. The system operates with **No Training Required**, allowing faster setup and updates, and eliminates the need for buffer groups, simplifying group management with **No Buffer Groups**.

### Example
#### Scenario
- Person are created and added into DynamicPersonGroup by reference.
- Clinic: Each clinic will have its own group.
- Daily Group: A smaller, temporary group for the daily visit list, nested within the larger - clinic group.
![clinic_checkin_management_example.jpg](clinic_checkin_management_example.jpg)
#### Workflow
![clinic_checkin_management_workflow.jpg](clinic_checkin_management_workflow.jpg)

### Key Features

* **No Training Required**: Faster setup and updates without a training step.
* **No Buffer Groups**: Simplify group management by eliminating the need for buffer groups.

### Steps Involved

* Face Detection:
    * Detect the largest face in the input image using the Azure Face API.
    * If no face is detected, log the result and terminate the process.
* Check/Generate Groups:
    * Verify if the clinic-specific/daily dynamic person group exists; if not, create it.
    * Ensure groups are created without buffer groups, simplifying the process.
* Face Identification:
    * Attempt to identify the face in the daily dynamic group first.
    * If no match is found in the daily group, check the clinic-specific group for a match.
* Person Creation:
    * If the face is not identified in either group, create a new person.
    * Add the largest detected face to the newly created person’s profile.
* Person Reference Linking:
    * Link the newly created or identified person by reference to the daily dynamic group for the current visit.
    * Link the person by reference to the clinic-specific dynamic person group for long-term management.