Email to DevOps Issues
Description

This repository contains a script that automatically processes emails and creates corresponding issues in Azure DevOps. It is ideal for teams wanting to automatically convert email requests into trackable tickets.
Prerequisites

Before setting up the project, ensure you meet the following requirements:

    Python 3.6 or higher
    Access to an email account with IMAP support
    An Azure DevOps account

Setup
Installation Steps

    Clone the repository:

    bash

git clone https://github.com/Muslix/email-to-devops-issues.git
cd email-to-devops-issues

Install the required Python packages:

bash

    pip install -r requirements.txt

Environment Configuration

    Create a file named .env in the project's root directory. This file is used to securely store sensitive data such as passwords and API keys. Add the following lines, replacing the values with your actual configuration data:

    makefile

    HOST=mail.yourmailserver.com
    USERNAME=your-email@example.com
    MAIL_PASSWORD=your-email-password
    MAILBOX=INBOX
    ORGANIZATION=your-devops-organization
    PROJECT=your-devops-project
    ACCESS_TOKEN=your-devops-access-token

Generating an Access Token for Azure DevOps

    Log in to your Azure DevOps account.
    Navigate to User Settings > Personal Access Tokens.
    Click New Token.
    Name your token and select the expiration date.
    Set the necessary permissions for your token to suit your use case (at a minimum, permission to create work items).
    Click Create and copy the token. Be sure to store it in a secure location, as it will not be displayed again after creation.

Usage

To start the script, navigate in your terminal or command prompt to the project directory and execute the following command:

bash

python main.py

The script continuously checks the specified email account for new messages and creates an issue in Azure DevOps for each new email.
Support

For support and bug reporting, please open an issue in the GitHub repository.
License

This project is licensed under the MIT License. Further details can be found in the LICENSE file.
