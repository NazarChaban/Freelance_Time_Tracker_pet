# Freelance Time Tracker

## Table of Contents
- [Description](#description)
- [Installation and Running](#installation-and-running)
- [API Endpoints](#api-endpoints)
- [API Endpoints Examples](#api-endpoints-examples)

## Description
Freelance Time Tracker is a Django-based REST API application that helps freelancers track time, manage clients, and generate invoices seamlessly.

## Installation and Running
1. Clone the repository:
    ```bash
    git clone https://github.com/NazarChaban/Freelance_Time_Tracker_pet.git
    ```
2. Change directory:
    ```bash
    cd Freelance_Time_Tracker_pet
    ```
3. Configure env variables in .env file (watch .env_exmp file)

4. Run Docker:
    ```bash
    docker-compose up --build
    ```

Or if you don't have docker:

3. Configure env variables in .env file (watch .env_exmp file)

4. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
5. Run migration (requires database connection)
    ```bash
    cd freelance_time_tracker
    python manage.py migrate
    ```
5. Start the development server:
    ```bash
    python manage.py runserver
    ```

## API Endpoints
### Users
- **POST /users/api/signup/**: Create new user.
- **POST /users/api/login/**: Authenticate user.
- **POST /users/api/logout/**: Logout user.

### Time Tracking
- **POST /time-tracking/start/**: Start tracking time.
- **POST /time-tracking/stop/**: Stop tracking time.
- **GET /time-tracking/invoices/**: Retrieve generated invoices.
- **POST /time-tracking/generate-invoice/**: Generate an invoice.

### Clients
- **GET /clients/api/**: Retrieve clients.
- **POST /clients/api/**: Create a client.
- **GET /clients/api/active/**: Retrieve active clients.
- **GET /clients/api/inactive/**: Retrieve inactive clients.

## API Endpoints Examples

### Authentication

- **Signup**
    ```http
    POST /users/api/signup/
    ```
    **Request Body**:
    - username: String
    - email: String
    - password: String

- **Login**
    ```http
    POST /users/api/login/
    ```
    **Request Body**:
    - email: String
    - password: String

- **Logout**
    ```http
    POST /users/api/logout/
    ```
    **Headers**:
    - Authorization: Bearer <access_token>

### Time Tracking

This requests require an Authorization header to be included with each of them.
The header should follow the format: Authorization: Bearer <access_token>.

- **Start Time Tracking**
    ```http
    POST /time-tracking/start/
    ```
    **Request Body**:
    - client_id: Integer

- **Stop Time Tracking**
    ```http
    POST /time-tracking/stop/
    ```

- **List Invoices**
    ```http
    GET /time-tracking/invoices/
    ```
    **Request Body** (optional):
    - client_id: Integer
    - invoice_id: Integer

- **Generate Invoice**
    ```http
    POST /time-tracking/generate-invoice/
    ```
    **Request Body**:
    - client_id: Integer

### Clients

This requests require an Authorization header to be included with each of them.
The header should follow the format: Authorization: Bearer <access_token>.

- **Get Clients**
    ```http
    GET /clients/api/clients/
    ```

- **Client Info**
    ```http
    GET /clients/api/clients/<client_id>/
    ```

- **Create Client**
    ```http
    POST /clients/api/clients/
    ```
    **Request Body**:
    - name: String
    - email: String
    - phone: String
    - website: String
    - rate: Integer

- **Get Active Clients**
    ```http
    GET /clients/api/clients/active/
    ```

- **Get Inactive Clients**
    ```http
    GET /clients/api/clients/inactive/
    ```

- **Edit Clients Info**
    ```http
    PATCH /clients/api/clients/<client_id>/
    ```
    **Request Body**:
    - name: String
    - email: String
    - phone: String
    - website: String
    - rate: Integer
    - is_active: Boolean

Happy tracking!