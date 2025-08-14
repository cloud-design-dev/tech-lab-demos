from flask import Flask, render_template, jsonify, request, session, redirect, url_for
import os
import json
import time
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

try:
    from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
    from ibm_platform_services import UserManagementV1
    from ibm_platform_services.user_management_v1 import UsersPager
    IBM_SDK_AVAILABLE = True
except ImportError:
    IBM_SDK_AVAILABLE = False

app = Flask(__name__)

# Database configuration with multiple environment variable support
def get_database_url():
    """Get database URL from environment variables with priority fallback"""
    # Priority 1: Full DATABASE_URL
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # Handle postgres:// vs postgresql:// prefix
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        return database_url
    
    # Priority 2: Individual PostgreSQL components
    postgres_user = os.environ.get('POSTGRES_USER')
    postgres_password = os.environ.get('POSTGRES_PASSWORD') 
    postgres_host = os.environ.get('POSTGRES_HOST')
    postgres_port = os.environ.get('POSTGRES_PORT', '5432')
    postgres_db = os.environ.get('POSTGRES_DB')
    
    if all([postgres_user, postgres_password, postgres_host, postgres_db]):
        return f"postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"
    
    # Priority 3: SQLite fallback
    return 'sqlite:///checkin.db'

database_url = get_database_url()
print(f"Using database: {database_url}")
print(f"Database type: {'PostgreSQL' if database_url.startswith('postgresql://') else 'SQLite'}")

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
db = SQLAlchemy(app)

# Admin authentication configuration
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'demo-admin-2024')

# Database initialization function
def ensure_database():
    """Ensure database tables exist"""
    try:
        with app.app_context():
            db.create_all()
            print("Database tables created successfully")
            print(f"Database file location: {database_url}")
            
            # Test the connection
            result = db.session.execute(text('SELECT 1')).scalar()
            print(f"Database connection test: {result}")
            
    except Exception as e:
        print(f"Error creating database tables: {e}")
        raise

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    group_name = db.Column(db.String(100), nullable=True)
    checked_in_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_validated = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'group_name': self.group_name,
            'checked_in_at': self.checked_in_at.isoformat(),
            'is_validated': self.is_validated
        }

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    max_members = db.Column(db.Integer, default=3)
    current_members = db.Column(db.Integer, default=0)
    is_full = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'max_members': self.max_members,
            'current_members': self.current_members,
            'is_full': self.is_full,
            'created_at': self.created_at.isoformat()
        }

# Global cache for user list to avoid repeated API calls
_user_cache = None
_cache_timestamp = None
_cache_ttl = 300  # 5 minutes cache

def get_active_ibm_cloud_users():
    """Fetch and cache active users from IBM Cloud account"""
    global _user_cache, _cache_timestamp
    
    if not IBM_SDK_AVAILABLE:
        print("IBM Cloud SDK not available")
        return []
    
    # Check cache validity
    current_time = time.time()
    if _user_cache is not None and _cache_timestamp is not None:
        if current_time - _cache_timestamp < _cache_ttl:
            print("Using cached user list")
            return _user_cache
    
    try:
        # Initialize IBM Cloud authenticator
        api_key = os.environ.get('IBM_CLOUD_API_KEY')
        account_id = os.environ.get('IBM_CLOUD_ACCOUNT_ID')
        
        if not api_key:
            print("IBM_CLOUD_API_KEY not set in environment")
            return []
        
        if not account_id:
            print("IBM_CLOUD_ACCOUNT_ID not set in environment")
            return []
        
        print(f"Fetching users from IBM Cloud account: {account_id}")
        
        # Initialize User Management service
        authenticator = IAMAuthenticator(api_key)
        user_management_service = UserManagementV1(authenticator=authenticator)
        
        # Fetch all users using pager
        all_results = []
        pager = UsersPager(
            client=user_management_service,
            account_id=account_id,
        )
        
        while pager.has_next():
            next_page = pager.get_next()
            if next_page is not None:
                all_results.extend(next_page)
        
        print(f"Fetched {len(all_results)} total users from IBM Cloud")
        
        # Filter for active users only
        active_users = []
        for user in all_results:
            user_dict = user.to_dict() if hasattr(user, 'to_dict') else user
            status = user_dict.get('state', '').upper()
            email = user_dict.get('email', '')
            
            if status == 'ACTIVE' and email:
                active_users.append({
                    'email': email.lower(),  # Normalize email to lowercase
                    'user_id': user_dict.get('user_id', ''),
                    'first_name': user_dict.get('first_name', ''),
                    'last_name': user_dict.get('last_name', ''),
                    'state': status
                })
        
        print(f"Found {len(active_users)} active users")
        
        # Update cache
        _user_cache = active_users
        _cache_timestamp = current_time
        
        return active_users
        
    except Exception as e:
        print(f"Error fetching IBM Cloud users: {e}")
        return []

