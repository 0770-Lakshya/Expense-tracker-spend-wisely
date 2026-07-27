# Expense Tracker

A personal expense tracking web application built with Django. Track, filter, and visualize your daily expenses with interactive charts.

## Features

- **Expense Management** - Add, edit, and delete expenses with title, amount, category, and date
- **Category Support** - Food, Transport, Shopping, Bills, Entertainment, Health, Education, Other
- **Dashboard** - View expenses with date-range filtering
- **Reports** - Category-wise pie chart and monthly spending trends
- **Dark/Light Theme** - Toggle between dark and light mode
- **Authentication** - Register, login/logout, and Google OAuth via django-allauth
- **Responsive UI** - Bootstrap 5 with animated Lordicon icons
- **Production Ready** - Deployable on Render with PostgreSQL

## Tech Stack

- **Backend**: Python, Django 6.0
- **Frontend**: Bootstrap 5, Chart.js, Lordicon
- **Auth**: django-allauth (Google OAuth)
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Deployment**: Render

## Getting Started

### Prerequisites

- Python 3.13+
- pip

### Setup

```bash
# Clone the repo
git clone https://github.com/0770-Lakshya/Expense-tracker-spend-wisely.git
cd expense-tracker/expense_tracker



# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start dev server
python manage.py runserver
```

## Environment Variables

| Variable | Description |
|---|---|
| `DJANGO_SECRET_KEY` | Django secret key (auto-generated if empty) |
| `DJANGO_DEBUG` | Set `True` for development |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated allowed hosts |
| `DATABASE_URL` | Database URL (defaults to SQLite) |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret |

## Deployment

The project includes a `render.yaml` for one-click deploy on [Render](https://render.com).

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

## Project Structure

```
expense_tracker/
├── expenses/           # Main app (models, views, templates)
│   ├── models.py       # Expense model
│   ├── views.py        # Dashboard, reports, CRUD views
│   └── urls.py         # URL routing
├── templates/          # HTML templates
│   ├── base.html       # Base layout with navbar and theme toggle
│   ├── expenses/       # Dashboard, filter, reports templates
│   └── registration/   # Login, signup templates
├── static/             # CSS, Lordicon JSON animations
├── expense_tracker/    # Django project settings
│   └── settings.py     # Main configuration
├── manage.py
└── requirements.txt
```
