# Event Management System

A Django-based event management system that allows users to create, manage, and register for events.

## Features

- User authentication and authorization
- Event creation and management
- Event registration and deregistration
- Event categories and filtering
- Admin dashboard for event management
- User registration management

## Setup Instructions

1. Clone the repository:
```bash
git clone <your-repo-url>
cd event-management
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up the database:
```bash
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

7. Access the application at `http://127.0.0.1:8000/`

## Project Structure

- `events/` - Main application directory
  - `models.py` - Database models
  - `views.py` - View functions and classes
  - `urls.py` - URL routing
  - `forms.py` - Form definitions
  - `templates/` - HTML templates
  - `static/` - Static files (CSS, JS, images)
  - `templatetags/` - Custom template tags

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 