def validate_user_with_ibm_cloud(email):
    """Validate user email against IBM Cloud account active user list"""
    if not IBM_SDK_AVAILABLE:
        print("IBM Cloud SDK not available, using fallback validation")
        # For demo purposes, accept any email that contains 'ibm' or ends with .com
        return email.lower().endswith('.com') or 'ibm' in email.lower()
    
    # Get active users from IBM Cloud
    active_users = get_active_ibm_cloud_users()
    
    if not active_users:
        print("No active users found or API error, falling back to basic validation")
        # Fallback to basic email validation if API fails
        return '@' in email and '.' in email and email.lower().endswith('.com')
    
    # Check if email exists in active user list
    email_lower = email.lower().strip()
    for user in active_users:
        if user['email'] == email_lower:
            print(f"User validated: {email} (ID: {user['user_id']})")
            return True
    
    print(f"User not found in active user list: {email}")
    return False

def get_next_available_group():
    """Get the next available group or create a new one"""
    # Find a group that's not full
    available_group = Group.query.filter_by(is_full=False).first()
    
    if available_group:
        return available_group
    
    # Create a new group
    group_count = Group.query.count()
    new_group_name = f"Group {group_count + 1}"
    
    new_group = Group(name=new_group_name)
    db.session.add(new_group)
    db.session.commit()
    
    return new_group

def assign_user_to_group(user):
    """Assign user to an available group"""
    group = get_next_available_group()
    
    user.group_name = group.name
    group.current_members += 1
    
    # Mark group as full if it reaches max capacity
    if group.current_members >= group.max_members:
        group.is_full = True
    
    db.session.commit()
    return group

def is_admin_authenticated():
    """Check if the current session is authenticated as admin"""
    return session.get('admin_authenticated', False)

def authenticate_admin(password):
    """Authenticate admin password and set session"""
    if password == ADMIN_PASSWORD:
        session['admin_authenticated'] = True
        return True
    return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/registered')
def registered_users():
    if not is_admin_authenticated():
        return redirect(url_for('admin_login'))
    return render_template('registered.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')
        if authenticate_admin(password):
            return redirect(url_for('registered_users'))
        else:
            return render_template('admin_login.html', error='Invalid password')
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_authenticated', None)
    return redirect(url_for('index'))

