# COMP2913 Team 17: Antiques & Collectibles Auction System

## Overview

This project implements an online auction platform specialised for antiques and collectibles. The system allows users to buy and sell items through a competitive bidding process, with built-in authentication services for verifying item authenticity.

For more detailed documentation, please visit the [Wiki](https://github.com/COMP2913-24-25/comp2913-team17/wiki).

## Core Features

- User auction management (bidding, selling, tracking)
- Item authentication system
- Multi-role user system (Users, Experts, Managers)
- Real-time notifications
- Search and discovery tools

## System Architecture

The application follows a three-tier architecture with a web-based interface, backend server, and database system. It's designed to handle multiple simultaneous users and real-time updates.

## Project Management
This project utilises GitHub's built-in tools for development tracking:

- Issues for task management
- Labels for releases
- Wiki for documentation
- Projects for sprint planning
- Actions for continuous integration

## Installation Instructions

## Running the Application

1. Insert an environment variable file named '.env' in the project root directory.
   This should be in the following format:

```bash
SECRET_KEY=
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
AWS_ACCESS_KEY=
AWS_SECRET_KEY=
AWS_BUCKET=
EMAIL_USER=
EMAIL_PASSWORD=
```

2. Create your virtual environment:

```bash
python3 -m venv myenv
```

3. Activate your virtual environment:
```bash
# For Windows Command Prompt
myenv\Scripts\activate

# For Windows PowerShell
.\myenv\Scripts\Activate.ps1

# For Linux/MacOS
source myenv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run Flask application:
```bash
# For production:
set FLASK_ENV=production # Command Prompt
$env:FLASK_ENV="production" # PowerShell
export FLASK_ENV=production # Linux/MacOS

flask run

# For development mode with debugging:
set FLASK_ENV=development # Command Prompt
$env:FLASK_ENV="development" # PowerShell
export FLASK_ENV=development # Linux/MacOS

flask run
```

5. Access the application:
- Open browser at: http://localhost:5000
- New feature at: http://localhost:5000/new-feature

# Security Features

## 1. Authentication
The application uses a secure authentication system to protect user accounts and data:

- OAuth integration: Uses Google OAuth 2.0 support for secure third-party authentication (`OAuthSignIn` classes)

Can be configured in `__init__.py` file

## 2. Password Policy
The application enforces strong password requirements (`RegisterForm`) to prevent common security issues:

- Length: Passwords between 8 and 24 characters
- Complexity: Requires at least one uppercase letter, one lowercase letter, one digit, and one special character
- Password Confirmation: Prevent mistyped passwords by requiring users to confirm their password
- Password Storage: Uses Werkzeug's `generate_password_hash` and `check_password_hash` to securely store passwords in the database (`models.py`)

## 3. Rate Limiting
The application implements rate limiting to protect against brute force attacks and API abuse:

- Login: Limited to 10 attempts per minute per IP address and 5 attempts per minute per account
- Registration: Limited to 5 attempts per hour and 20 per day per IP address
- Account updates: Limited to 10 attempts per hour per IP address
- OAuth operations: Limited to 10 per hour per IP address

Rate limits can be configured in the `limiter_utils.py` file.

## 4. CSRF Protection
The application implements comprehensive Cross-Site Request Forgery (CSRF) protection:

- **Server-Side Implementation**: Uses Flask-WTF's CSRFProtect extension (`extensions.py`) to generate and validate tokens
- **Form-Based Protection**: Each HTML form includes a hidden CSRF token: `{{ form.csrf_token }}`
- **AJAX Protection**: JavaScript utility `csrf.js` automatically adds CSRF tokens to all AJAX requests.

This protection ensures that all state-changing operations (POST, PUT, DELETE) require a valid CSRF token, preventing attackers from tricking users into submitting unauthorized requests.

## 5. WebSocket Security
The application implements security measures for WebSocket connections:

- **Authentication Required**: Socket connections are authenticated using the same session as HTTP requests
- **Room-based Authorization**: Users can only join rooms they have permission to access
- **Origin Validation**: WebSockets validate connection origins to prevent cross-site WebSocket hijacking
- **Connection Scope Limitation**: Users can only access resources they're authorized to via scoped room membership

## 6. File Upload Security
The application includes comprehensive file upload security mechanisms:

- **File Type Validation**: Only permitted file extensions are allowed
- **File Size Limits**: Maximum size for uploaded files is enforced
- **Secure Filename Processing**: Sanitizing filenames to prevent directory traversal attacks
- **External Storage**: Files are stored in AWS S3 rather than on the local filesystem
- **Private File Access**: Authentication required with temporary signed URLs for accessing sensitive files

## 7. Authorization
The application implements a robust authorization system:

- **Role-based Access Control**: Three-tier user roles system
- **Function-level Authorization**: Routes check appropriate role permissions
- **Resource Ownership Verification**: Users can only modify their own resources
- **Granular Permissions**: Specific permissions for auction items, bids, authentication requests, etc.

## 8. Account Lockout
The application implements account lockout mechanisms to prevent brute force attacks:

- **Progressive Lockout**: After 5 failed login attempts, the account is locked temporarily
- **Account Recovery**: Automatic account unlocking after a set time period (15 minutes)
- **Login Attempt Tracking**: Failed login attempts are tracked in the database
- **Failed Attempt Reset**: Counter is reset upon successful login

## 9. Secure Cookies
The application enforces secure cookie policies:

- **HTTP-Only Cookies**: Session cookies are set with the HttpOnly flag to prevent JavaScript access
- **Secure Flag**: Cookies are only transmitted over HTTPS when in production
- **SameSite Policy**: Cookies use `SameSite=Lax` to prevent CSRF attacks
- **Session Timeout**: Sessions expire after a period of inactivity
- **Session Invalidation**: On logout, sessions are properly invalidated and cookies cleared

## 10. Security Scripts
The application includes automated security tools and scripts:

- **Bandit Static Analysis**: Automated security scanning of Python code
- **Pre-commit Hooks**: Security checks run automatically before git commits
- **Security Reporting**: Security issues are automatically reported and logged
- **Vulnerability Scanning**: Regular scanning for known vulnerabilities in dependencies
- **Security Header Configuration**: Proper security headers setup (HSTS, CSP, etc.)

# How to add more features and test them

## Project Structure (Not finalised yet)
```
bidding_project/
├── main/
│   ├── __init__.py
│   ├── admin_page/
│   ├── bidding_page/
│   ├── home_page/
│   ├── item_page/
│   └── user_page/
├── tests/
├── app.py
└── README.md
```

## Adding New Features

### 1. Create Blueprint Structure
Create a new directory in `main/` with the following structure:
```
new_feature_page/
├── __init__.py
├── routes.py
├── static/
│   └── style.css
└── templates/
    └── new_feature.html
```

### 2. Set Up Blueprint
In `new_feature_page/__init__.py`:
```python
from flask import Blueprint

new_feature_page = Blueprint('new_feature_page', __name__,
                           template_folder='templates',
                           static_folder='static')

from . import routes
```

### 3. Create Routes
In `new_feature_page/routes.py`:
```python
from flask import render_template
from . import new_feature_page

@new_feature_page.route('/')
def index():
    return render_template('new_feature.html')
```

### 4. Create Template
In `new_feature_page/templates/new_feature.html`:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>New Feature</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <h1>New Feature Page</h1>
</body>
</html>
```

### 5. Register Blueprint
In `main/__init__.py`:
```python
from .new_feature_page import new_feature_page
app.register_blueprint(new_feature_page, url_prefix='/new-feature')
```

## Testing Features

### 1. Create Test Structure
```
tests/
├── __init__.py
├── conftest.py
└── test_new_feature.py
```

### 2. Configure Tests
In `tests/conftest.py`:
```python
import pytest
from main import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
```

### 3. Write Tests
In `tests/test_new_feature.py`:
```python
def test_new_feature_page(client):
    response = client.get('/new-feature/')
    assert response.status_code == 200
    assert b'New Feature Page' in response.data
```
### Optional: Create a virtual environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate # Linux

venv\Scripts\activate # Windows
```

### 4. Run Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_new_feature.py

# Run with coverage
pytest --cov=main tests/

# Run with coverage and fail if coverage is below 80% (or any other value)
pytest --cov=main tests/ --cov-fail-under=80
```

## Code Quality and Security Tools

### Flake8
Flake8 is a Python linting tool that checks your code against coding style (PEP 8), programming errors (like "library imported but unused" and "variable declared but not used"), and cyclomatic complexity.

1. Install Flake8:
```bash
pip install flake8
```

2. Run Flake8:
```bash
# Check all Python files
flake8 .

# Check specific file
flake8 main/routes.py

# Run with specific configurations
flake8 --max-line-length=120 --exclude=venv/
```

3. Common configurations (add to `setup.cfg` or `tox.ini`):
```ini
# filepath: /c:/Users/User/OneDrive/Desktop/bidding_project/setup.cfg
[flake8]
max-line-length = 120
exclude = venv/,__pycache__/
ignore = E203, W503
```

### Bandit
Bandit is a security linter designed to find common security issues in Python code.

1. Install Bandit:
```bash
pip install bandit
```

2. Basic Usage:
```bash
# Scan all Python files
bandit -r .

# Scan specific file
bandit main/routes.py

# Generate HTML report
bandit -r . -f html -o security-report.html
```

3. Enhanced Security Scanning:
```bash
# Install the security scanning tools
pip install bandit

# Run the comprehensive security scan
python scripts/security_scan.py

# Install Git pre-commit hook for automatic scanning
python scripts/install_hooks.py
```

4. Understanding Bandit Configuration:
   - `bandit.yaml` contains comprehensive settings for security scanning
   - The scan checks for SQL injections, command injections, weak cryptography, etc.
   - Security reports are generated in both JSON and HTML formats
   - High-severity issues will prevent commits when using the pre-commit hook

5. Common Security Issues to Watch For:
   - SQL Injection: Avoid string formatting in queries, use parameterized queries
   - Command Injection: Never use user input directly in system commands
   - Weak Cryptography: Avoid outdated hashing algorithms (MD5, SHA1)
   - Hard-coded Secrets: Never store API keys, passwords or tokens in code
   - Cross-Site Scripting: Always escape user input in templates

### Adding to Development Workflow

1. Add to requirements:
```bash
# filepath: /c:/Users/User/OneDrive/Desktop/bidding_project/requirements-dev.txt
flake8>=6.1.0
bandit>=1.7.5
```

2. Run as part of test suite:
```bash
# Run all quality checks
flake8 . && bandit -r . && pytest
```

3. VS Code Integration:
Install the "Python" extension in VS Code and add to settings.json:
```json
{
    "python.linting.flake8Enabled": true,
    "python.linting.enabled": true,
    "python.linting.banditEnabled": true
}
```

## Useful Links

[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/IsXyYN_x)

[![Open in Codespaces](https://classroom.github.com/assets/launch-codespace-2972f46106e565e64193e422d61a12cf1da4916b45550586e14ef0a7c637dd04.svg)](https://classroom.github.com/open-in-codespaces?assignment_repo_id=18092142)

- https://www.freecodecamp.org/news/how-to-use-blueprints-to-organize-flask-apps/
- https://flask.palletsprojects.com/en/2.0.x/tutorial/tests/
- https://flask.palletsprojects.com/en/2.0.x/blueprints/
