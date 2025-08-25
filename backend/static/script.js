// API Configuration
const API_BASE = 'http://localhost:8000';
let refreshInterval;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    updateConnectionStatus('connecting');
    loadDashboardData();
    setupEventListeners();
    startAutoRefresh();
    loadWebhookConfig();
});

// Setup event listeners
function setupEventListeners() {
    document.getElementById('refresh-btn').addEventListener('click', function() {
        this.disabled = true;
        this.innerHTML = '🔄 Refreshing...';
        
        loadDashboardData().finally(() => {
            this.disabled = false;
            this.innerHTML = '🔄 Refresh';
        });
    });
    
    document.getElementById('copy-url').addEventListener('click', copyWebhookUrl);
}

// Update connection status
function updateConnectionStatus(status) {
    const statusElement = document.getElementById('connection-status');
    statusElement.className = `status-indicator ${status}`;
    
    switch(status) {
        case 'connected':
            statusElement.textContent = '✅ Connected';
            break;
        case 'disconnected':
            statusElement.textContent = '❌ Disconnected';
            break;
        case 'connecting':
            statusElement.textContent = '🔄 Connecting...';
            break;
    }
}

// Load all dashboard data
async function loadDashboardData() {
    try {
        // Test API connectivity
        const healthResponse = await fetch(`${API_BASE}/health`);
        if (!healthResponse.ok) throw new Error('API not responding');
        
        updateConnectionStatus('connected');
        
        // Load data in parallel
        const [metricsData, buildsData] = await Promise.all([
            loadMetrics(),
            loadBuilds()
        ]);
        
        updateLastUpdated();
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        updateConnectionStatus('disconnected');
        showError(`Failed to load data: ${error.message}`);
    }
}

// Load metrics summary
async function loadMetrics() {
    try {
        const response = await fetch(`${API_BASE}/api/metrics/summary`);
        const data = await response.json();
        
        updateMetrics(data);
        return data;
    } catch (error) {
        console.error('Error loading metrics:', error);
        throw error;
    }
}

// Load recent builds
async function loadBuilds() {
    try {
        const response = await fetch(`${API_BASE}/api/builds?limit=10`);
        const data = await response.json();
        
        updateBuilds(data.builds || []);
        document.getElementById('total-builds').textContent = data.total || 0;
        
        // Update latest commit status if we have builds
        if (data.builds && data.builds.length > 0) {
            updateLatestCommitStatus(data.builds[0]);
        }
        
        return data;
    } catch (error) {
        console.error('Error loading builds:', error);
        throw error;
    }
}

// Update metrics display
function updateMetrics(data) {
    document.getElementById('success-rate').textContent = 
        data.success_rate ? `${Math.round(data.success_rate * 100)}%` : '--';
    
    document.getElementById('avg-build-time').textContent = 
        data.avg_build_time_seconds ? `${Math.round(data.avg_build_time_seconds)}s` : '--';
    
    const statusElement = document.getElementById('last-build-status');
    statusElement.textContent = data.last_build_status || '--';
    statusElement.className = `metric-value ${data.last_build_status || ''}`;
}

// Update builds list
function updateBuilds(builds) {
    const container = document.getElementById('builds-container');
    
    if (!builds || builds.length === 0) {
        container.innerHTML = '<div class="loading">No builds found</div>';
        return;
    }
    
    const buildsHtml = builds.map(build => {
        const statusClass = build.status || 'unknown';
        // Fix timestamp formatting with proper IST timezone handling
        let buildTime = 'Unknown';
        if (build.started_at) {
            try {
                // Handle timestamps that might be missing timezone info
                let dateStr = build.started_at;
                // If timestamp doesn't end with Z or timezone info, assume it's UTC
                if (!dateStr.endsWith('Z') && !dateStr.includes('+') && !dateStr.includes('-', 10)) {
                    dateStr += 'Z'; // Treat as UTC
                }
                const date = new Date(dateStr);
                
                // Convert to IST explicitly
                buildTime = date.toLocaleString('en-IN', {
                    timeZone: 'Asia/Kolkata',
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit',
                    second: '2-digit',
                    timeZoneName: 'short'
                });
            } catch (e) {
                console.error('Date parsing error:', e, 'for timestamp:', build.started_at);
                buildTime = build.started_at;
            }
        }
        const duration = build.duration_seconds ? `${Math.round(build.duration_seconds)}s` : 'N/A';
        
        return `
            <div class="build-item ${statusClass}">
                <div class="build-info">
                    <div class="build-id">Build #${build.external_id || build.id}</div>
                    <div class="build-details">
                        ${buildTime} • Duration: ${duration} • Branch: ${build.branch || 'main'}
                        ${build.triggered_by ? `• By: ${build.triggered_by}` : ''}
                    </div>
                </div>
                <div class="build-status ${statusClass}">
                    ${statusClass}
                </div>
            </div>
        `;
    }).join('');
    
    container.innerHTML = buildsHtml;
}