@app.route('/api/checkin', methods=['POST'])
def checkin_user():
    try:
        data = request.json or {}
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({"success": False, "error": "Email is required"}), 400
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({
                "success": True,
                "message": "You have already checked in!",
                "group_name": existing_user.group_name,
                "checked_in_at": existing_user.checked_in_at.isoformat(),
                "already_registered": True
            })
        
        # Validate user with IBM Cloud
        is_valid = validate_user_with_ibm_cloud(email)
        if not is_valid:
            return jsonify({
                "success": False,
                "error": "Email not found in authorized user list"
            }), 403
        
        # Create new user
        new_user = User(email=email, is_validated=True)
        db.session.add(new_user)
        db.session.flush()  # Get the ID without committing
        
        # Assign to group
        group = assign_user_to_group(new_user)
        
        return jsonify({
            "success": True,
            "message": "Successfully checked in!",
            "group_name": new_user.group_name,
            "group_members": group.current_members,
            "group_max": group.max_members,
            "checked_in_at": new_user.checked_in_at.isoformat(),
            "already_registered": False
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Check-in error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/registered')
def get_registered_users():
    try:
        users = User.query.order_by(User.checked_in_at.desc()).all()
        groups = Group.query.all()
        
        # Group users by their assigned groups
        grouped_users = {}
        for user in users:
            if user.group_name not in grouped_users:
                grouped_users[user.group_name] = []
            grouped_users[user.group_name].append(user.to_dict())
        
        return jsonify({
            "total_users": len(users),
            "total_groups": len(groups),
            "users": [user.to_dict() for user in users],
            "groups": [group.to_dict() for group in groups],
            "grouped_users": grouped_users
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/lookup', methods=['POST'])
def lookup_user_group():
    """Look up a user's group by their email address"""
    try:
        data = request.json or {}
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({
                "success": False,
                "error": "Email address is required"
            }), 400
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        if not user:
            return jsonify({
                "success": False,
                "error": "User not found. Please check your email address or register first.",
                "email": email
            }), 404
        
        # Get group information if user has a group
        group_info = None
        if user.group_name:
            group = Group.query.filter_by(name=user.group_name).first()
            if group:
                group_info = group.to_dict()
                # Get other group members
                group_members = User.query.filter_by(group_name=user.group_name).all()
                group_info['members'] = [u.email for u in group_members]
        
        return jsonify({
            "success": True,
            "user": {
                "email": user.email,
                "group_name": user.group_name,
                "checked_in_at": user.checked_in_at.isoformat() if user.checked_in_at else None,
                "is_validated": user.is_validated
            },
            "group": group_info
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Lookup failed: {str(e)}"
        }), 500

@app.route('/api/stats')
def get_stats():
    try:
        total_users = User.query.count()
        total_groups = Group.query.count()
        full_groups = Group.query.filter_by(is_full=True).count()
        available_groups = Group.query.filter_by(is_full=False).count()
        
        return jsonify({
            "total_users": total_users,
            "total_groups": total_groups,
            "full_groups": full_groups,
            "available_groups": available_groups,
            "average_group_size": round(total_users / max(total_groups, 1), 1)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "ibm_sdk_available": IBM_SDK_AVAILABLE
    })

@app.route('/api/debug/active-users')
def get_active_users():
    """Debug endpoint to show active IBM Cloud users"""
    try:
        active_users = get_active_ibm_cloud_users()
        return jsonify({
            "total_active_users": len(active_users),
            "cache_age_seconds": int(time.time() - _cache_timestamp) if _cache_timestamp else None,
            "ibm_sdk_available": IBM_SDK_AVAILABLE,
            "api_key_configured": bool(os.environ.get('IBM_CLOUD_API_KEY')),
            "account_id_configured": bool(os.environ.get('IBM_CLOUD_ACCOUNT_ID')),
            "active_users": active_users[:10] if active_users else [],  # Show first 10 for privacy
            "note": "Only showing first 10 users for privacy. Use in development only."
        })
    except Exception as e:
        return jsonify({
            "error": str(e),
            "ibm_sdk_available": IBM_SDK_AVAILABLE,
            "api_key_configured": bool(os.environ.get('IBM_CLOUD_API_KEY')),
            "account_id_configured": bool(os.environ.get('IBM_CLOUD_ACCOUNT_ID'))
        }), 500

@app.route('/api/debug/clear-cache', methods=['POST'])
def clear_user_cache():
    """Clear the user cache to force refresh"""
    global _user_cache, _cache_timestamp
    _user_cache = None
    _cache_timestamp = None
    return jsonify({"message": "User cache cleared successfully"})

@app.route('/api/ibm-cloud-users')
def get_ibm_cloud_users():
    """Get all IBM Cloud account users for admin view"""
    if not is_admin_authenticated():
        return jsonify({"error": "Authentication required"}), 401
    
    try:
        active_users = get_active_ibm_cloud_users()
        
        # Get registered user emails for comparison
        registered_users = User.query.all()
        registered_emails = set(user.email for user in registered_users)
        
        # Categorize users
        users_data = []
        for user in active_users:
            user_info = {
                'email': user['email'],
                'first_name': user.get('first_name', ''),
                'last_name': user.get('last_name', ''),
                'user_id': user.get('user_id', ''),
                'state': user.get('state', 'ACTIVE'),
                'is_registered': user['email'] in registered_emails
            }
            users_data.append(user_info)
        
        # Sort by registration status (unregistered first) then by email
        users_data.sort(key=lambda x: (x['is_registered'], x['email']))
        
        # Calculate statistics
        total_users = len(users_data)
        registered_count = sum(1 for u in users_data if u['is_registered'])
        unregistered_count = total_users - registered_count
        
        return jsonify({
            "success": True,
            "total_users": total_users,
            "registered_count": registered_count,
            "unregistered_count": unregistered_count,
            "users": users_data,
            "cache_age_seconds": int(time.time() - _cache_timestamp) if _cache_timestamp else None,
            "ibm_sdk_available": IBM_SDK_AVAILABLE
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Error fetching IBM Cloud users: {str(e)}",
            "ibm_sdk_available": IBM_SDK_AVAILABLE
        }), 500

if __name__ == '__main__':
    # Initialize database on startup
    ensure_database()
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)