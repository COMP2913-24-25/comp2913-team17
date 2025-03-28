# COMP2913 Team 17: Antiques & Collectibles Auction System

## Project Description

This project implements an online auction platform specialised for antiques and collectibles. The system allows users to buy and sell items through a competitive bidding process, with built-in authentication services for verifying item authenticity.

![Screenshot of the Vintage Vault homepage](homepage.png)

For more detailed documentation, please visit the [Wiki](https://github.com/COMP2913-24-25/comp2913-team17/wiki).

You can access a live version of the application [here](https://vintage-vault-aesv.onrender.com/).

## Table of Contents
1. [Description](#project-description)
2. [Installation](#installation)
3. [Usage](#usage)
4. [Technology Stack](#technology-stack)
5. [Tests](#tests)
6. [Credits](#credits)
7. [How to Contribute](#how-to-contribute)

## Installation

1. Insert an environment variable file named `.env` in the project root directory.
   This should be in the following format with the key values filled in:

```bash
SECRET_KEY=
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
AWS_ACCESS_KEY=
AWS_SECRET_KEY=
AWS_BUCKET=
AWS_REGION=
EMAIL_USER=
EMAIL_PASSWORD=
STRIPE_PUBLISHABLE_KEY=
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
```

2. Create your virtual environment (optional but recommended):

```bash
python3 -m venv myenv
```

3. Activate your virtual environment (optional but recommended):
```bash
# For Linux/MacOS
source myenv/bin/activate

# For Windows Command Prompt
myenv\Scripts\activate

# For Windows PowerShell
.\myenv\Scripts\Activate.ps1
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Run the Flask application in development mode:
```bash
flask run --debug
```

By default, the application will use an existing SQLite database file named `database.db` in the main directory. If this file is not present, the application will create a new database file populated with dummy data. To run the application with no initial data, use the following command:

```bash
# For Linux/MacOS
EMPTY_DB=1 flask run --debug

# For Windows Command Prompt
set EMPTY_DB=1 && flask run --debug

# For Windows PowerShell
$env:EMPTY_DB=1; flask run --debug
```
6. Set Up Stripe

To accomodate payments, you will need to install Stripe CLI, instructions can be found [here](https://docs.stripe.com/stripe-cli). Once you have set up Stripe CLI and populated the `.env` file with your Stripe API keys, you will need to run the following command in a separate terminal window to forward Stripe events to your local server:

```bash
stripe listen --forward-to http://127.0.0.1:5000/item/stripe-webhook
```

7. Access the application:
- Open the browser at: http://localhost:5000

## Usage

### Features

| Feature                            | Description                                                                                                         |
|------------------------------------|---------------------------------------------------------------------------------------------------------------------|
| **🧑‍💻 Account Creation**           | Users can create accounts using their email and sign in with Google, allowing them to create and bid on auctions.  |
| **📦 Listing Items**               | Sellers can list items for auction, with durations up to 5 days by default.                                                   |
| **💰 Bidding and Payment**         | Buyers can submit bids for a minimum of 1p above the current bid price. When a buyer wins an auction, they are instructed to complete payment by entering their card details, or choosing a saved card if this has been opted for before. |
| **🔔 Notification System**         | Notifications are rendered in the browser for significant events such as account creation, winning bids, and payment prompts. Some important notifications are also sent via email to keep users who are not currently browsing the site up to date. |
| **🧑‍🔬 Experts**                   | "Expert" is a role for users who are able to authenticate items for given categories. These users are not able to bid on items and may only authenticate items they are assigned to. |
| **⏰ Expert Availability**         | Experts can mark themselves as available/unavailable for work at various dates and times. This prevents an expert from being assigned to authenticate an item when they are not available. |
| **📑 Authentication Requests**    | Sellers can request their items be authenticated by a designated Expert. This is supplemented by a Seller/Expert messaging system, where the seller can provide more details/photos at the expert's request. When an item is authenticated, the auction for it will feature an authenticated badge for buyer confidence. |
| **👨‍💼 Managers**                  | "Manager" is a dedicated role for  Vintage Vault administrators, giving them access to user roles, platform statistics, and site configuration options.        |
| **⚙️ Manager Options**             | In the management dashboard, a manager can update the roles of users in real time. Managers are also tasked with assigning experts to auctions with pending authentication requests. This can be set manually, or auto-assigned based on a recommendation algorithm which considers the niche of the expert and their availability. |
| **📊 Platform Statistics/Configuration** | Managers can view sales information for the platform over a period of up to 6 months. Visible statistics include the number of paid auctions, projected revenue, commission income, and other relevant data to help with the platform's performance monitoring. Additionally, managers may update the platform fee percentages as well as the maximum auction duration possible for future listings. |

## Technology Stack
### **Frontend**

- [jQuery](https://jquery.com/) - Simplifies event handling, DOM manipulation, and AJAX requests, enabling real-time updates and dynamic interactions on the frontend.

- [Bootstrap](https://getbootstrap.com/) - For responsive styling and maintaining accessibility for mobile users.

### **Backend**

- [Flask](https://flask.palletsprojects.com/en/stable/) - A lightweight web application framework.

- [SQLAlchemy](https://www.sqlalchemy.org/) - An SQL toolkit and ORM for Python.

- [SQLite](https://www.sqlite.org/index.html) - A C library that provides a lightweight disk-based database.

- [PostgreSQL](https://www.postgresql.org/) - An open-source relational database management system, used with the deployed application.

### **Testing**

- [pytest](https://docs.pytest.org/en/stable/) - Facilitates writing and running Python tests for the backend.

### APIs

- [Stripe](https://stripe.com/gb) - Secure handling of payments.

- [Google OAuth](https://developers.google.com/identity/protocols/oauth2) - For user authentication and account creation.

- [Google Mail](https://developers.google.com/gmail/api) - For sending emails.

- [AWS S3](https://aws.amazon.com/s3/) - For storing images and other static files.

### Deployment

- [Render](https://render.com/) - A cloud platform for hosting web applications.

## Tests

Testing is encouraged for all features as it allows us to maintain the integrity of the site and catch bugs early. The following commands will allow you to run the project's unit tests:

```bash
# Run all tests
pytest

# Run a specific test file
pytest tests/test_feature.py
```

## Credits

### Contributors
- [@itsuf](https://github.com/itsuf)
- [@jkhwarazmi](https://github.com/jkhwarazmi)
- [@ldarnbr](https://github.com/ldarnbr)
- [@nabiljefferson98](https://github.com/nabiljefferson98)
- [@Nadia8844](https://github.com/Nadia8844)
- [@zakwanmalik](https://github.com/zakwanmalik)

### Coordinator
- [@abbeloe](https://github.com/abbeloe)

### Organization
- [University of Leeds](https://github.com/enterprises/the-university-of-leeds)

## How to contribute

Contributions after the final assessment deadline are welcome! To contribute, follow these steps to ensure your changes can be properly reviewed and integrated.

1. Create a Fork

This can be done using the button at the top right of the [project homepage](https://github.com/COMP2913-24-25/comp2913-team17). Forking allows you to experiment with the project without affecting the original repository.

2. Clone Your Fork

To create a local copy of your fork, use this command:
```
git clone https://github.com/yourusername/repo-name
```

3. Create a Branch

```bash
git checkout -b <issueId-issueDescription>
```

4. Push Your Changes

This project follows the conventional commit structure, please see the [coding style guide](https://github.com/COMP2913-24-25/comp2913-team17/wiki/Coding-Style-Guide) in the [wiki](https://github.com/COMP2913-24-25/comp2913-team17/wiki) for more information. Your changes might be rejected if your commit messages don't follow this structure.

```bash
# To stage all changes you've made
git add .

# To save changes locally
git commit -m "conventional commit message"

# To upload to the remote repository
git push
```

5. Create a Pull Request

The pull request should be linked to an issue where possible using "Closes #<id>". This ensures that when your changes are merged, it will automatically close the issue it is linked with. Pull requests should be descriptive, with markdown headings breaking up sections. Images are always welcome especially for UI changes so we can see a before and after.

6. Await Review

Once the designated coordinator has looked over your changes and tested them, they will handle the merging process for you. After this, you have successfully contributed to the project! Thank you! 😃
