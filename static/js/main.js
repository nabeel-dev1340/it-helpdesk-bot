// Main JavaScript file for IT Help Bot

// Global variables
let currentOS = 'Unknown';
// Note: isConnected is declared in chat.html to avoid conflicts

// Utility functions
function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatDate(date) {
    return new Date(date).toLocaleString();
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

function showLoading(elementId, message = 'Loading...') {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `
            <div class="text-center py-4">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2">${message}</p>
            </div>
        `;
    }
}

function hideLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = '';
    }
}

function showError(elementId, message) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `
            <div class="text-center text-danger">
                <i class="fas fa-exclamation-triangle fa-2x mb-2"></i>
                <p>${message}</p>
            </div>
        `;
    }
}

// API functions
async function apiCall(endpoint, method = 'GET', data = null) {
    try {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            }
        };
        
        if (data) {
            options.body = JSON.stringify(data);
        }
        
        const response = await fetch(endpoint, options);
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'API request failed');
        }
        
        return result;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// System information functions
async function getSystemInfo() {
    try {
        const data = await apiCall('/api/system-info');
        return data;
    } catch (error) {
        console.error('Error getting system info:', error);
        throw error;
    }
}

async function runNetworkTest() {
    try {
        const data = await apiCall('/api/network-test');
        return data;
    } catch (error) {
        console.error('Error running network test:', error);
        throw error;
    }
}

async function executeCommand(command) {
    try {
        const data = await apiCall('/api/execute-command', 'POST', { command: command });
        return data;
    } catch (error) {
        console.error('Error executing command:', error);
        throw error;
    }
}

// Chat functions
function initializeChat() {
    // This function will be overridden by chat.js if on chat page
    console.log('Chat not initialized - not on chat page');
}

// Modal functions
function showModal(modalId) {
    const modal = new bootstrap.Modal(document.getElementById(modalId));
    modal.show();
}

function hideModal(modalId) {
    const modal = bootstrap.Modal.getInstance(document.getElementById(modalId));
    if (modal) {
        modal.hide();
    }
}

// Form validation
function validateInput(input, minLength = 1, maxLength = 1000) {
    const value = input.value.trim();
    
    if (value.length < minLength) {
        return { valid: false, message: `Input must be at least ${minLength} characters long` };
    }
    
    if (value.length > maxLength) {
        return { valid: false, message: `Input must be no more than ${maxLength} characters long` };
    }
    
    return { valid: true, message: '' };
}

// Security functions
function sanitizeInput(input) {
    return input.replace(/[<>\"'&]/g, '');
}

function validateCommand(command) {
    // Basic command validation
    const dangerousPatterns = [
        'rm -rf', 'del /s', 'format', 'fdisk', 'dd',
        'sudo', 'su', 'chmod 777', 'chown root',
        'wget', 'curl', 'nc', 'telnet', 'ssh'
    ];
    
    const commandLower = command.toLowerCase();
    
    for (const pattern of dangerousPatterns) {
        if (commandLower.includes(pattern)) {
            return { valid: false, message: `Command contains dangerous pattern: ${pattern}` };
        }
    }
    
    return { valid: true, message: '' };
}

// UI helper functions
function updateConnectionStatus(status, type) {
    const statusElements = document.querySelectorAll('.connection-status');
    statusElements.forEach(element => {
        element.innerHTML = `
            <span class="badge bg-${type}">
                <i class="fas fa-circle me-1"></i>${status}
            </span>
        `;
    });
}

function updateOSBadge(osType) {
    const osElements = document.querySelectorAll('.os-badge');
    osElements.forEach(element => {
        element.textContent = osType;
    });
}

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Initialize common functionality
    initializeCommon();
    
    // Add global error handler
    window.addEventListener('error', function(event) {
        console.error('Global error:', event.error);
        showNotification('An error occurred. Please try again.', 'danger');
    });
    
    // Add unhandled promise rejection handler
    window.addEventListener('unhandledrejection', function(event) {
        console.error('Unhandled promise rejection:', event.reason);
        showNotification('An error occurred. Please try again.', 'danger');
    });
});

function initializeCommon() {
    // Load system information if on home page
    if (window.location.pathname === '/' || window.location.pathname === '/index.html') {
        loadSystemOverview();
    }
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

// Export functions for use in other scripts
window.ITHelpBot = {
    formatBytes,
    formatDate,
    showNotification,
    showLoading,
    hideLoading,
    showError,
    apiCall,
    getSystemInfo,
    runNetworkTest,
    executeCommand,
    showModal,
    hideModal,
    validateInput,
    sanitizeInput,
    validateCommand,
    updateConnectionStatus,
    updateOSBadge
}; 