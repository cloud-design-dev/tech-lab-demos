class OpenShiftDemo {
    constructor() {
        this.currentStep = 3;
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadStatus();
        this.loadPersistenceStatus();  // Load DB stats on page load
        this.loadMetrics();  // Load metrics on page load
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
            <strong>Hostname:</strong> ${data.deployment_info.hostname}<br>
            <strong>Version:</strong> ${data.deployment_info.version}
        `);
    }

    async loadPersistenceStatus() {
        try {
            const response = await fetch('/api/persistence/stats');
            const stats = await response.json();
            
            if (stats.total_entries > 0) {
                this.updateStatus('persistence-status', `
                    <strong>📊 Database Status</strong><br>
                    Total Entries: ${stats.total_entries}<br>
                    Database: ${stats.database_type}<br>
                    Last Entry: ${stats.latest_entry ? new Date(stats.latest_entry.timestamp).toLocaleTimeString() : 'None'}<br>
                    Status: Connected ✅
                `);
            } else {
                this.updateStatus('persistence-status', `
                    <strong>📊 Database Ready</strong><br>
                    Total Entries: 0<br>
                    Database: ${stats.database_type}<br>
                    Status: Connected & Ready ✅
                `);
            }
        } catch (error) {
            console.error('Error loading persistence status:', error);
            this.updateStatus('persistence-status', 'Database connection error ❌');
        }
    }

    async testPersistence() {
        this.updateStatus('persistence-status', 'Testing database persistence...');
        
        try {
            const testData = {
                data: `Database test entry ${Date.now()}`
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
                // Get persistence stats to show total entries
                const statsResponse = await fetch('/api/persistence/stats');
                const stats = await statsResponse.json();
                
                this.updateStatus('persistence-status', `
                    <strong>✅ Database Persistence Working!</strong><br>
                    Entry ID: ${result.entry.id}<br>
                    Data: ${result.entry.data}<br>
                    Total DB Entries: ${stats.total_entries || 0}<br>
                    Database: ${stats.database_type || 'Unknown'}<br>
                    Time: ${new Date(result.entry.timestamp).toLocaleTimeString()}
                `);
                
                // Don't auto-complete Step 4 - let user control with checkbox
            } else {
                this.updateStatus('persistence-status', `❌ Database test failed: ${result.error}`);
            }
        } catch (error) {
            console.error('Persistence test error:', error);
            this.updateStatus('persistence-status', '❌ Error testing database persistence');
        }
    }

    reloadDemo() {
        this.updateStatus('app-status', 'Reloading page to verify data persistence...');
        this.updateStatus('persistence-status', 'Watch how database entries persist after reload! 🎯');
        
        setTimeout(() => {
            window.location.reload();
        }, 2000);
    }

    async simulateTraffic() {
        this.updateStatus('metrics-display', '🚀 Contacting Code Engine traffic generator...');
        
        try {
            // Call the external traffic generation endpoint
            const response = await fetch('/api/traffic/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const result = await response.json();
            
            if (result.success) {
                const requests_sent = result.requests_sent || 0;
                const errors = result.errors || 0;
                const success_rate = requests_sent > 0 ? ((requests_sent / (requests_sent + errors)) * 100).toFixed(1) : '0';
                
                this.updateStatus('metrics-display', `
                    <strong>🚦 Code Engine Traffic Generation Complete!</strong><br>
                    Target: ${result.app_url}<br>
                    Duration: ${result.duration} @ ${result.rate}<br>
                    Requests Sent: ${requests_sent}<br>
                    Errors: ${errors}<br>
                    Success Rate: ${success_rate}%<br>
                    Generator: traffic-gen-fn.codeengine<br>
                    Time: ${new Date().toLocaleTimeString()}
                `);
            } else {
                // Fallback to local traffic generation
                console.warn('External traffic generator failed, falling back to local:', result.error);
                await this.simulateLocalTraffic();
                
                this.updateStatus('metrics-display', `
                    <strong>🚦 Local Traffic Generated (Fallback)</strong><br>
                    External generator error: ${result.error}<br>
                    Local requests: 10<br>
                    Time: ${new Date().toLocaleTimeString()}
                `);
            }
            
            // Auto-complete scaling step if we're on it
            if (this.currentStep === 5) {
                setTimeout(() => this.completeCurrentStep(), 3000);
            }
        } catch (error) {
            console.error('Traffic generation error:', error);
            // Fallback to local traffic generation
            await this.simulateLocalTraffic();
            this.updateStatus('metrics-display', `
                <strong>🚦 Local Traffic Generated (Fallback)</strong><br>
                Code Engine function unavailable<br>
                Local requests: 10<br>
                Time: ${new Date().toLocaleTimeString()}
            `);
        }
    }
    
    async simulateLocalTraffic() {
        // Fallback: simulate local traffic like before
        const requests = [];
        for (let i = 0; i < 10; i++) {
            requests.push(
                fetch('/api/health').then(r => r.json())
            );
        }
        await Promise.all(requests);
    }

    async loadMetrics() {
        try {
            const response = await fetch('/api/metrics');
            const metrics = await response.json();
            
            let resourceInfo = '';
            if (metrics.container && metrics.container.memory_total_mb > 0) {
                const container = metrics.container;
                
                // CPU Utilization
                resourceInfo += `<br><strong>🔥 CPU Utilization:</strong> ${container.cpu_percent}%`;
                if (container.cpu_limit_cores > 0) {
                    resourceInfo += ` / ${container.cpu_limit}<br>`;
                    resourceInfo += `<strong>📈 CPU vs Limit:</strong> ${container.cpu_limit_percent}%<br>`;
                } else {
                    resourceInfo += ' (no limit)<br>';
                }
                
                // Memory Utilization - show pod-level metrics when we have container limits
                if (container.metrics_source === 'cgroups') {
                    // Pod-level metrics from container limits
                    resourceInfo += `<strong>🧠 RAM Utilization:</strong> ${container.memory_percent}% (${container.memory_used_mb}/${container.memory_total_mb} MB)<br>`;
                    resourceInfo += `<strong>📊 RAM vs Limit:</strong> ${container.memory_percent}% (${container.memory_used_mb}/${container.memory_limit_mb} MB)<br>`;
                } else {
                    // Host metrics when container limits not available
                    resourceInfo += `<strong>🧠 RAM Utilization:</strong> ${container.memory_percent}% (${container.memory_used_mb}/${container.memory_total_mb} MB)<br>`;
                    if (container.memory_limit_mb > 0) {
                        resourceInfo += `<strong>📊 RAM vs Limit:</strong> ${container.memory_limit_percent}% (${container.memory_used_mb}/${container.memory_limit_mb} MB)<br>`;
                    } else {
                        resourceInfo += `<em>Deploy to OpenShift to see pod-level limits</em><br>`;
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
                resourceInfo += `<br><small>Source: ${sourceLabel}</small>`;
            } else {
                resourceInfo = '<br><strong>📊 Container Metrics:</strong><br>Resource metrics unavailable';
            }
            
            // Network/Connection Info
            let networkInfo = '';
            if (metrics.network) {
                const network = metrics.network;
                networkInfo += `<br><br><strong>🌐 Inbound Connections:</strong><br>`;
                networkInfo += `Active: ${network.active_connections}<br>`;
                networkInfo += `Total Requests: ${network.total_requests}<br>`;
                networkInfo += `Rate: ${network.requests_per_minute} req/min<br>`;
                
                if (network.top_endpoints.length > 0) {
                    networkInfo += `<strong>Top Endpoints:</strong><br>`;
                    network.top_endpoints.forEach(ep => {
                        networkInfo += `• ${ep.endpoint}: ${ep.count}<br>`;
                    });
                }
            }
            
            this.updateStatus('metrics-display', `
                <strong>📊 Container Resource Metrics</strong>${resourceInfo}${networkInfo}<br>
                Updated: ${new Date().toLocaleTimeString()}
            `);
        } catch (error) {
            this.updateStatus('metrics-display', '❌ Error fetching metrics');
        }
    }

    viewApiStatus() {
        // Open the persistence stats API endpoint in a new tab
        const baseUrl = window.location.origin;
        const apiUrl = `${baseUrl}/api/persistence/stats`;
        window.open(apiUrl, '_blank');
    }

    openTrafficGenerator() {
        // Open traffic generator (placeholder for now)
        window.open('https://example.com', '_blank');
    }

    async completeCurrentStep() {
        if (this.currentStep > 6) {
            this.updateStatus('app-status', 'All steps completed! 🎉');
            return;
        }

        try {
            const response = await fetch(`/api/step/${this.currentStep}`, {
                method: 'POST'
            });
            
            const result = await response.json();
            
            if (result.success) {
                // Reload status to update UI
                await this.loadStatus();
                
                if (result.current_step > 6) {
                    this.celebrateCompletion();
                }
            }
        } catch (error) {
            console.error('Error completing step:', error);
        }
    }

    celebrateCompletion() {
        this.updateStatus('app-status', '🎉 ALL STEPS COMPLETED! 🎉');
        
        // Add some celebration effects
        const container = document.querySelector('.container');
        container.style.animation = 'celebration 2s ease-in-out';
        
        setTimeout(() => {
            container.style.animation = '';
        }, 2000);
    }

    updateStatus(elementId, content) {
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = content;
        }
    }

    toggleStep4Complete() {
        const checkbox = document.getElementById('step4-complete');
        const connector45 = document.getElementById('connector-4-5');
        const connector56 = document.getElementById('connector-5-6');
        
        if (checkbox.checked) {
            // Only toggle Step 4 to completed and Step 5 to current, no further advancement
            if (this.currentStep === 4) {
                // Update connectors to show arrows
                connector45.textContent = '→';
                connector45.className = 'connector';
                connector56.textContent = '→';
                connector56.className = 'connector';
                
                // Mark step 4 as completed and step 5 as current
                this.currentStep = 5;
                this.updateStepStatus(4, 'completed');
                this.updateStepStatus(5, 'current');
            }
        } else {
            // Reset connectors to disabled state
            connector45.textContent = '⊘';
            connector45.className = 'connector disabled';
            connector56.textContent = '⊘';
            connector56.className = 'connector disabled';
            
            // Reset to step 4 being current
            this.currentStep = 4;
            this.updateStepStatus(4, 'current');
            this.updateStepStatus(5, 'pending');
        }
    }
    
    updateStepStatus(stepId, status) {
        const stepElement = document.querySelector(`[data-step="${stepId}"]`);
        if (stepElement) {
            stepElement.className = `step ${status}`;
            const badge = stepElement.querySelector('.status-badge');
            if (badge) {
                badge.className = `status-badge ${status}`;
                badge.textContent = status.toUpperCase();
            }
        }
    }

    startStatusUpdates() {
        // Update status every 30 seconds
        setInterval(() => {
            this.loadStatus();
            this.loadMetrics();  // Also refresh metrics
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
    window.openShiftDemo = new OpenShiftDemo();
});