# API Documentation - Stroke Prediction Management System

## Overview

This document provides comprehensive API documentation for the Stroke Prediction Management System. While the application is primarily designed as a web interface, this documentation describes the underlying routes and data structures for developers and integrators.

---

## Table of Contents

1. [Authentication](#authentication)
2. [User Management](#user-management)
3. [Patient Management](#patient-management)
4. [Analytics](#analytics)
5. [Admin Functions](#admin-functions)
6. [Error Handling](#error-handling)
7. [Data Models](#data-models)

---

## Base URL

```
Development: http://localhost:5000
Production: https://your-domain.com
```

---

## Authentication

### Register User

**Endpoint:** `POST /register`

**Description:** Create a new user account

**Content-Type:** `application/x-www-form-urlencoded`

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| username | string | Yes | Unique username (min 3 chars) |
| email | string | Yes | Valid email address |
| password | string | Yes | Password (min 8 chars, uppercase, lowercase, number) |
| confirm_password | string | Yes | Must match password |

**Example Request:**
```http
POST /register HTTP/1.1
Host: localhost:5000
Content-Type: application/x-www-form-urlencoded

username=johndoe&email=john@example.com&password=SecurePass123&confirm_password=SecurePass123
```

**Success Response:**
```
Status: 302 Redirect to /login
Flash Message: "Registration successful! Please log in."
```

**Error Responses:**

| Status | Message | Reason |
|--------|---------|--------|
| 400 | "All fields are required." | Missing required field |
| 400 | "Invalid email format." | Email format invalid |
| 400 | "Passwords do not match." | Password confirmation mismatch |
| 400 | "Password must be at least 8 characters long" | Weak password |
| 409 | "Username or email already exists." | Duplicate user |

---

### Login

**Endpoint:** `POST /login`

**Description:** Authenticate user and create session

**Content-Type:** `application/x-www-form-urlencoded`

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| username | string | Yes | Registered username |
| password | string | Yes | User password |

**Example Request:**
```http
POST /login HTTP/1.1
Host: localhost:5000
Content-Type: application/x-www-form-urlencoded

username=johndoe&password=SecurePass123
```

**Success Response:**
```
Status: 302 Redirect to /dashboard
Set-Cookie: session=<encrypted_session_token>; HttpOnly; SameSite=Lax
Flash Message: "Welcome back, johndoe!"
```

**Error Responses:**

| Status | Message | Reason |
|--------|---------|--------|
| 400 | "Please provide both username and password." | Missing credentials |
| 401 | "Invalid username or password." | Authentication failed |

**Security Features:**
- Bcrypt password verification
- Session token generation
- Failed attempt logging
- Rate limiting (5 attempts per minute)

---

### Logout

**Endpoint:** `GET /logout`

**Description:** Terminate user session

**Authentication:** Required

**Example Request:**
```http
GET /logout HTTP/1.1
Host: localhost:5000
Cookie: session=<session_token>
```

**Success Response:**
```
Status: 302 Redirect to /login
Flash Message: "You have been logged out successfully."
```

---

## User Management

### View Dashboard

**Endpoint:** `GET /dashboard`

**Description:** Display user dashboard with statistics

**Authentication:** Required

**Example Request:**
```http
GET /dashboard HTTP/1.1
Host: localhost:5000
Cookie: session=<session_token>
```

**Success Response:**
```json
Status: 200 OK
Content-Type: text/html

{
  "stats": {
    "total_patients": 5110,
    "stroke_cases": 249,
    "no_stroke_cases": 4861,
    "avg_age": 43.2
  },
  "recent_patients": [
    {
      "id": 9046,
      "gender": "Male",
      "age": 67,
      "stroke": 1,
      "...": "..."
    }
  ]
}
```

---

## Patient Management

### List Patients

**Endpoint:** `GET /patients`

**Description:** Retrieve paginated list of patients with optional filters

**Authentication:** Required

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| page | integer | No | Page number (default: 1) |
| search | string | No | Search by ID, gender, work type, smoking status |
| stroke_filter | integer | No | Filter by stroke status (0 or 1) |
| gender_filter | string | No | Filter by gender (Male, Female, Other) |

**Example Request:**
```http
GET /patients?page=1&stroke_filter=1&gender_filter=Male HTTP/1.1
Host: localhost:5000
Cookie: session=<session_token>
```

**Success Response:**
```json
Status: 200 OK

{
  "patients": [
    {
      "id": 9046,
      "gender": "Male",
      "age": 67.0,
      "hypertension": 0,
      "heart_disease": 1,
      "ever_married": "Yes",
      "work_type": "Private",
      "Residence_type": "Urban",
      "avg_glucose_level": 228.69,
      "bmi": 36.6,
      "smoking_status": "formerly smoked",
      "stroke": 1
    }
  ],
  "page": 1,
  "total_pages": 13
}
```

---

### View Patient Details

**Endpoint:** `GET /patient/<int:patient_id>`

**Description:** Retrieve detailed information for a specific patient

**Authentication:** Required

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| patient_id | integer | Yes | Unique patient identifier |

**Example Request:**
```http
GET /patient/9046 HTTP/1.1
Host: localhost:5000
Cookie: session=<session_token>
```

**Success Response:**
```json
Status: 200 OK

{
  "id": 9046,
  "gender": "Male",
  "age": 67.0,
  "hypertension": 0,
  "heart_disease": 1,
  "ever_married": "Yes",
  "work_type": "Private",
  "Residence_type": "Urban",
  "avg_glucose_level": 228.69,
  "bmi": 36.6,
  "smoking_status": "formerly smoked",
  "stroke": 1,
  "created_at": "2025-12-01T10:30:00",
  "updated_at": "2025-12-01T10:30:00",
  "created_by": "admin"
}
```

**Error Responses:**

| Status | Message | Reason |
|--------|---------|--------|
| 404 | "Patient not found." | Invalid patient ID |

---

### Add Patient

**Endpoint:** `POST /patient/add`

**Description:** Create a new patient record

**Authentication:** Required

**Content-Type:** `application/x-www-form-urlencoded`

**Parameters:**

| Parameter | Type | Required | Validation |
|-----------|------|----------|------------|
| patient_id | integer | Yes | Unique, positive integer |
| gender | string | Yes | Male, Female, Other |
| age | float | Yes | 0-120 |
| hypertension | integer | Yes | 0 or 1 |
| heart_disease | integer | Yes | 0 or 1 |
| ever_married | string | Yes | Yes, No |
| work_type | string | Yes | Private, Self-employed, Govt_job, Children, Never_worked |
| Residence_type | string | Yes | Urban, Rural |
| avg_glucose_level | float | Yes | 0-500 |
| bmi | float/string | No | 10-100 or "N/A" |
| smoking_status | string | Yes | formerly smoked, never smoked, smokes, Unknown |
| stroke | integer | Yes | 0 or 1 |

**Example Request:**
```http
POST /patient/add HTTP/1.1
Host: localhost:5000
Cookie: session=<session_token>
Content-Type: application/x-www-form-urlencoded

patient_id=99999&gender=Male&age=45&hypertension=0&heart_disease=0&ever_married=Yes&work_type=Private&Residence_type=Urban&avg_glucose_level=120.5&bmi=25.6&smoking_status=never+smoked&stroke=0
```

**Success Response:**
```
Status: 302 Redirect to /patients
Flash Message: "Patient record added successfully!"
```

**Error Responses:**

| Status | Message | Reason |
|--------|---------|--------|
| 400 | "Missing required field: [field_name]" | Required field missing |
| 400 | "Age must be between 0 and 120" | Invalid age range |
| 400 | "Glucose level must be between 0 and 500" | Invalid glucose |
| 400 | "BMI must be between 10 and 100" | Invalid BMI |
| 409 | "Patient ID already exists." | Duplicate patient ID |

**Security Features:**
- Input sanitization
- Type validation
- Range checking
- SQL injection prevention
- XSS protection

---

### Update Patient

**Endpoint:** `POST /patient/edit/<int:patient_id>`

**Description:** Update existing patient record

**Authentication:** Required

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| patient_id | integer | Yes | Patient to update |

**Body Parameters:** Same as Add Patient (except patient_id cannot be changed)

**Example Request:**
```http
POST /patient/edit/99999 HTTP/1.1
Host: localhost:5000
Cookie: session=<session_token>
Content-Type: application/x-www-form-urlencoded

gender=Male&age=46&hypertension=0&heart_disease=0&...
```

**Success Response:**
```
Status: 302 Redirect to /patients
Flash Message: "Patient record updated successfully!"
```

**Error Responses:**

| Status | Message | Reason |
|--------|---------|--------|
| 404 | "Patient not found." | Invalid patient ID |
| 400 | Validation errors | Invalid input data |

**Metadata Updated:**
- `updated_at`: Current timestamp
- `updated_by`: Current user's username

---

### Delete Patient

**Endpoint:** `POST /patient/delete/<int:patient_id>`

**Description:** Delete patient record permanently

**Authentication:** Required

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| patient_id | integer | Yes | Patient to delete |

**Example Request:**
```http
POST /patient/delete/99999 HTTP/1.1
Host: localhost:5000
Cookie: session=<session_token>
```

**Success Response:**
```
Status: 302 Redirect to /patients
Flash Message: "Patient record deleted successfully."
```

**Error Responses:**

| Status | Message | Reason |
|--------|---------|--------|
| 404 | "Patient not found." | Invalid patient ID |

**Security Features:**
- Confirmation required in UI
- Action logged
- User attribution
- Cannot be undone

---

## Analytics

### View Analytics Dashboard

**Endpoint:** `GET /analytics`

**Description:** Retrieve data analytics and visualizations

**Authentication:** Required

**Example Request:**
```http
GET /analytics HTTP/1.1
Host: localhost:5000
Cookie: session=<session_token>
```

**Success Response:**
```json
Status: 200 OK

{
  "gender_dist": [
    {"_id": "Male", "count": 2994},
    {"_id": "Female", "count": 2115},
    {"_id": "Other", "count": 1}
  ],
  "age_groups": [
    {"_id": "0-20", "count": 104, "stroke_count": 0},
    {"_id": "20-40", "count": 1581, "stroke_count": 18},
    {"_id": "40-60", "count": 2044, "stroke_count": 73},
    {"_id": "60-80", "count": 1276, "stroke_count": 140},
    {"_id": "80+", "count": 105, "stroke_count": 18}
  ],
  "smoking_stroke": [
    {"_id": "never smoked", "count": 1892, "stroke_count": 87},
    {"_id": "formerly smoked", "count": 885, "stroke_count": 71},
    {"_id": "smokes", "count": 789, "stroke_count": 46},
    {"_id": "Unknown", "count": 1544, "stroke_count": 45}
  ],
  "health_correlation": [
    {
      "_id": {"hypertension": 0, "heart_disease": 0},
      "count": 4169,
      "stroke_count": 153
    },
    {
      "_id": {"hypertension": 1, "heart_disease": 0},
      "count": 498,
      "stroke_count": 59
    },
    {
      "_id": {"hypertension": 0, "heart_disease": 1},
      "count": 338,
      "stroke_count": 26
    },
    {
      "_id": {"hypertension": 1, "heart_disease": 1},
      "count": 105,
      "stroke_count": 11
    }
  ]
}
```

**Data Visualizations:**
- Gender Distribution (Pie Chart)
- Stroke by Age Group (Bar Chart)
- Smoking Status (Doughnut Chart)
- Health Conditions (Bar Chart)

---

## Admin Functions

### View All Users

**Endpoint:** `GET /admin/users`

**Description:** View all registered users (admin only)

**Authentication:** Required (Admin role)

**Example Request:**
```http
GET /admin/users HTTP/1.1
Host: localhost:5000
Cookie: session=<session_token>
```

**Success Response:**
```json
Status: 200 OK

{
  "users": [
    {
      "id": 1,
      "username": "admin",
      "email": "admin@hospital.com",
      "is_admin": true,
      "created_at": "2025-12-01T00:00:00",
      "last_login": "2025-12-01T15:30:00"
    },
    {
      "id": 2,
      "username": "johndoe",
      "email": "john@example.com",
      "is_admin": false,
      "created_at": "2025-12-01T10:00:00",
      "last_login": "2025-12-01T14:00:00"
    }
  ]
}
```

**Error Responses:**

| Status | Message | Reason |
|--------|---------|--------|
| 403 | "Admin privileges required to access this page." | Non-admin user |

---

## Error Handling

### Standard Error Pages

#### 404 Not Found

**Example Response:**
```http
HTTP/1.1 404 Not Found
Content-Type: text/html

Custom 404 error page displayed
```

#### 403 Forbidden

**Example Response:**
```http
HTTP/1.1 403 Forbidden
Content-Type: text/html

Custom 403 error page displayed
```

#### 500 Internal Server Error

**Example Response:**
```http
HTTP/1.1 500 Internal Server Error
Content-Type: text/html

Custom 500 error page displayed
Error logged to security.log
```

### Flash Messages

Flash messages are displayed using Bootstrap alerts:

**Categories:**
- `success`: Green alert for successful operations
- `danger`: Red alert for errors
- `warning`: Yellow alert for warnings
- `info`: Blue alert for informational messages

---

## Data Models

### User Model (SQLite)

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    is_admin BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);
```

**Indexes:**
- PRIMARY KEY on `id`
- UNIQUE on `username`
- UNIQUE on `email`

### Patient Model (MongoDB)

```javascript
{
  _id: ObjectId,                    // MongoDB automatic ID
  id: Integer,                      // Patient unique ID (indexed, unique)
  gender: String,                   // "Male", "Female", "Other"
  age: Float,                       // 0-120
  hypertension: Integer,            // 0 or 1
  heart_disease: Integer,           // 0 or 1
  ever_married: String,             // "Yes", "No"
  work_type: String,                // Work category
  Residence_type: String,           // "Urban", "Rural"
  avg_glucose_level: Float,         // 0-500 mg/dL
  bmi: Float | String,              // 10-100 or "N/A"
  smoking_status: String,           // Smoking category
  stroke: Integer,                  // 0 or 1 (indexed)
  created_at: ISODate,              // Record creation timestamp
  updated_at: ISODate,              // Last update timestamp
  created_by: String,               // Username who created
  updated_by: String                // Username who last updated
}
```

**Indexes:**
- `id`: unique, ascending
- `age`: ascending
- `stroke`: ascending
- `created_at`: descending

---

## Security Considerations

### Authentication & Authorization

1. **Session Management**
   - HTTPOnly cookies prevent XSS
   - SameSite attribute prevents CSRF
   - 2-hour session timeout
   - Strong session protection

2. **Password Security**
   - Bcrypt hashing with salt
   - Minimum password requirements enforced
   - No plain-text storage
   - Secure password comparison

3. **Input Validation**
   - Server-side validation on all inputs
   - Type checking
   - Range validation
   - SQL injection prevention
   - XSS prevention

4. **CSRF Protection**
   - Flask-WTF tokens on all POST requests
   - Automatic token validation
   - Token expiration

5. **Rate Limiting**
   - Login attempts limited to 5 per minute
   - Prevents brute force attacks
   - Failed attempts logged

### Data Protection

1. **Database Security**
   - Parameterized queries prevent SQL injection
   - MongoDB connection authentication
   - Encrypted connections
   - Access control

2. **Audit Logging**
   - All security events logged
   - User actions tracked
   - Timestamps recorded
   - Log rotation configured

---

## Rate Limits

| Endpoint | Limit | Window |
|----------|-------|--------|
| POST /login | 5 requests | 1 minute |
| POST /register | 3 requests | 1 hour |
| All others | 200 requests | 1 day |

---

## HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful GET request |
| 302 | Found | Redirect after successful POST |
| 400 | Bad Request | Validation error, malformed request |
| 401 | Unauthorized | Authentication required or failed |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Duplicate resource (e.g., username) |
| 500 | Internal Server Error | Server-side error |

---

## Testing the API

### Using cURL

**Login Example:**
```bash
curl -X POST http://localhost:5000/login \
  -d "username=admin&password=admin123" \
  -c cookies.txt \
  -L
```

**Get Dashboard:**
```bash
curl -X GET http://localhost:5000/dashboard \
  -b cookies.txt
```

**Add Patient:**
```bash
curl -X POST http://localhost:5000/patient/add \
  -b cookies.txt \
  -d "patient_id=99999&gender=Male&age=45&..." \
  -L
```

### Using Python Requests

```python
import requests

# Login
session = requests.Session()
response = session.post(
    'http://localhost:5000/login',
    data={'username': 'admin', 'password': 'admin123'}
)

# Get patients
response = session.get('http://localhost:5000/patients')
print(response.text)

# Add patient
patient_data = {
    'patient_id': 99999,
    'gender': 'Male',
    'age': 45,
    # ... other fields
}
response = session.post(
    'http://localhost:5000/patient/add',
    data=patient_data
)
```

---

## Changelog

### Version 1.0.0 (December 2025)
- Initial API release
- User authentication endpoints
- Patient CRUD operations
- Analytics endpoints
- Admin functionality
- Comprehensive security features

---

## Support

For API support or questions:
- Email: api-support@your-domain.com
- Documentation: https://your-domain.com/docs
- GitHub Issues: https://github.com/yourusername/stroke-prediction-system/issues

---

**API Documentation Version**: 1.0  
**Last Updated**: December 2025  
**Application Version**: 1.0.0

---

*This API is designed for internal use and integration. External access requires additional authentication mechanisms.*













