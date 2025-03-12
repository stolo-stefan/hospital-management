In order to install the dependencies and to run the application you need to follow these steps:

1. Create and activate a virtual environment:
    
    - For Windows, run these commands in the terminal::
        python -m venv venv
        venv\Scripts\Activate
    
    - For Mac/Linux run these commands in the terminal:
        python3 -m venv venv
        source venv/bin/activate
    
2. Install dependencies:

    - The requirements.txt file contains all the dependencies used for this app.:

    - After following step 1, run this command:
        pip install -r requirements.txt

3. Verify Installation:

    - Run the command to see the output (installed packages):
        pip freeze

4. Configure .env and DataBase:

    -Create 2 mySql databases named hospital_db, test_database

    -Update the .env file with your database credentials and secret keys:

        Example:
        FLASK_ENV=development
        DATABASE_URI = mysql://root:root@localhost:3306/hospital_db
        SECRET_KEY=superSecretKey
        JWT_SECRET_KEY=mySuperSecretJwtKey
        TEST_DATABASE_URI=mysql+pymysql://root:root@localhost:3306/test_database

5. Run migration and fixture:

    - In the virtual environment run:
        flask db upgrade debbd70a4a90
        python load_fixtures1.py
    
6. Start application:

    - Each time you run the application, you must execute one of the following commands based on your operating system:
        venv\Scripts\Activate
                OR
        source venv/bin/activate
        
    - After that you can run the Flask application with:
        python run.py

7. How to run tests:

API EndPoints:

1. Authentication Endpoints
    Base URL: /api/auth

    1.1 Login
        Endpoint: POST /login
        Description: Logs in a user and returns a JWT token.
        Required Fields: name (string), password (string).
        Response:
            200 OK: Returns an access token.
            400 Bad Request: Missing or invalid credentials.
    1.2 Register
        Endpoint: POST /register
        Description: Registers a new user (Doctor, Assistant). Only General Managers can register new users.
        Required Fields: name (string), password (string), role (string: Doctor or Assistant).
        Response:
            201 Created: User registered successfully.
            400 Bad Request: Missing fields or user already exists.
            401 Unauthorized: Only General Managers can register new users.

2. Doctor Endpoints
    Base URL: /api/doctors

    2.1 Get All Doctors
        Endpoint: GET /
        Description: Retrieves a list of all registered doctors. Only accessible by General Managers.
        Response:
            200 OK: Returns a list of doctors.
            204 No Content: No doctors found.
            401 Unauthorized: Only General Managers can access.
    2.2 Update Doctor
        Endpoint: PUT /<int:doctor_id>
        Description: Updates a doctor's information. Only General Managers can update.
        Required Fields: At least one of name, password, or role.
        Response:
            200 OK: Doctor updated successfully.
            404 Not Found: Doctor not found.
            401 Unauthorized: Only General Managers can update doctors.
    2.3 Delete Doctor
        Endpoint: DELETE /<int:doctor_id>
        Description: Deletes a doctor. Only General Managers can delete.
        Response:
            200 OK: Doctor deleted successfully.
            404 Not Found: Doctor not found.
            401 Unauthorized: Only General Managers can delete doctors.

3. Assistant Endpoints
    Base URL: /api/assistants

    3.1 Get All Assistants
        Endpoint: GET /
        Description: Retrieves a list of all registered assistants. Only accessible by General Managers.
        Response:
            200 OK: Returns a list of assistants.
            204 No Content: No assistants found.
            401 Unauthorized: Only General Managers can access.
    3.2 Update Assistant
        Endpoint: PUT /<int:assistant_id>
        Description: Updates an assistant's information. Only General Managers can update.
        Required Fields: At least one of name, password, or role.
        Response:
            200 OK: Assistant updated successfully.
            404 Not Found: Assistant not found.
            401 Unauthorized: Only General Managers can update assistants.
    3.3 Delete Assistant
        Endpoint: DELETE /<int:assistant_id>
        Description: Deletes an assistant. Only General Managers can delete.
        Response:
            200 OK: Assistant deleted successfully.
            404 Not Found: Assistant not found.
            401 Unauthorized: Only General Managers can delete assistants.
            
