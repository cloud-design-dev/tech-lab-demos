class OpenShiftDemo {
    constructor() {
        this.currentStep = 3;
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadStatus();
        this.loadMetrics(); // Load metrics immediately on page load
        this.startStatusUpdates();
    }

    bindEvents() {
        document.getElementById('test-persistence').addEventListener('click', () => this.testPersistence());
        document.getElementById('reload-demo').addEventListener('click', () => this.reloadDemo());
        document.getElementById('traffic-generator').addEventListener('click', () => this.openTrafficGenerator());
        document.getElementById('view-api-status').addEventListener('click', () => this.viewApiStatus());
    }

    async loadStatus() {
        try {
            const response = await fetch('/api/status');
            const data = await response.json();
            this.updateUI(data);
        } catch (error) {
            console.error('Error loading status:', error);
            this.updateStatus('app-status', 'Error loading status');
        }
    }

    updateUI(data) {
        this.currentStep = data.current_step;
        
        // Update step statuses
        data.steps.forEach(step => {
            const stepElement = document.querySelector(`[data-step="${step.id}"]`);
            if (stepElement) {
                stepElement.className = `step ${step.status}`;
                const badge = stepElement.querySelector('.status-badge');
                if (badge) {
                    badge.className = `status-badge ${step.status}`;
                    badge.textContent = step.status.toUpperCase();
                }
                
                // Update "you are here" indicator
                const youAreHere = stepElement.querySelector('.you-are-here');
                if (step.status === 'current') {
                    if (!youAreHere) {
                        const indicator = document.createElement('div');
                        indicator.className = 'you-are-here';
                        stepElement.appendChild(indicator);
                    }
                } else if (youAreHere) {
                    youAreHere.remove();
                }
            }
        });

        this.updateStatus('app-status', `
            <strong>Current Step:</strong> ${this.currentStep}<br>
            <strong>Completed:</strong> ${data.steps.filter(s => s.status === 'completed').length}/6<br>
            <strong>Namespace:</strong> ${data.deployment_info.namespace}<br>
            <strong>Version:</strong> ${data.deployment_info.version}
        `);
    }

    async testPersistence() {
        this.updateStatus('persistence-status', 'Testing persistence...');
        
        try {
            const testData = {
                data: `Test entry ${Date.now()}`,
                timestamp: new Date().toISOString()
            };

            const response = await fetch('/api/persistence/test', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(testData)
            });

            const result = await response.json();
            
            if (result.success) {
                this.updateStatus('persistence-status', `
                    <strong>✅ Success!</strong><br>
                    Entry ID: ${result.entry.id}<br>
                    Data: ${result.entry.data}<br>
                    Time: ${new Date(result.entry.timestamp).toLocaleTimeString()}
                `);
            } else {
                this.updateStatus('persistence-status', '❌ Persistence test failed');
            }
        } catch (error) {
            console.error('Persistence test error:', error);
            this.updateStatus('persistence-status', '❌ Error testing persistence');
        }
    }

    reloadDemo() {
        this.updateStatus('app-status', 'Reloading page to demonstrate data loss...');
        this.updateStatus('persistence-status', 'Watch the ID counter reset to 0 after reload!');
        
        setTimeout(() => {
            window.location.reload();
        }, 2000);
    }


    async loadMetrics() {
        try {
            const response = await fetch('/api/metrics');
            const metrics = await response.json();
            this.displayMetrics(metrics);
        } catch (error) {
            console.error('Error loading metrics:', error);
            this.updateStatus('metrics-display', '❌ Error loading metrics');
        }
    }


    displayMetrics(metrics) {
        let metricsHtml = '<strong>📊 Pod Resource Metrics</strong><br>';
        
        if (metrics.container && metrics.container.memory_total_mb > 0) {
            const container = metrics.container;
            
            // CPU Utilization
            metricsHtml += `<strong>🔥 CPU Utilization:</strong> ${container.cpu_percent}%`;
            if (container.cpu_limit_cores > 0) {
                metricsHtml += ` / ${container.cpu_limit}<br>`;
                metricsHtml += `<strong>📈 CPU vs Limit:</strong> ${container.cpu_limit_percent}%<br>`;
            } else {
                metricsHtml += ' (no limit)<br>';
            }
            
            // Memory Utilization - only show pod-level metrics when we have container limits
            if (container.metrics_source === 'cgroups') {
                // Pod-level metrics from container limits
                metricsHtml += `<strong>🧠 RAM Utilization:</strong> ${container.memory_percent}% (${container.memory_used_mb}/${container.memory_total_mb} MB)<br>`;
                metricsHtml += `<strong>📊 RAM vs Limit:</strong> ${container.memory_percent}% (${container.memory_used_mb}/${container.memory_limit_mb} MB)<br>`;
            } else {
                // Host metrics when container limits not available
                metricsHtml += `<strong>🧠 RAM Utilization:</strong> ${container.memory_percent}% (${container.memory_used_mb}/${container.memory_total_mb} MB)<br>`;
                if (container.memory_limit_mb > 0) {
                    metricsHtml += `<strong>📊 RAM vs Limit:</strong> ${container.memory_limit_percent}% (${container.memory_used_mb}/${container.memory_limit_mb} MB)<br>`;
                } else {
                    metricsHtml += `<em>Deploy to OpenShift to see pod-level limits</em><br>`;
                }
            }
            
            // Network/Connection Info
            if (metrics.network) {
                const network = metrics.network;
                metricsHtml += `<br><strong>🌐 Inbound Connections:</strong><br>`;
                metricsHtml += `Active: ${network.active_connections}<br>`;
                metricsHtml += `Total Requests: ${network.total_requests}<br>`;
                metricsHtml += `Rate: ${network.requests_per_minute} req/min<br>`;
                
                if (network.top_endpoints.length > 0) {
                    metricsHtml += `<strong>Top Endpoints:</strong><br>`;
                    network.top_endpoints.forEach(ep => {
                        metricsHtml += `• ${ep.endpoint}: ${ep.count}<br>`;
                    });
                }
            }
            
            // Source information
            let sourceLabel = '';
            switch(container.metrics_source) {
                case 'psutil': sourceLabel = '(Host System)'; break;
                case 'cgroups': sourceLabel = '(Pod Limits)'; break;
                case 'proc_meminfo': sourceLabel = '(Host Fallback)'; break;
                default: sourceLabel = '(Unknown Source)'; break;
            }
            metricsHtml += `<br><small>Source: ${sourceLabel}</small><br>`;
            
        } else {
            metricsHtml += 'Resource metrics unavailable<br>';
        }
        
        metricsHtml += `<small>Updated: ${new Date().toLocaleTimeString()}</small>`;
        
        this.updateStatus('metrics-display', metricsHtml);
    }

    viewApiStatus() {
        // Open the API stats endpoint in a new window
        window.open('/api/persistence/stats', '_blank');
    }

    openTrafficGenerator() {
        // Open traffic generator (placeholder for now)
        window.open('https://example.com', '_blank');
    }

    updateStatus(elementId, content) {
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = content;
        }
    }

    startStatusUpdates() {
        // Update status and metrics every 30 seconds
        setInterval(() => {
            this.loadStatus();
            this.loadMetrics();
        }, 30000);
    }
}

// Add celebration animation
const style = document.createElement('style');
style.textContent = `
    @keyframes celebration {
        0%, 100% { transform: scale(1) rotate(0deg); }
        25% { transform: scale(1.02) rotate(1deg); }
        75% { transform: scale(1.02) rotate(-1deg); }
    }
`;
document.head.appendChild(style);

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new OpenShiftDemo();
});