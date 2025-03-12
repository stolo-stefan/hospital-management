# Hospital Management System

## Installation Guide

### 1. Create and Activate a Virtual Environment

#### Windows:
```sh
python -m venv venv
venv\Scripts\Activate
```

#### Mac/Linux:
```sh
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies
Ensure you have the required dependencies installed by running:
```sh
pip install -r requirements.txt
```

### 3. Verify Installation
Check the installed packages:
```sh
pip freeze
```

### 4. Configure `.env` and Database

- Create two MySQL databases named `hospital_db` and `test_database`.
- Update the `.env` file with your database credentials and secret keys:

#### Example `.env` file:
```env
FLASK_ENV=development
DATABASE_URI=mysql://root:root@localhost:3306/hospital_db
SECRET_KEY=superSecretKey
JWT_SECRET_KEY=mySuperSecretJwtKey
TEST_DATABASE_URI=mysql+pymysql://root:root@localhost:3306/test_database
```

### 5. Run Migrations and Load Fixtures
Run the following commands inside the virtual environment:
```sh
flask db upgrade debbd70a4a90
python load_fixtures1.py
```

### 6. Start Application
Activate the virtual environment and run the Flask application:

#### Windows:
```sh
venv\Scripts\Activate
python run.py
```

#### Mac/Linux:
```sh
source venv/bin/activate
python run.py
```

## Running Tests

To run tests, use:
```sh
pytest
```

---

## API Endpoints

### 1. Authentication Endpoints
**Base URL:** `/api/auth`

#### 1.1 Login
- **Endpoint:** `POST /login`
- **Description:** Logs in a user and returns a JWT token.
- **Required Fields:** `name (string)`, `password (string)`
- **Responses:**
  - `200 OK`: Returns an access token.
  - `400 Bad Request`: Missing or invalid credentials.

#### 1.2 Register
- **Endpoint:** `POST /register`
- **Description:** Registers a new user (Doctor, Assistant). Only General Managers can register new users.
- **Required Fields:** `name (string)`, `password (string)`, `role (Doctor/Assistant)`
- **Responses:**
  - `201 Created`: User registered successfully.
  - `400 Bad Request`: Missing fields or user already exists.
  - `401 Unauthorized`: Only General Managers can register new users.

### 2. Doctor Endpoints
**Base URL:** `/api/doctors`

#### 2.1 Get All Doctors
- **Endpoint:** `GET /`
- **Description:** Retrieves all registered doctors. Only accessible by General Managers.
- **Responses:**
  - `200 OK`: Returns a list of doctors.
  - `204 No Content`: No doctors found.
  - `401 Unauthorized`: Only General Managers can access.

#### 2.2 Update Doctor
- **Endpoint:** `PUT /<int:doctor_id>`
- **Description:** Updates a doctor's information. Only General Managers can update.
- **Required Fields:** At least one of `name, password, or role`.
- **Responses:**
  - `200 OK`: Doctor updated successfully.
  - `404 Not Found`: Doctor not found.
  - `401 Unauthorized`: Only General Managers can update doctors.

#### 2.3 Delete Doctor
- **Endpoint:** `DELETE /<int:doctor_id>`
- **Description:** Deletes a doctor. Only General Managers can delete.
- **Responses:**
  - `200 OK`: Doctor deleted successfully.
  - `404 Not Found`: Doctor not found.
  - `401 Unauthorized`: Only General Managers can delete doctors.

### 3. Assistant Endpoints
**Base URL:** `/api/assistants`

#### 3.1 Get All Assistants
- **Endpoint:** `GET /`
- **Description:** Retrieves all registered assistants. Only accessible by General Managers.
- **Responses:**
  - `200 OK`: Returns a list of assistants.
  - `204 No Content`: No assistants found.
  - `401 Unauthorized`: Only General Managers can access.

#### 3.2 Update Assistant
- **Endpoint:** `PUT /<int:assistant_id>`
- **Description:** Updates an assistant's information. Only General Managers can update.
- **Required Fields:** At least one of `name, password, or role`.
- **Responses:**
  - `200 OK`: Assistant updated successfully.
  - `404 Not Found`: Assistant not found.
  - `401 Unauthorized`: Only General Managers can update assistants.

#### 3.3 Delete Assistant
- **Endpoint:** `DELETE /<int:assistant_id>`
- **Description:** Deletes an assistant. Only General Managers can delete.
- **Responses:**
  - `200 OK`: Assistant deleted successfully.
  - `404 Not Found`: Assistant not found.
  - `401 Unauthorized`: Only General Managers can delete assistants.

### 4. Patient Endpoints
**Base URL:** `/api/patients`

#### 4.1 Register a New Patient
- **Endpoint:** `POST /register`
- **Description:** Creates a new patient. Allowed for General Managers and Doctors.
- **Required Fields:** `name (string)`
- **Responses:**
  - `201 Created`: Patient registered successfully.
  - `400 Bad Request`: Missing or invalid data.
  - `401 Unauthorized`: Only General Managers or Doctors can register patients.

#### 4.2 Get All Patients
- **Endpoint:** `GET /`
- **Description:** Retrieves all patients.
- **Responses:**
  - `200 OK`: Returns a list of patients.

#### 4.3 Get Patient by ID
- **Endpoint:** `GET /<int:patient_id>`
- **Description:** Retrieves a specific patient by ID.
- **Responses:**
  - `200 OK`: Returns patient details.
  - `404 Not Found`: Patient not found.

#### 4.4 Update Patient
- **Endpoint:** `PUT /<int:patient_id>`
- **Description:** Updates a patient’s information. Allowed for General Managers and Doctors.
- **Required Fields:** `name (optional)`
- **Responses:**
  - `200 OK`: Patient updated successfully.
  - `400 Bad Request`: Invalid data.
  - `404 Not Found`: Patient not found.

### 5. Treatment Endpoints
**Base URL:** `/api/treatments`

#### 5.1 Register a New Treatment
- **Endpoint:** `POST /register`
- **Description:** Registers a new treatment. Allowed for General Managers and Doctors.
- **Required Fields:** `name (string)`, `description (string)`
- **Responses:**
  - `201 Created`: Treatment registered successfully.
  - `400 Bad Request`: Missing or invalid data.

#### 5.2 Get All Treatments
- **Endpoint:** `GET /`
- **Description:** Retrieves all treatments.
- **Responses:**
  - `200 OK`: Returns a list of treatments.

#### 5.3 Prescribe Treatment to a Patient
- **Endpoint:** `POST /<int:treatment_id>/prescribe/<int:patient_id>`
- **Description:** Assigns an existing treatment to a patient. Only the supervising doctor can prescribe.
- **Responses:**
  - `201 Created`: Treatment prescribed successfully.
  - `403 Forbidden`: Doctor does not supervise the patient.
  - `404 Not Found`: Patient or treatment not found.

---

For full API documentation, refer to the project documentation files.