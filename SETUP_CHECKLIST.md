# Setup Checklist

## ✅ Fixed Issues

- [x] Added missing imports in settings.py (`Csv`, `timedelta`)
- [x] Configured custom User model (`AUTH_USER_MODEL`)
- [x] Fixed User model bugs (REQUIRED_FIELDS, get_full_name, get_short_name)
- [x] Added CORS middleware to MIDDLEWARE list
- [x] Added missing `include` import in urls.py
- [x] Fixed app name (removed 'applicants', added 'roles')
- [x] Added static/media file configuration
- [x] Made role field nullable for superuser creation
- [x] Added CORS and file upload settings

## 🔧 Next Steps (Run These Commands)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Create Database
Make sure PostgreSQL is running, then:
```bash
createdb accipere_db
```

### 3. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Create Superuser
```bash
python manage.py createsuperuser
```

### 5. Run Server
```bash
python manage.py runserver
```

## 📝 Optional Steps

### Create media and staticfiles directories
```bash
mkdir -p media staticfiles
```

### Collect static files (for production)
```bash
python manage.py collectstatic
```

### Make setup script executable (Unix/Mac)
```bash
chmod +x setup.sh
./setup.sh
```

## ⚠️ Important Notes

- The `.env` file contains your database credentials
- Change `SECRET_KEY` before deploying to production
- Set `DEBUG=False` in production
- The Role field in User model is now optional (null=True) to allow superuser creation
- You can assign roles to users after creating them
