# COMP2913 Team 17: Antiques & Collectibles Auction System

## Project Description

This project implements an online auction platform specialised for antiques and collectibles. The system allows users to buy and sell items through a competitive bidding process, with built-in authentication services for verifying item authenticity.

For more detailed documentation, please visit the [Wiki](https://github.com/COMP2913-24-25/comp2913-team17/wiki).

## Table of Contents
1. [Description](#description)
2. [Technology Stack](#technology-stack)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Credits](#credits)
6. [License](#license)
7. [How to Contribute](#how-to-contribute)
8. [Testing](#tests)

## Technology Stack
### **Frontend**

- [jQuery](https://jquery.com/) - Simplifies event handling, DOM manipulation, and AJAX requests, enabling real-time updates and dynamic interactions on the frontend.

- [Bootstrap](https://getbootstrap.com/) - For responsive styling, maintaining accessibility for mobile users.

### **Backend**

- [Flask](https://flask.palletsprojects.com/en/stable/) - A lightweight web application framework.

- [SQLAlchemy](https://www.sqlalchemy.org/) - An SQL toolkit and ORM using Python.

- [Stripe](https://stripe.com/gb) - Secure handling of payments.

### **Testing**

- [pytest](https://docs.pytest.org/en/stable/) - Facilitates writing and running tests for the backend.


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

To accomodate payments, you will need to set up Stripe CLI, instructions can be found [here](https://docs.stripe.com/stripe-cli). Once you have set up Stripe CLI and populated the `.env` file with your Stripe API keys, you will need to run the following command:

```bash
stripe listen --forward-to http://127.0.0.1:5000/item/stripe-webhook
```

7. Access the application:
- Open the browser at: http://localhost:5000
- Access any page at: http://localhost:5000/page

A live version of the application can be found at: https://vintage-vault-aesv.onrender.com/

## Usage

### Features

| Feature                            | Description                                                                                                         |
|------------------------------------|---------------------------------------------------------------------------------------------------------------------|
| **🧑‍💻 Account Creation**           | Users can create accounts using their email or signing in with Google, allowing them to create and bid on auctions.  |
| **📦 Listing Items**               | Sellers can list items for auction, with durations up to 5 days.                                                   |
| **💰 Bidding and Payment**         | Buyers can submit bids for a minimum of 1p above the current bid price. When a buyer wins an auction, they are instructed to complete payment by entering their card details, or choosing a saved card if this has been opted for before. |
| **🔔 Notification System**         | Notifications are rendered in the browser for significant events such as account creation, winning bids, and payment prompts. Some important notifications are also sent via email to keep users updated who are not currently browsing the site. |
| **🧑‍🔬 Experts**                   | "Expert" is a role for users who are able to authenticate items for given categories. These users are not able to bid on items and may only authenticate items they are assigned to. |
| **⏰ Expert Availability**         | Experts can mark themselves as available/unavailable for work for various dates and times. This prevents an expert from being assigned for authentication of an item when they are not available. |
| **📑 Authentication Requests**    | Sellers can request their items be authenticated by a designated Expert. This is supplemented by a Seller/Expert messaging system, where the seller can provide more details/photos at the expert's request. When an item is authenticated, the auction for it will feature an authenticated badge for buyer confidence. |
| **👨‍💼 Managers**                  | "Manager" is a role dedicated for VintageVault staff, giving them access to user roles and platform statistics.        |
| **⚙️ Manager Options**             | In the management dashboard, a manager can update the roles of users in real time. Managers are also tasked with assigning experts to auctions who have requested authentication. This can be set manually, or auto-assigned based on a recommendation algorithm which considers the niche of the expert and their availability. |
| **📊 Platform Statistics/Configuration** | Managers can view sales information for the platform over a period of up to 6 months. Visible statistics include the number of paid auctions, projected revenue, commission income, and other relevant data to help with the platform's performance monitoring. Additionally, managers may update the platform fee percentages as well as the maximum auction duration possible for future listings. |



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

Contributions after the final assessment deadline (01/04/2025) are welcome! To contribute, follow these steps to ensure your changes can be properly reviewed and integrated.

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

Once the designated coordinator has looked over your changes and tested them, they will handle the merging process for you. After this, you have successfully contributed to the project! Thankyou 😃

## Tests

Testing is encouraged for all features, it allows us to maintain the integrity of the site and catch bugs early. Testing may seem to add more work, but actually prevents more work in the long run when diagnosing and fixing errors.

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