4. Patient Endpoints
    Base URL: /api/patients

    4.1 Register a New Patient
        Endpoint: POST /register
        Description: Creates a new patient. Allowed for General Managers and Doctors.
        Required Fields: name (string).
        Response:
            201 Created: Patient registered successfully.
            400 Bad Request: Missing or invalid data.
            401 Unauthorized: Only General Managers or Doctors can register patients.
    4.2 Get All Patients
        Endpoint: GET /
        Description: Retrieves a list of all patients.
        Response:
            200 OK: Returns a list of patients.
    4.3 Get Patient by ID
        Endpoint: GET /<int:patient_id>
        Description: Retrieves a specific patient by ID.
        Response:
            200 OK: Returns patient details.
            404 Not Found: Patient not found.
    4.4 Update Patient
        Endpoint: PUT /<int:patient_id>
        Description: Updates a patient’s information. Allowed for General Managers and Doctors.
        Required Fields: name (optional).
        Response:
            200 OK: Patient updated successfully.
            400 Bad Request: Invalid data.
            404 Not Found: Patient not found.
    4.5 Delete Patient
        Endpoint: DELETE /<int:patient_id>
        Description: Deletes a patient and removes associated data.
        Response:
            200 OK: Patient deleted successfully.
            404 Not Found: Patient not found.
    4.6 Assign Assistant to Patient
        Endpoint: POST /<int:patient_id>/assign
        Description: Assigns an assistant to a patient.
        Required Fields:
        assistant_id (required)
        doctor_id (only required if assigned by General Manager)
        Response:
            201 Created: Assistant assigned to patient.
            400 Bad Request: Missing data.
            401 Unauthorized: Only Doctors or General Managers can assign assistants.
    4.7 Get Patients Assigned to a Doctor
        Endpoint: GET /doctor/patients
        Description: Retrieves a list of patients assigned to a doctor.
        Response:
            200 OK: Returns a list of assigned patients.
            404 Not Found: No patients found.

5. Treatment Endpoints
    Base URL: /api/treatments

    5.1 Register a New Treatment
        Endpoint: POST /register
        Description: Registers a new treatment. Allowed for General Managers and Doctors.
        Required Fields: name (string), description (string).
        Response:
            201 Created: Treatment registered successfully.
            400 Bad Request: Missing or invalid data.
    5.2 Get All Treatments
        Endpoint: GET /
        Description: Retrieves a list of all treatments.
        Response:
            200 OK: Returns a list of treatments.
    5.3 Get Treatment by ID
        Endpoint: GET /<int:treatment_id>
        Description: Retrieves a specific treatment by ID.
        Response:
            200 OK: Returns treatment details.
            404 Not Found: Treatment not found.
    5.4 Update Treatment
        Endpoint: PUT /<int:treatment_id>
        Description: Updates treatment information. Allowed for General Managers and Doctors.
        Response:
            200 OK: Treatment updated successfully.
            404 Not Found: Treatment not found.
    5.5 Delete Treatment
        Endpoint: DELETE /<int:treatment_id>
        Description: Deletes a treatment from the system.
        Response:
            200 OK: Treatment deleted successfully.
            404 Not Found: Treatment not found.
    5.6 Prescribe Treatment to a Patient
        Endpoint: POST /<int:treatment_id>/prescribe/<int:patient_id>
        Description: Assigns an existing treatment to a patient. Only the supervising doctor can prescribe.
        Response:
            201 Created: Treatment prescribed successfully.
            403 Forbidden: Doctor does not supervise the patient.
            404 Not Found: Patient or treatment not found.
    5.7 Apply Treatment
        Endpoint: POST /<int:treatment_id>/apply/<int:patient_id>
        Description: Marks a prescribed treatment as applied by an Assistant.
        Response:
            200 OK: Treatment successfully applied.
            403 Forbidden: Assistant is not assigned to the patient.
            404 Not Found: Treatment or patient not found.

6. Report Endpoints
    Base URL: /api/reports

    6.1 Doctor-Patient Report
        Endpoint: GET /doctors-patients
        Description: Retrieves a report of all doctors and their assigned patients.
        Response:
            200 OK: Returns a structured report.
    6.2 Patient Treatment Report
        Endpoint: GET /patient-treatments/<int:patient_id>
        Description: Retrieves all treatments applied to a specific patient.
        Response:
            200 OK: Returns treatment history.
            403 Forbidden: Doctor does not supervise this patient.