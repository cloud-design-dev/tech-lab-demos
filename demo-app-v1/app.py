from flask import Flask, render_template, jsonify, request
import os
import json
import time
import subprocess
import socket
from datetime import datetime
from collections import defaultdict

# Try to import psutil for container metrics
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("psutil not available - container metrics will be limited")

app = Flask(__name__)

# Global request counter for tracking inbound connections
request_stats = {
    "total_requests": 0,
    "active_connections": 0,
    "requests_by_endpoint": defaultdict(int),
    "start_time": datetime.now()
}

# Session tracking for persistence reset
session_stats = {
    "last_main_page_access": None,
    "persistence_data_reset_time": datetime.now()
}

@app.before_request
def track_request():
    """Track incoming requests"""
    request_stats["total_requests"] += 1
    request_stats["active_connections"] += 1
    endpoint = request.endpoint or 'unknown'
    request_stats["requests_by_endpoint"][endpoint] += 1

@app.after_request
def track_response(response):
    """Track completed requests"""
    request_stats["active_connections"] = max(0, request_stats["active_connections"] - 1)
    return response

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
    """Get container hostname or local hostname"""
    try:
        return os.environ.get('HOSTNAME', 'localhost')
    except Exception:
        return 'localhost'

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
        request_stats["requests_by_endpoint"].items(), 
        key=lambda x: x[1], 
        reverse=True
    )[:3]
    connections_info["top_endpoints"] = [
        {"endpoint": ep, "count": count} for ep, count in sorted_endpoints
    ]
    
    return connections_info

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
            # CPU limits - cgroups v2 first
            try:
                with open('/sys/fs/cgroup/cpu.max', 'r') as f:
                    cpu_max = f.read().strip()
                    if cpu_max != 'max':
                        quota, period = cpu_max.split()
                        if int(quota) > 0:
                            cpu_limit_cores = int(quota) / int(period)
            except FileNotFoundError:
                # Try cgroups v1
                try:
                    with open('/sys/fs/cgroup/cpu/cpu.cfs_quota_us', 'r') as f:
                        quota = int(f.read().strip())
                    with open('/sys/fs/cgroup/cpu/cpu.cfs_period_us', 'r') as f:
                        period = int(f.read().strip())
                    if quota > 0:
                        cpu_limit_cores = quota / period
                except FileNotFoundError:
                    pass
            
            # Memory limits and current usage - cgroups v2 first
            try:
                with open('/sys/fs/cgroup/memory.current', 'r') as f:
                    memory_current_bytes = int(f.read().strip())
                with open('/sys/fs/cgroup/memory.max', 'r') as f:
                    memory_max_str = f.read().strip()
                    if memory_max_str != 'max':
                        memory_limit_bytes = int(memory_max_str)
            except FileNotFoundError:
                # Try cgroups v1
                try:
                    with open('/sys/fs/cgroup/memory/memory.usage_in_bytes', 'r') as f:
                        memory_current_bytes = int(f.read().strip())
                    with open('/sys/fs/cgroup/memory/memory.limit_in_bytes', 'r') as f:
                        memory_limit_bytes = int(f.read().strip())
                        # cgroups v1 sometimes reports very large numbers that aren't real limits
                        if memory_limit_bytes > (1024**4):  # If > 1TB, probably not a real limit
                            memory_limit_bytes = None
                except FileNotFoundError:
                    pass
                    
        except Exception as cgroup_error:
            print(f"Error reading cgroups: {cgroup_error}")
        
        # If we have container limits, use them for accurate pod metrics
        if memory_limit_bytes and memory_current_bytes:
            print("Using cgroups for accurate container metrics")
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
            print("Using psutil for host metrics (no container limits detected)")
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

# In-memory storage for demo purposes
storage_data = {
    "current_step": 3,
    "steps": [
        {"id": 1, "name": "Deploy ROKS Cluster", "status": "completed"},
        {"id": 2, "name": "Dashboard Overview", "status": "completed"},
        {"id": 3, "name": "Deploy Demo App", "status": "current"},
        {"id": 4, "name": "Add Persistence", "status": "pending"},
        {"id": 5, "name": "Resource Limits & Scaling", "status": "pending"},
        {"id": 6, "name": "Profit!", "status": "pending"}
    ],
    "persistence_test_data": [],
    "deployment_info": {
        "app_name": "OpenShift Demo App",
        "version": "1.0.0",
        "deployed_at": datetime.now().isoformat(),
        "namespace": detect_environment(),
        "hostname": get_hostname()
    }
}

def reset_persistence_data():
    """Reset persistence data to simulate in-memory loss on page reload"""
    storage_data["persistence_test_data"] = []
    session_stats["persistence_data_reset_time"] = datetime.now()
    print("Persistence data reset due to main page access")

@app.route('/')
def index():
    # Reset persistence data when main page is accessed
    # This simulates the ephemeral nature of in-memory storage
    reset_persistence_data()
    session_stats["last_main_page_access"] = datetime.now()
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
    data = request.json
    test_entry = {
        "id": len(storage_data["persistence_test_data"]) + 1,
        "data": data.get("data", "test data"),
        "timestamp": datetime.now().isoformat()
    }
    storage_data["persistence_test_data"].append(test_entry)
    return jsonify({"success": True, "entry": test_entry})

@app.route('/api/persistence/data')
def get_persistence_data():
    return jsonify(storage_data["persistence_test_data"])

@app.route('/api/persistence/stats')
def get_persistence_stats():
    """Show persistence statistics - demonstrates in-memory storage limitations"""
    return jsonify({
        "total_entries": len(storage_data["persistence_test_data"]),
        "storage_type": "in-memory",
        "persistence_level": "ephemeral",
        "data_survives_restart": False,
        "data_survives_page_reload": False,
        "entries": storage_data["persistence_test_data"],
        "warning": "Data will be lost when container restarts or page reloads",
        "last_data_reset": session_stats["persistence_data_reset_time"].isoformat(),
        "last_main_page_access": session_stats["last_main_page_access"].isoformat() if session_stats["last_main_page_access"] else None,
        "last_updated": datetime.now().isoformat()
    })

@app.route('/api/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": storage_data["deployment_info"]["version"]
    })

@app.route('/api/metrics')
def metrics():
    # Get container resource utilization
    resources = get_container_resources()
    container_info = {
        "hostname": get_hostname(),
        "namespace": detect_environment(),
        "psutil_available": PSUTIL_AVAILABLE
    }
    container_info.update(resources)
    
    # Get network/connection information
    network_info = get_network_connections()
    
    return jsonify({
        "total_steps": len(storage_data["steps"]),
        "completed_steps": len([s for s in storage_data["steps"] if s["status"] == "completed"]),
        "current_step": storage_data["current_step"],
        "persistence_entries": len(storage_data["persistence_test_data"]),
        "uptime": "running",
        "container": container_info,
        "network": network_info
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8085))
    app.run(host='0.0.0.0', port=port, debug=True)