// Show error message
function showError(message) {
    const container = document.getElementById('builds-container');
    container.innerHTML = `
        <div class="error-message">
            <strong>Error:</strong> ${message}
        </div>
    `;
}

// Update latest commit status section
function updateLatestCommitStatus(latestBuild) {
    if (!latestBuild) {
        // Set loading state if no data
        document.getElementById('latest-commit-status').textContent = 'No Data';
        document.getElementById('latest-commit-status').className = 'commit-status-badge loading';
        return;
    }
    
    // Update status badge
    const statusBadge = document.getElementById('latest-commit-status');
    statusBadge.textContent = latestBuild.status || 'Unknown';
    statusBadge.className = `commit-status-badge ${latestBuild.status || 'loading'}`;
    
    // Update build details
    document.getElementById('latest-build-id').textContent = `#${latestBuild.external_id || latestBuild.id}`;
    document.getElementById('latest-branch').textContent = latestBuild.branch || 'main';
    
    // Format commit SHA (show first 8 characters)
    const commitSha = latestBuild.commit_sha || 'unknown';
    document.getElementById('latest-commit-sha').textContent = commitSha.substring(0, 8) + (commitSha.length > 8 ? '...' : '');
    
    document.getElementById('latest-triggered-by').textContent = latestBuild.triggered_by || 'Unknown';
    
    // Format timestamps in IST with proper timezone handling
    let startedTime = 'Unknown';
    if (latestBuild.started_at) {
        try {
            // Handle timestamps that might be missing timezone info
            let dateStr = latestBuild.started_at;
            // If timestamp doesn't end with Z or timezone info, assume it's UTC
            if (!dateStr.endsWith('Z') && !dateStr.includes('+') && !dateStr.includes('-', 10)) {
                dateStr += 'Z'; // Treat as UTC
            }
            const date = new Date(dateStr);
            
            // Convert to IST explicitly
            startedTime = date.toLocaleString('en-IN', {
                timeZone: 'Asia/Kolkata',
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
                timeZoneName: 'short'
            });
        } catch (e) {
            console.error('Date parsing error for latest build:', e, 'for timestamp:', latestBuild.started_at);
            startedTime = latestBuild.started_at;
        }
    }
    document.getElementById('latest-started-at').textContent = startedTime;
    
    // Format duration
    const duration = latestBuild.duration_seconds 
        ? `${Math.round(latestBuild.duration_seconds)}s`
        : 'N/A';
    document.getElementById('latest-duration').textContent = duration;
    
    // Update build URL
    const buildLink = document.getElementById('latest-build-url');
    if (latestBuild.url) {
        buildLink.href = latestBuild.url;
        buildLink.textContent = 'View on GitHub';
        buildLink.style.display = 'inline';
    } else {
        buildLink.style.display = 'none';
    }
}

// Update last updated timestamp in IST
function updateLastUpdated() {
    const now = new Date();
    const timeString = now.toLocaleString('en-IN', {
        timeZone: 'Asia/Kolkata',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        timeZoneName: 'short'
    });
    document.getElementById('last-updated').textContent = timeString;
}

// Start auto-refresh
function startAutoRefresh() {
    // Refresh every 30 seconds
    refreshInterval = setInterval(loadDashboardData, 30000);
}

// Load webhook configuration
async function loadWebhookConfig() {
    // For now, we'll show a placeholder since we don't have the tunnel URL in the frontend
    // In a real implementation, this could be an API endpoint that returns the current webhook URL
    const webhookUrl = document.getElementById('webhook-url');
    webhookUrl.textContent = 'Check console or server logs for current tunnel URL';
}

// Copy webhook URL to clipboard
function copyWebhookUrl() {
    const webhookUrl = document.getElementById('webhook-url').textContent;
    
    if (navigator.clipboard) {
        navigator.clipboard.writeText(webhookUrl).then(() => {
            showNotification('Webhook URL copied to clipboard!');
        }).catch(err => {
            console.error('Failed to copy: ', err);
        });
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = webhookUrl;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showNotification('Webhook URL copied to clipboard!');
    }
}

// Show notification
function showNotification(message) {
    // Simple notification - in a real app you might use a proper notification library
    const originalText = document.getElementById('copy-url').textContent;
    const button = document.getElementById('copy-url');
    button.textContent = '✅';
    
    setTimeout(() => {
        button.textContent = originalText;
    }, 2000);
}

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
});
