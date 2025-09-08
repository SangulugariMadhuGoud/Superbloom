# Superbloom Agency

Monorepo: Django backend + Vite React frontend.

## Local Development

- Backend (Django):
  - Python 3.13 recommended
  - Create venv in `backend/.venv` and install:
    ```bash
    pip install -r backend/requirements.txt
    python backend/manage.py migrate
    python backend/manage.py runserver
    ```
- Frontend (Vite React):
  ```bash
  cd frontend
  npm install
  npm run dev
  ```

## Production Settings

- Configure environment variables (examples):
  - `DJANGO_SECRET_KEY`
  - `DJANGO_DEBUG=false`
  - `DJANGO_ALLOWED_HOSTS=yourdomain.com`
  - `CORS_ALLOWED_ORIGINS=https://yourfrontend.com`
  - `CSRF_TRUSTED_ORIGINS=https://yourfrontend.com`
- Static files are served by WhiteNoise.
- WSGI: `gunicorn` via `backend/Procfile`.

## Google Sheets Export (optional)
- Set `GOOGLE_SHEETS_CREDENTIALS_FILE` and `GOOGLE_SHEETS_SPREADSHEET_ID` in settings or env.
- Share the sheet with the service account email.

## Deploy

- Backend to PaaS (Render/Heroku/Fly):
  - Install from `backend/requirements.txt`
  - Run migrations: `python manage.py migrate`
  - Start command: `gunicorn server.wsgi --bind 0.0.0.0:$PORT`
- Frontend: deploy `frontend` via Netlify/Vercel. Set `VITE_API_BASE` to backend URL.

## CI/CD

- Suggested: GitHub Actions to run `python manage.py check` and `npm run build`.
