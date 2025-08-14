# OpenShift Demo Lab - Check-in Application

A Flask web application for registering users for the OpenShift Demo Lab, with group assignment and PostgreSQL persistence.

## Features

- **User Registration**: Email-based check-in system
- **IBM Cloud Integration**: User validation against IBM Cloud account lists
- **Group Assignment**: Automatic assignment to groups of 3 users
- **Duplicate Prevention**: Prevents multiple check-ins from the same email
- **Admin Dashboard**: View all registered users and group assignments
- **Database Persistence**: PostgreSQL support with SQLite fallback
- **Visual Consistency**: Matches the v2 demo app styling

## Endpoints

### User Endpoints
- `GET /` - Check-in form
- `POST /api/checkin` - Submit check-in with email
- `GET /registered` - Admin view of all registered users

### API Endpoints
- `GET /api/registered` - JSON list of all users and groups
- `GET /api/stats` - Registration statistics
- `GET /api/health` - Health check

## Database Schema

### Users Table
- `id` - Primary key
- `email` - Unique email address  
- `group_name` - Assigned group name
- `checked_in_at` - Registration timestamp
- `is_validated` - IBM Cloud validation status

### Groups Table
- `id` - Primary key
- `name` - Group name (e.g., "Group 1")
- `max_members` - Maximum group size (default: 3)
- `current_members` - Current member count
- `is_full` - Full status flag
- `created_at` - Creation timestamp

## Environment Variables

Create a `.env` file in the check-in directory with the following variables:

- `IBM_CLOUD_API_KEY` - IBM Cloud API key for user validation (required)
- `IBM_CLOUD_ACCOUNT_ID` - IBM Cloud account ID to fetch users from (required)
- `DATABASE_URL` - PostgreSQL connection string (defaults to SQLite)
- `PORT` - Server port (default: 8080)

See `.env.example` for a template.

## Local Development

```bash
cd check-in/
cp .env.example .env
# Edit .env with your IBM Cloud credentials
pip install -r requirements.txt
python app.py
```

Visit http://localhost:8080 for the check-in form.

### Debug Endpoints

- `GET /api/debug/active-users` - Show active IBM Cloud users (development only)
- `POST /api/debug/clear-cache` - Clear user cache to force refresh

## Docker Deployment

```bash
docker build -t checkin-app .
docker run -p 8080:8080 checkin-app
```

## OpenShift Deployment

1. Deploy PostgreSQL database:
```bash
oc apply -f openshift/postgresql.yaml
```

2. Deploy the application:
```bash
oc new-app python:3.12~https://github.com/your-repo/tech-labs-dallas --context-dir=check-in --name=checkin-app
oc expose svc/checkin-app
```

3. Set environment variables:
```bash
oc set env dc/checkin-app DATABASE_URL="postgresql://user:pass@postgresql:5432/checkin"
oc set env dc/checkin-app IBM_CLOUD_API_KEY="your-api-key"
```

## Group Assignment Logic

1. New user submits email for check-in
2. Email is validated against IBM Cloud user list
3. User is assigned to the first available group (not full)
4. If no groups available, a new group is created
5. Groups are marked full when they reach 3 members
6. Duplicate check-ins return existing group assignment

## IBM Cloud Integration

The app validates user emails against IBM Cloud account lists using the IBM Platform Services SDK. If the SDK is not available or configured, it falls back to basic email format validation.

### API Endpoints
- **POST /api/checkin** - Submit user registration with email validation
- **GET /api/registered** - JSON data for all users and group assignments
- **GET /api/stats** - Registration statistics and completion metrics
- **GET /api/health** - Application health check with SDK status
- **GET /api/debug/active-users** - Show active IBM Cloud users (debug only)
- **POST /api/debug/clear-cache** - Clear user cache to force refresh

## User Validation Process

1. **IBM Cloud Integration**: App fetches active users from your IBM Cloud account using the User Management API
2. **User Filtering**: Only users with "ACTIVE" status are eligible for registration
3. **Email Matching**: User email must exactly match an active user in the account
4. **Caching**: User list is cached for 5 minutes to reduce API calls
5. **Fallback**: If API is unavailable, falls back to basic email validation

## Visual Design

The application uses the same brutalist styling as the v2 demo app:
- **Color scheme**: Red (#d43f00) primary, gray accents
- **Typography**: Courier New monospace font
- **Layout**: Clean cards with bold borders and shadows
- **Responsive**: Mobile-friendly design