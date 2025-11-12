# Accipere - Job Application Management System

A Django REST API for managing job applications with role-based access control.

## Setup Instructions

### 1. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy `.env.example` to `.env` and update the values:

```bash
cp .env.example .env
```

Make sure to:
- Set a strong `SECRET_KEY` for production
- Configure your PostgreSQL database credentials
- Update `ALLOWED_HOSTS` for production
- Set `DEBUG=False` in production

### 4. Setup Database

Make sure PostgreSQL is running and create the database:

```sql
CREATE DATABASE accipere_db;
```

### 5. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser

```bash
python manage.py createsuperuser
```

You'll be prompted for:
- Email
- First name
- Last name
- Password

### 7. Run Development Server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000`

## Project Structure

```
accipere/
├── accipere/          # Project settings
├── authentication/    # Auth endpoints (login, register, etc.)
├── users/            # User management
├── roles/            # Role management
├── jobs/             # Job postings
├── applications/     # Job applications
├── common/           # Shared utilities
```

## API Endpoints

- `/admin/` - Django admin interface
- `/api/` - API endpoints (authentication, users, jobs, etc.)

## Technologies

- Django 4.2
- Django REST Framework
- PostgreSQL
- JWT Authentication (Simple JWT)
- CORS Headers
