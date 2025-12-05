# Stroke Prediction Management System

A secure, full-featured web application for managing and analyzing stroke prediction patient data using Flask, SQLite, and MongoDB.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)
![MongoDB](https://img.shields.io/badge/MongoDB-4.0+-brightgreen.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Security Features](#security-features)
- [Technology Stack](#technology-stack)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Running Tests](#running-tests)
- [Project Structure](#project-structure)
- [Usage Guide](#usage-guide)
- [Database Schema](#database-schema)
- [Security Best Practices](#security-best-practices)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

The Stroke Prediction Management System is a professional-grade web application designed for healthcare providers to securely manage and analyze patient stroke prediction data. The system implements industry-standard security practices and provides an intuitive interface for CRUD operations on patient records.

## ✨ Features

### Core Functionality
- **User Authentication & Authorization**
  - Secure user registration and login
  - Password strength validation
  - Session management with timeout
  - Role-based access control (Admin/User)

- **Patient Data Management (CRUD Operations)**
  - Add new patient records with comprehensive validation
  - View detailed patient information with risk assessment
  - Update existing patient records
  - Delete patient records with confirmation
  - Search and filter capabilities
  - Pagination for large datasets

- **Data Analytics & Visualization**
  - Interactive charts and graphs using Chart.js
  - Gender distribution analysis
  - Age group stroke correlation
  - Smoking status impact analysis
  - Health condition correlation studies

- **Dashboard & Reporting**
  - Real-time statistics overview
  - Recent patient records display
  - Risk assessment indicators
  - Health metrics visualization

### Advanced Features
- **Multi-Database Architecture**
  - SQLite for user authentication and session data
  - MongoDB for patient records and medical data
  - Efficient data separation for security and scalability

- **Responsive Design**
  - Mobile-friendly interface
  - Bootstrap 5 for modern UI components
  - Custom CSS for enhanced user experience
  - Cross-browser compatibility

## 🔒 Security Features

The application implements multiple layers of security to protect sensitive healthcare data:

### 1. **Password Security**
- Bcrypt hashing with salt for password storage
- Password strength validation (minimum 8 characters, uppercase, lowercase, numbers)
- Secure password reset mechanism
- No plain-text password storage

### 2. **Input Validation & Sanitization**
- Server-side validation for all user inputs
- XSS (Cross-Site Scripting) prevention
- SQL injection prevention through parameterized queries
- Input sanitization for special characters
- Type checking and range validation

### 3. **Session Security**
- Secure session handling with Flask-Login
- HTTPOnly cookies to prevent XSS attacks
- Session timeout after inactivity
- CSRF (Cross-Site Request Forgery) protection via Flask-WTF
- Session protection level set to 'strong'

### 4. **Data Protection**
- Encrypted database connections
- Secure data transmission
- Access control and authorization
- Audit logging for security events

### 5. **Additional Security Measures**
- Security headers implementation
- Error handling without information leakage
- Rate limiting capabilities
- Secure file handling
- Environment variable management for sensitive configuration

## 🛠 Technology Stack

### Backend
- **Flask 3.0.0** - Python web framework
- **Flask-Login 0.6.3** - User session management
- **Flask-WTF 1.2.1** - CSRF protection and form handling
- **Python 3.8+** - Programming language

### Databases
- **SQLite** - User authentication and session data
- **MongoDB 4.0+** - Patient records and medical data
- **PyMongo 4.6.0** - MongoDB driver for Python

### Security
- **bcrypt 4.1.2** - Password hashing
- **WTForms 3.1.1** - Form validation

### Data Processing
- **Pandas 2.1.4** - Data manipulation and analysis

### Frontend
- **Bootstrap 5.3** - UI framework
- **Chart.js 4.4** - Data visualization
- **Font Awesome 6.4** - Icons
- **Custom CSS/JS** - Enhanced user experience

## 💻 System Requirements

- Python 3.8 or higher
- MongoDB 4.0 or higher
- 4GB RAM minimum
- 1GB free disk space
- Modern web browser (Chrome, Firefox, Safari, Edge)

## 📦 Installation

### Step 1: Clone or Download the Repository

```bash
# If using Git
git clone https://github.com/yourusername/stroke-prediction-system.git
cd stroke-prediction-system

# Or download and extract the ZIP file
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Install and Start MongoDB

**Windows:**
1. Download MongoDB from https://www.mongodb.com/try/download/community
2. Install MongoDB using the installer
3. Start MongoDB service:
   ```bash
   net start MongoDB
   ```

**macOS (using Homebrew):**
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install mongodb
sudo systemctl start mongodb
sudo systemctl enable mongodb
```

### Step 5: Verify MongoDB Installation

```bash
# Check if MongoDB is running
mongosh --eval "db.version()"
```

## ⚙ Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here-change-in-production
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB=stroke_prediction
FLASK_ENV=development
```
This project uses GitHub repository secrets for the MongoDB Atlas connection. For local development:

### Database Configuration

The application will automatically:
- Create SQLite database (`users.db`) on first run
- Create default admin user (username: `admin`, password: `admin123`)
- Load patient data from CSV into MongoDB
- Create necessary indexes for performance

## 🚀 Running the Application

### Start the Application

```bash
python app.py
```

The application will be available at: **http://localhost:5000**

### Default Login Credentials

- **Username:** `admin`
- **Password:** `admin123`

⚠️ **Important:** Change the default admin password immediately after first login in a production environment.

## 🧪 Running Tests

### Run All Tests

```bash
python test_app.py
```

### Test Coverage

The test suite includes:
- ✅ Security function tests (input sanitization, validation)
- ✅ Password hashing and verification tests
- ✅ Patient data validation tests
- ✅ Flask route and authentication tests
- ✅ XSS and SQL injection prevention tests
- ✅ User registration and login tests

### Expected Output

```
Test Security Functions ... OK
Test Patient Data Validation ... OK
Test Flask Application ... OK
Test Password Hashing ... OK
Test Input Sanitization ... OK

======================================================================
TEST SUMMARY
======================================================================
Tests Run: 25
Successes: 25
Failures: 0
Errors: 0
======================================================================
```

## 📁 Project Structure

```
stroke-prediction-system/
│
├── app.py                          # Main Flask application
├── test_app.py                     # Comprehensive unit tests
├── requirements.txt                # Python dependencies
├── .gitignore                      # Git ignore rules
│
├── healthcare-dataset-stroke-data.csv  # Patient dataset
│
├── templates/                      # HTML templates
│   ├── base.html                  # Base template with navigation
│   ├── login.html                 # User login page
│   ├── register.html              # User registration page
│   ├── dashboard.html             # Main dashboard
│   ├── patients.html              # Patient list with search
│   ├── add_patient.html           # Add new patient form
│   ├── edit_patient.html          # Edit patient form
│   ├── view_patient.html          # Patient detail view
│   ├── analytics.html             # Data analytics page
│   ├── admin_users.html           # User management (admin)
│   ├── 404.html                   # 404 error page
│   ├── 403.html                   # 403 error page
│   └── 500.html                   # 500 error page
│
├── static/                         # Static files
│   ├── css/
│   │   └── style.css              # Custom CSS styles
│   └── js/
│       └── main.js                # Custom JavaScript
│
└── users.db                        # SQLite database (auto-generated)
```

## 📖 Usage Guide

### 1. User Registration

1. Navigate to the registration page
2. Enter username (minimum 3 characters)
3. Enter valid email address
4. Create strong password (min 8 chars, uppercase, lowercase, number)
5. Confirm password
6. Click "Register"

### 2. User Login

1. Navigate to login page
2. Enter your username and password
3. Click "Login"
4. You'll be redirected to the dashboard

### 3. Dashboard Overview

The dashboard displays:
- Total patient count
- Stroke cases count
- Non-stroke cases count
- Average patient age
- Recent patient records

### 4. Managing Patients

**Adding a Patient:**
1. Click "Add Patient" in navigation or dashboard
2. Fill in all required fields:
   - Patient ID (unique)
   - Gender
   - Age
   - BMI (optional)
   - Average glucose level
   - Hypertension (Yes/No)
   - Heart disease (Yes/No)
   - Marital status
   - Work type
   - Residence type
   - Smoking status
   - Stroke (Yes/No)
3. Click "Save Patient"

**Viewing Patient Details:**
1. Go to "Patients" page
2. Click the eye icon (👁) next to any patient
3. View comprehensive patient information and risk assessment

**Editing a Patient:**
1. Go to "Patients" page
2. Click the edit icon (✏️) next to the patient
3. Modify the required fields
4. Click "Update Patient"

**Deleting a Patient:**
1. Go to "Patients" page
2. Click the delete icon (🗑️) next to the patient
3. Confirm deletion in the modal dialog

**Searching and Filtering:**
1. Use the search bar to find patients by ID, gender, work type
2. Filter by stroke status (Yes/No/All)
3. Filter by gender (Male/Female/Other/All)
4. Click "Filter" to apply

### 5. Analytics

View interactive charts and statistics:
- Gender distribution pie chart
- Stroke cases by age group
- Smoking status correlation
- Health conditions impact
- Detailed statistics table

### 6. Admin Functions

Admin users can:
- View all registered users
- Monitor user activity
- Access system logs
- Manage user permissions

## 🗄 Database Schema

### SQLite (users.db)

**users table:**
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

### MongoDB (stroke_prediction)

**patients collection:**
```javascript
{
    _id: ObjectId,
    id: Integer (unique patient ID),
    gender: String,
    age: Float,
    hypertension: Integer (0 or 1),
    heart_disease: Integer (0 or 1),
    ever_married: String,
    work_type: String,
    Residence_type: String,
    avg_glucose_level: Float,
    bmi: Float or "N/A",
    smoking_status: String,
    stroke: Integer (0 or 1),
    created_at: DateTime,
    updated_at: DateTime,
    created_by: String (username)
}
```

## 🛡 Security Best Practices

### For Deployment

1. **Change Default Credentials**
   - Immediately change admin password
   - Use strong, unique passwords

2. **Environment Variables**
   - Never commit `.env` file to version control
   - Use environment-specific configurations
   - Generate strong SECRET_KEY

3. **HTTPS Configuration**
   - Enable SSL/TLS in production
   - Set SESSION_COOKIE_SECURE = True
   - Use secure MongoDB connections

4. **Database Security**
   - Enable MongoDB authentication
   - Use strong database passwords
   - Restrict database access by IP
   - Regular database backups

5. **Application Security**
   - Keep dependencies updated
   - Monitor security logs
   - Implement rate limiting
   - Regular security audits

6. **Network Security**
   - Use firewall rules
   - Restrict port access
   - Use VPN for sensitive operations

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Code Standards

- Follow PEP 8 style guide for Python code
- Add comprehensive comments
- Write unit tests for new features
- Update documentation as needed

## Reference
- Documentation: https://github.com/yourusername/stroke-prediction-system/wiki

## 🙏 Acknowledgments

- Flask framework and community
- MongoDB team
- Bootstrap contributors
- Chart.js developers
- Healthcare dataset providers
- Open-source community

## 📊 Version History

### Version 1.0.0 (2025)
- Initial release
- User authentication system
- CRUD operations for patient data
- Data analytics and visualization
- Comprehensive security features
- Unit testing suite
- Full documentation

---

**Built with ❤️ for Healthcare Data Management**

**Note:** This application is designed for educational and demonstration purposes. For production healthcare environments, ensure compliance with HIPAA, GDPR, and other relevant healthcare data regulations.

