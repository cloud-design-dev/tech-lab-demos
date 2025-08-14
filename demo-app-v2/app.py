from flask import Flask, render_template, jsonify, request
import os
import json
import time
import subprocess
import socket
import requests
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

app = Flask(__name__)

# Global request counter for tracking inbound connections
app_start_time = time.time()
request_stats = {
    "active_connections": 0,
    "total_requests": 0,
    "endpoint_counts": {},
    "start_time": datetime.now()
}

@app.before_request
def before_request():
    """Track incoming requests"""
    request_stats["total_requests"] += 1
    request_stats["active_connections"] += 1
    
    # Track endpoint usage
    endpoint = request.endpoint or 'unknown'
    request_stats["endpoint_counts"][endpoint] = request_stats["endpoint_counts"].get(endpoint, 0) + 1

@app.after_request
def after_request(response):
    """Track completed requests"""
    request_stats["active_connections"] = max(0, request_stats["active_connections"] - 1)
    return response

# Database configuration  
def get_database_url():
    """Get database URL with fallback logic"""
    # First try the full DATABASE_URL
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url:
        # Fix postgres:// to postgresql:// if needed
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        return database_url
    
    # Try to build PostgreSQL URL from individual components
    pg_host = os.environ.get('POSTGRESQL_SERVICE_HOST')
    pg_port = os.environ.get('POSTGRESQL_SERVICE_PORT', '5432')
    pg_db = os.environ.get('POSTGRESQL_DATABASE', 'postgres')
    pg_user = os.environ.get('POSTGRESQL_USER')
    pg_password = os.environ.get('POSTGRESQL_PASSWORD')
    
    if pg_host and pg_user and pg_password:
        database_url = f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}"
        print("Built PostgreSQL URL from individual environment variables")
        return database_url
    
    # Fallback to SQLite - check for PVC path first, then writable directory
    sqlite_path = os.environ.get('SQLITE_PATH', '/tmp/v2_demo.db')
    
    # Create directory if it doesn't exist (for PVC mounting)
    sqlite_dir = os.path.dirname(sqlite_path)
    if sqlite_dir and sqlite_dir != '/tmp':
        try:
            os.makedirs(sqlite_dir, exist_ok=True)
            print(f"Created SQLite directory: {sqlite_dir}")
        except PermissionError:
            print(f"Cannot create directory {sqlite_dir}, falling back to /tmp")
            sqlite_path = '/tmp/v2_demo.db'
    
    print(f"No PostgreSQL config found, falling back to SQLite: {sqlite_path}")
    return f'sqlite:///{sqlite_path}'

database_url = get_database_url()
print(f"Using database: {database_url}")

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

try:
    db = SQLAlchemy(app)
except Exception as db_init_error:
    print(f"Database initialization error: {db_init_error}")
    # If there's an issue with the database setup, provide helpful error info
    print("Check that DATABASE_URL or PostgreSQL environment variables are set correctly")
    raise

# Database initialization function
def ensure_database():
    """Ensure database tables exist"""
    try:
        with app.app_context():
            db.create_all()
            print("Database tables created successfully")
            print(f"Database location: {database_url}")
            
            # Test the connection
            result = db.session.execute(text('SELECT 1')).scalar()
            print(f"Database connection test: {result}")
            
            # Check if this is PostgreSQL or SQLite
            if 'postgresql' in database_url:
                print("Using PostgreSQL for persistent storage")
            else:
                print("Using SQLite for local development (data will not persist across restarts)")
            
    except Exception as e:
        print(f"Error creating database tables: {e}")
        print(f"Database URL: {database_url}")
        if 'postgresql' in database_url:
            print("PostgreSQL connection failed. Check if:")
            print("- PostgreSQL service is running")
            print("- DATABASE_URL or PostgreSQL environment variables are correct")
            print("- Network connectivity to database")
        raise

# Database Models
class PersistenceTest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'data': self.data,
            'timestamp': self.timestamp.isoformat()
        }

