# Job Portal

A Django-based job portal application with separate candidate and recruiter modules.

## Features
- Candidate signup/login, profile management, job applications
- Recruiter signup/login, posting jobs, viewing applicants
- Media uploads for profile pictures and company images

## Tech Stack
- Python, Django
- SQLite (default database)
- HTML/CSS templates

## Setup
1. Clone the repo
2. Create a virtual environment and install dependencies:
pip install django
3. Run migrations:
python manage.py makemigrations
python manage.py migrate
4. Start the server:
python manage.py runserver