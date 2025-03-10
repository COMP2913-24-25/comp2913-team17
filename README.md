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

2. Run Bandit:
```bash
# Scan all Python files
bandit -r .

# Scan specific file
bandit main/routes.py

# Generate HTML report
bandit -r . -f html -o security-report.html
```

3. Common configurations (add to `bandit.yaml`):
```yaml
# filepath: /c:/Users/User/OneDrive/Desktop/bidding_project/bandit.yaml
exclude_dirs: ['tests', 'venv']
skips: ['B311']  # Standard pseudo-random generators are not suitable for security/cryptographic purposes
```

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
