# Payroll Management System
---

## Overview
The Payroll Management System is a Django-based application designed to handle employee management, payroll, and payout processes. It includes custom user registration, payout request handling, and group-based access controls to ensure secure and efficient operations.

---

## Navigation
- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
  - [Admin Panel](#admin-panel)
  - [Login](#login)
  - [Employee Management](#employee-management)
  - [User Registration](#user-registration)
  - [Payout Requests](#payout-requests)
- [Code Highlights](#code-highlights)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)
- [Running with Docker](#running-with-docker)

---

## Features
- **Employee Management**: 
  - Create, update, and manage employee records.
  - Automatically generate unique employee codes.

- **Custom User Registration**:
  - Link users to employees via employee codes.
  - Assign users to specific groups like "Accountant" based on their role.

- **Payout Requests**:
  - Allow employees to request payouts from their available earnings.
  - Admins can process requests and update balances securely.

- **Group-Based Access Control**:
  - Accountants have restricted access to payout and payroll data.

---

## Requirements
- Python 3.x
- Django 5.x

---

## Installation

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/nearYouluV/payroll_system.git
    ```

2. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3. **Apply Migrations**:
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```
4. **Create `.env` File**:
   In your project root, create a `.env` file to store environment variables, such as `DEBUG` and `DJANGO_SECRET_KEY`. Example:

   ```
   DEBUG=True
   DJANGO_SECRET_KEY=your_secret_key_here
   ```
5. **Create a Superuser**:
    ```bash
    python manage.py createsuperuser
    ```

6. **Populate users**:
    ```bash
    python manage.py populate
    ```

7. **Run the Development Server**:
    ```bash
    python manage.py runserver
    ```

---

## Usage

### Admin Panel
The Django admin panel allows you to manage employees. Accessible at `/admin`.

### Login 
I have created a `populate` command to populate users, they have the same password for all - "Password123". You can log in into the site using the username field at the "customuser" sheet.

### Employee Management
- Navigate to the "Employees" section in the site.
- Use filters and search to locate specific employees.
- Add, update, or delete employee records as needed.

### User Registration
You can create a user with a generated unique code using the `employees/` page when logged in as an accountant. Users must register via the custom registration form. Employees need to use their unique employee code to complete registration.

### Payout Requests
- Employees can submit payout requests via the application.
- Accountants can process these requests, ensuring proper balance deductions.

---

## Code Highlights

### `models.py`
Defines the core models:
- **`Employee`**: Represents employee records with fields like `position`, `salary_rate`, and `employee_code`.
- **`PayoutRequest`**: Handles employee payout requests with status tracking.

### `forms.py`
Custom forms for:
- **Payout Request**: Allows employees to request payouts.
- **User Registration**: Validates employee codes and ensures unique user accounts.

### `admin.py`
Custom admin configuration for managing employees:
- List filters and search capabilities.
- Custom actions like batch deletion.

### `management/commands/populate.py`
A custom Django management command that populates the database with fake users. This command creates users with a default password of `Password123`.

To use this command, run:
```bash
python manage.py populate
```

---

## Running with Docker

To run the project using Docker, follow these steps:

1. **Ensure Docker is Installed**:
   If you don't have Docker installed, you can download and install it from [Docker's official website](https://www.docker.com/get-started).


2. **Build and Run the Docker Container**:
    In the project root, run the following command to build the Docker image and start the container:

    ```bash
    docker-compose build
    docker-compose run web python manage.py makemigrations
    docker-compose run web python manage.py migrate
    docker-compose run web python manage.py populate
    docker-compose up 
    ```

    This command does the following:
    - Builds the Docker image from the `Dockerfile`.
    - Runs the `django_app` container.
    - Runs the Django migrations and starts the development server on port `8000`.

3. **Access the Application**:
   After the container is running, you can access the application at `http://localhost:8000`.

4. **Stopping the Docker Container**:
   To stop the container, use:

   ```bash
   docker-compose down
   ```

---

## Contributing
Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a feature branch: `git checkout -b feature-name`.
3. Commit your changes: `git commit -m "Add feature"`.
4. Push to the branch: `git push origin feature-name`.
5. Open a pull request.

---

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## Contact
For questions or support, reach out to:
- **Email**: v.pelishenko1999@gmail.com
- **GitHub**: [nearYouluV](https://github.com/nearYouluV)
- **LinkedIn**: [Vitaliy Pelishenko](https://www.linkedin.com/in/vitaliy-pelishenko-563431246/)