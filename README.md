# BaylorGrants

## Description

BaylorGrants is a Django-based Grants Management System designed to facilitate the entire grant lifecycle from application through to review, approval, and reporting. This system aims to streamline interactions between grantors and subgrantees, ensuring transparency, efficiency, and effectiveness in the grants management process.

## Features

- **Grant Application**: Enables subgrantees to apply for grants online.
- **Application Review**: Allows reviewers to assess applications and provide feedback.
- **Grant Reporting**: Facilitates subgrantees in submitting reports on grant utilization and outcomes.
- **User Management**: Supports managing user accounts, including roles and permissions customization.

## Getting Started

Follow these instructions to get a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

- Python (3.8 or newer)
- pip (Python package manager)
- Virtual Environment

### Setting Up a Development Environment

1. **Clone the Repository**

    ```bash
    git clone https://github.com/masabagerald/BaylorGrants.git
    cd BaylorGrants
    ```

2. **Create a Virtual Environment**

    - Unix/macOS:
        ```bash
        python3 -m venv venv
        ```

    - Windows:
        ```bash
        python -m venv venv
        ```

3. **Activate the Virtual Environment**

    - Unix/macOS:
        ```bash
        source venv/bin/activate
        ```

    - Windows:
        ```bash
        .\venv\Scripts\activate
        ```

4. **Install Dependencies**

    With the virtual environment activated, install the project dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Configuration

- Set up necessary environment variables (e.g., `SECRET_KEY`, database settings).
- Initialize the database:
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

### Running the Development Server

Start the server with:
```bash
python manage.py runserver