def detect_environment():
    """Detect if running in OpenShift/Kubernetes or local environment"""
    try:
        # Check for OpenShift/Kubernetes environment variables
        if os.environ.get('OPENSHIFT_BUILD_NAMESPACE'):
            return os.environ.get('OPENSHIFT_BUILD_NAMESPACE')
        elif os.environ.get('KUBERNETES_SERVICE_HOST'):
            # Try to get namespace from service account
            try:
                with open('/var/run/secrets/kubernetes.io/serviceaccount/namespace', 'r') as f:
                    return f.read().strip()
            except FileNotFoundError:
                pass
        
        # Try oc command to get current project
        try:
            result = subprocess.run(['oc', 'project', '-q'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
            
        return 'local-dev'
    except Exception:
        return 'local-dev'

def get_hostname():
    """Get container/pod hostname"""
    try:
        return socket.gethostname()
    except Exception:
        return 'unknown'

def get_network_connections():
    """Get network connection information"""
    connections_info = {
        "active_connections": request_stats["active_connections"],
        "total_requests": request_stats["total_requests"],
        "uptime_seconds": (datetime.now() - request_stats["start_time"]).total_seconds(),
        "requests_per_minute": 0,
        "top_endpoints": []
    }
    
    # Calculate requests per minute
    if connections_info["uptime_seconds"] > 0:
        connections_info["requests_per_minute"] = round(
            (connections_info["total_requests"] / connections_info["uptime_seconds"]) * 60, 2
        )
    
    # Get top endpoints
    sorted_endpoints = sorted(
        request_stats["endpoint_counts"].items(), 
        key=lambda x: x[1], 
        reverse=True
    )[:3]
    connections_info["top_endpoints"] = [
        {"endpoint": ep, "count": count} for ep, count in sorted_endpoints
    ]
    
    return connections_info

def get_app_url():
    """Get the application URL for external traffic generation"""
    try:
        namespace = detect_environment()
        if namespace != 'local-dev':
            # Try to detect OpenShift route
            try:
                # Try to get route via oc command if available
                result = subprocess.run(['oc', 'get', 'route', 'openshift-demo-app-v2', '-o', 'jsonpath={.spec.host}'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0 and result.stdout.strip():
                    route_host = result.stdout.strip()
                    return f"https://{route_host}"
            except:
                pass
            
            # Fallback: try to construct from request context if available
            try:
                from flask import request
                if hasattr(request, 'host'):
                    return f"https://{request.host}"
            except:
                pass
            
            # Final fallback: construct likely route URL pattern
            # Note: Code Engine function only accepts .containers.appdomain.cloud domains
            # For other domains, the function will return a 403 error
            hostname = get_hostname()
            return f"https://openshift-demo-app-v2-{namespace}.apps.cluster.local"
        
        # Local development fallback
        return "http://localhost:8080"
    except Exception as e:
        print(f"Error detecting app URL: {e}")
        return "http://localhost:8080"

# Database already initialized above - no need for separate function

# In-memory storage for non-persistent data
storage_data = {
    "current_step": 4,  # Updated to step 4 for persistence demo
    "steps": [
        {"id": 1, "name": "Deploy ROKS Cluster", "status": "completed"},
        {"id": 2, "name": "Dashboard Overview", "status": "completed"},
        {"id": 3, "name": "Deploy Demo App", "status": "completed"},
        {"id": 4, "name": "Add Persistence", "status": "current"},
        {"id": 5, "name": "Resource Limits & Scaling", "status": "pending"},
        {"id": 6, "name": "Profit!", "status": "pending"}
    ],
    "deployment_info": {
        "app_name": "OpenShift Demo App - V2 with Persistence",
        "version": "2.0.0",
        "deployed_at": datetime.now().isoformat(),
        "namespace": detect_environment(),
        "hostname": get_hostname()
    }
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    return jsonify(storage_data)

@app.route('/api/step/<int:step_id>', methods=['POST'])
def complete_step(step_id):
    for step in storage_data["steps"]:
        if step["id"] == step_id:
            step["status"] = "completed"
            break
    
    # Update current step
    if step_id < 6:
        storage_data["current_step"] = step_id + 1
        for step in storage_data["steps"]:
            if step["id"] == step_id + 1:
                step["status"] = "current"
                break
    
    return jsonify({"success": True, "current_step": storage_data["current_step"]})

@app.route('/api/persistence/test', methods=['POST'])
def test_persistence():
    try:
        # Ensure database exists before any operations
        ensure_database()
        
        data = request.json or {}
        test_entry = PersistenceTest(
            data=data.get("data", f"Test data entry {datetime.now().strftime('%H:%M:%S')}")
        )
        db.session.add(test_entry)
        db.session.commit()
        
        print(f"Created database entry: {test_entry.id}")
        
        # Verify entry was saved
        saved_entry = PersistenceTest.query.get(test_entry.id)
        if saved_entry:
            print(f"Verified entry in database: {saved_entry.id}")
            return jsonify({"success": True, "entry": saved_entry.to_dict()})
        else:
            return jsonify({"success": False, "error": "Entry not found after save"}), 500
            
    except Exception as e:
        db.session.rollback()
        print(f"Database error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/persistence/data')
def get_persistence_data():
    try:
        entries = PersistenceTest.query.order_by(PersistenceTest.timestamp.desc()).all()
        return jsonify([entry.to_dict() for entry in entries])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/persistence/stats')
def get_persistence_stats():
    try:
        # Ensure database exists before any operations
        ensure_database()
        
        total_entries = PersistenceTest.query.count()
        latest_entry = PersistenceTest.query.order_by(PersistenceTest.timestamp.desc()).first()
        all_entries = PersistenceTest.query.all()
        
        return jsonify({
            "total_entries": total_entries,
            "latest_entry": latest_entry.to_dict() if latest_entry else None,
            "database_type": "PostgreSQL" if "postgresql" in app.config['SQLALCHEMY_DATABASE_URI'] else "SQLite",
            "database_url": app.config['SQLALCHEMY_DATABASE_URI'],
            "all_entry_ids": [e.id for e in all_entries]
        })
    except Exception as e:
        print(f"Error getting stats: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/debug/cgroups')
def debug_cgroups():
    """Debug cgroups detection for troubleshooting"""
    debug_info = {
        "cgroups_v2_paths": {},
        "cgroups_v1_paths": {},
        "filesystem_check": {},
        "error_log": []
    }
    
    # Check cgroups v2 paths
    v2_paths = [
        '/sys/fs/cgroup/cpu.max',
        '/sys/fs/cgroup/memory.current', 
        '/sys/fs/cgroup/memory.max'
    ]
    
    for path in v2_paths:
        try:
            with open(path, 'r') as f:
                content = f.read().strip()
                debug_info["cgroups_v2_paths"][path] = content[:100]  # Limit output
        except Exception as e:
            debug_info["cgroups_v2_paths"][path] = f"Error: {str(e)}"
    
    # Check cgroups v1 paths
    v1_paths = [
        '/sys/fs/cgroup/cpu/cpu.cfs_quota_us',
        '/sys/fs/cgroup/cpu/cpu.cfs_period_us',
        '/sys/fs/cgroup/memory/memory.usage_in_bytes',
        '/sys/fs/cgroup/memory/memory.limit_in_bytes'
    ]
    
    for path in v1_paths:
        try:
            with open(path, 'r') as f:
                content = f.read().strip()
                debug_info["cgroups_v1_paths"][path] = content[:100]  # Limit output
        except Exception as e:
            debug_info["cgroups_v1_paths"][path] = f"Error: {str(e)}"
    
    # Check if /sys/fs/cgroup exists
    import os
    debug_info["filesystem_check"] = {
        "/sys/fs/cgroup exists": os.path.exists("/sys/fs/cgroup"),
        "/sys/fs/cgroup/cpu exists": os.path.exists("/sys/fs/cgroup/cpu"),
        "/sys/fs/cgroup/memory exists": os.path.exists("/sys/fs/cgroup/memory"),
        "cwd": os.getcwd(),
        "environment_type": detect_environment()
    }
    
    return jsonify(debug_info)

@app.route('/api/debug/db')
def debug_database():
    try:
        # Test database connection
        result = db.session.execute(text('SELECT 1')).scalar()
        entries = PersistenceTest.query.all()
        
        return jsonify({
            "connection_test": result,
            "table_exists": True,
            "total_entries": len(entries),
            "entries": [e.to_dict() for e in entries],
            "database_url": app.config['SQLALCHEMY_DATABASE_URI']
        })
    except Exception as e:
        return jsonify({
            "error": str(e),
            "database_url": app.config['SQLALCHEMY_DATABASE_URI']
        }), 500

@app.route('/api/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": storage_data["deployment_info"]["version"],
        "psutil_available": PSUTIL_AVAILABLE
    })

def get_container_resources():
    """Get container resource utilization (container-level metrics)"""
    resources = {
        "cpu_percent": 0,
        "cpu_limit_cores": 0,
        "cpu_limit_percent": 0,
        "memory_percent": 0,
        "memory_used_mb": 0,
        "memory_total_mb": 0,
        "memory_limit_mb": 0,
        "memory_limit_percent": 0,
        "cpu_limit": "unknown",
        "metrics_source": "unavailable"
    }
    
    try:
        # First, try to get container limits from cgroups for accurate pod metrics
        cpu_limit_cores = None
        memory_limit_bytes = None
        memory_current_bytes = None
        
        # Try to get container limits and current usage from cgroups
        try:
            print("V2: Attempting cgroups detection...")
            # CPU limits - cgroups v2 first
            try:
                with open('/sys/fs/cgroup/cpu.max', 'r') as f:
                    cpu_max = f.read().strip()
                    print(f"V2: Found cgroups v2 cpu.max: {cpu_max}")
                    if cpu_max != 'max':
                        quota, period = cpu_max.split()
                        if int(quota) > 0:
                            cpu_limit_cores = int(quota) / int(period)
                            print(f"V2: Detected CPU limit: {cpu_limit_cores} cores")
            except FileNotFoundError:
                print("V2: cgroups v2 CPU not found, trying v1...")
                # Try cgroups v1
                try:
                    with open('/sys/fs/cgroup/cpu/cpu.cfs_quota_us', 'r') as f:
                        quota = int(f.read().strip())
                    with open('/sys/fs/cgroup/cpu/cpu.cfs_period_us', 'r') as f:
                        period = int(f.read().strip())
                    print(f"V2: Found cgroups v1 CPU quota={quota}, period={period}")
                    if quota > 0:
                        cpu_limit_cores = quota / period
                        print(f"V2: Detected CPU limit: {cpu_limit_cores} cores")
                except FileNotFoundError:
                    print("V2: cgroups v1 CPU not found")
                    pass
            
            # Memory limits and current usage - cgroups v2 first
            try:
                with open('/sys/fs/cgroup/memory.current', 'r') as f:
                    memory_current_bytes = int(f.read().strip())
                with open('/sys/fs/cgroup/memory.max', 'r') as f:
                    memory_max_str = f.read().strip()
                    print(f"V2: Found cgroups v2 memory.max: {memory_max_str}")
                    if memory_max_str != 'max':
                        memory_limit_bytes = int(memory_max_str)
                        print(f"V2: Detected memory limit: {memory_limit_bytes / 1024 / 1024:.1f} MB")
            except FileNotFoundError:
                print("V2: cgroups v2 memory not found, trying v1...")
                # Try cgroups v1
                try:
                    with open('/sys/fs/cgroup/memory/memory.usage_in_bytes', 'r') as f:
                        memory_current_bytes = int(f.read().strip())
                    with open('/sys/fs/cgroup/memory/memory.limit_in_bytes', 'r') as f:
                        memory_limit_bytes = int(f.read().strip())
                        print(f"V2: Found cgroups v1 memory limit: {memory_limit_bytes / 1024 / 1024:.1f} MB")
                        # cgroups v1 sometimes reports very large numbers that aren't real limits
                        if memory_limit_bytes > (1024**4):  # If > 1TB, probably not a real limit
                            print("V2: Memory limit too large, probably not real - ignoring")
                            memory_limit_bytes = None
                except FileNotFoundError:
                    print("V2: cgroups v1 memory not found")
                    pass
                    
        except Exception as cgroup_error:
            print(f"Error reading cgroups: {cgroup_error}")
        
        # If we have container limits, use them for accurate pod metrics
        if memory_limit_bytes and memory_current_bytes:
            print("V2: Using cgroups for accurate container metrics")
            resources["memory_used_mb"] = round(memory_current_bytes / 1024 / 1024, 1)
            resources["memory_total_mb"] = round(memory_limit_bytes / 1024 / 1024, 1)
            resources["memory_limit_mb"] = round(memory_limit_bytes / 1024 / 1024, 1)
            resources["memory_percent"] = round((memory_current_bytes / memory_limit_bytes) * 100, 1)
            resources["memory_limit_percent"] = resources["memory_percent"]
            resources["metrics_source"] = "cgroups"
            
            if cpu_limit_cores:
                resources["cpu_limit_cores"] = round(cpu_limit_cores, 2)
                resources["cpu_limit"] = f"{cpu_limit_cores:.1f} cores"
                
            # Get CPU usage from psutil if available, otherwise estimate
            if PSUTIL_AVAILABLE:
                cpu_percent = psutil.cpu_percent(interval=0.1)
                resources["cpu_percent"] = round(cpu_percent, 1)
                
                # Calculate CPU vs limit if we have a limit
                if cpu_limit_cores:
                    total_cores = psutil.cpu_count()
                    if total_cores:
                        actual_cpu_usage = (cpu_percent / 100) * total_cores
                        resources["cpu_limit_percent"] = round((actual_cpu_usage / cpu_limit_cores) * 100, 1)
            
        elif PSUTIL_AVAILABLE:
            print("V2: Using psutil for host metrics (no container limits detected)")
            # Fallback to psutil but only if no container limits found
            resources["cpu_percent"] = round(psutil.cpu_percent(interval=0.1), 1)
            memory = psutil.virtual_memory()
            resources["memory_percent"] = round(memory.percent, 1)
            resources["memory_used_mb"] = round(memory.used / 1024 / 1024, 1)
            resources["memory_total_mb"] = round(memory.total / 1024 / 1024, 1)
            resources["metrics_source"] = "psutil"
            
            # Still try to get CPU limits for display
            if cpu_limit_cores:
                resources["cpu_limit_cores"] = round(cpu_limit_cores, 2)
                resources["cpu_limit"] = f"{cpu_limit_cores:.1f} cores"
        else:
            print("No container limits detected and psutil unavailable")
            resources["metrics_source"] = "unavailable"
    except Exception as e:
        print(f"Error getting resource metrics: {e}")
        resources["metrics_source"] = "error"
    
    print(f"Resource metrics: {resources}")
    return resources

@app.route('/api/metrics')
def metrics():
    try:
        persistence_count = PersistenceTest.query.count()
    except:
        persistence_count = 0
    
    # Get current pod/container information
    container_info = {
        "hostname": get_hostname(),
        "namespace": detect_environment()
    }
    
    # Get container resource utilization
    resources = get_container_resources()
    container_info.update(resources)
    
    # Get network/connection information
    network_info = get_network_connections()
    
    return jsonify({
        "total_steps": len(storage_data["steps"]),
        "completed_steps": len([s for s in storage_data["steps"] if s["status"] == "completed"]),
        "current_step": storage_data["current_step"],
        "persistence_entries": persistence_count,
        "database_connected": True,
        "uptime": "running",
        "container": container_info,
        "network": network_info
    })

@app.route('/api/traffic/generate', methods=['POST'])
def generate_external_traffic():
    """Send traffic generation request to external serverless function"""
    try:
        # Get configuration for external traffic generator
        traffic_endpoint = os.environ.get('TRAFFIC_GENERATOR_URL')
        if not traffic_endpoint:
            # Default to Code Engine traffic generation function
            traffic_endpoint = 'https://traffic-gen-fn.17rgnniognng.us-south.codeengine.appdomain.cloud'
        
        # Get the current application URL
        app_url = get_app_url()
        
        # Prepare payload for the Code Engine traffic generator
        payload = {
            "url": app_url,  # Code Engine function expects 'url', not 'target_url'
            "duration": 60,  # 1 minute of traffic (max 300s per function limit)
            "requests_per_second": 10  # 10 RPS (max 50 per function limit)
        }
        
        # Send request to external traffic generator
        response = requests.post(
            traffic_endpoint,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json() if response.content else {}
            return jsonify({
                "success": True,
                "message": "External traffic generation completed",
                "app_url": app_url,
                "traffic_endpoint": traffic_endpoint,
                "duration": "60 seconds",
                "rate": "10 req/sec",
                "generator_response": result,
                "requests_sent": result.get("result", {}).get("requests_sent", 0),
                "errors": result.get("result", {}).get("errors", 0)
            })
        else:
            error_msg = f"Traffic generator responded with {response.status_code}"
            try:
                error_detail = response.json()
                if response.status_code == 403 and 'containers.appdomain.cloud' in str(error_detail):
                    error_msg = f"Domain validation failed - Code Engine function only accepts .containers.appdomain.cloud domains. Current URL: {app_url}"
                else:
                    error_msg += f": {error_detail.get('error', 'Unknown error')}"
            except:
                pass
            
            return jsonify({
                "success": False,
                "error": error_msg,
                "app_url": app_url,
                "traffic_endpoint": traffic_endpoint
            }), 500
            
    except requests.exceptions.Timeout:
        return jsonify({
            "success": False,
            "error": "Traffic generator request timed out",
            "app_url": get_app_url()
        }), 500
    except requests.exceptions.RequestException as e:
        return jsonify({
            "success": False,
            "error": f"Failed to contact traffic generator: {str(e)}",
            "app_url": get_app_url()
        }), 500
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "app_url": get_app_url()
        }), 500

if __name__ == '__main__':
    # Initialize database on startup
    ensure_database()
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)