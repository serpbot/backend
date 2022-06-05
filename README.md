# backend

## Installation

All the dependencies can be found in the requirements.txt file. This file contains both the specific packages as well as their exact versions required for proper functioning. It also makes it very easy to quickly setup as pip can read it directly.

> pip install -r requirements.txt

## Start server

Before being able to run the scheduler, you must set the following environment variables:
- SQS_REGION
- SQS_NAME
- DATABASE_NAME
- DATABASE_HOST
- DATABASE_USERNAME
- DATABASE_PASSWORD
- COGNITO_REGION
- COGNITO_USERPOOL_ID
- COGNITO_APP_CLIENT_ID
- COGNITO_APP_CLIENT_SECRET
- HCAPTCHA_SECRET
- HCAPTCHA_SITE_KEY
- CONTACT_EMAIL
- SWAGGER_UI

The process can be launched by running the command below:

> python3 src/main.py
