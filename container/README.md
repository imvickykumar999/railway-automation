# Railway Deployment Django Web Application

A Django web application for managing Railway deployment configurations through a user-friendly web interface.

## Features

- **Web Form Interface**: Fill in Railway deployment configuration through a form
- **Data Storage**: Save configurations in SQLite database
- **CRUD Operations**: Create, Read, Update, Delete deployment configurations
- **Admin Panel**: Django admin interface for managing configurations

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r ../requirements.txt
   ```

2. **Navigate to container directory:**
   ```bash
   cd container
   ```

3. **Run migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Create superuser (optional, for admin panel):**
   ```bash
   python manage.py createsuperuser
   ```

5. **Run development server:**
   ```bash
   python manage.py runserver
   ```

6. **Access the application:**
   - Main application: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

## Usage

1. **Create a new configuration:**
   - Click "New Configuration" button
   - Fill in the form fields:
     - **Railway Token** (required): Get from https://railway.com/account/tokens
     - **Project Name** (required): Unique name for your project
     - **Docker Image** (required): Docker image to deploy
     - **Stream Key** (required): YouTube stream key
     - **YouTube ID** (required): YouTube video ID
   - Click "Create Configuration"

2. **View configurations:**
   - All configurations are listed on the home page
   - Click "View" to see details

3. **Edit configuration:**
   - Click "Edit" on any configuration
   - Update the fields and save

4. **Delete configuration:**
   - Click "Delete" on any configuration
   - Confirm deletion

## Model Fields

The `RailwayDeployment` model stores:
- `railway_token`: Railway API token (required)
- `project_name`: Project name (required)
- `docker_image`: Docker image name (required)
- `stream_key`: YouTube stream key (required)
- `youtube_id`: YouTube video ID (required)
- `is_active`: Active status flag
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

## Integration with railway_deploy.py

You can integrate this Django app with the `railway_deploy.py` script by:
1. Exporting saved configurations to `.env` format
2. Using the Django model data to populate environment variables
3. Calling the deployment script programmatically from Django views

