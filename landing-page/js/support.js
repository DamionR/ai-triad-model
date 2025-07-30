/**
 * Support Page JavaScript
 * Handles search functionality, status updates, and support interactions
 */

// Wait for DOM to be ready
document.addEventListener('DOMContentLoaded', function() {
    initializeSupportPage();
});

function initializeSupportPage() {
    initializeSupportSearch();
    initializeStatusDashboard();
    initializeSupportTracking();
    initializeAccessibilityEnhancements();
}

/**
 * Support Search Functionality
 */
function initializeSupportSearch() {
    const searchInput = document.getElementById('supportSearch');
    const searchBtn = document.querySelector('.support-search-btn');
    
    if (searchInput && searchBtn) {
        // Handle search on button click
        searchBtn.addEventListener('click', handleSupportSearch);
        
        // Handle search on Enter key
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                handleSupportSearch();
            }
        });
        
        // Real-time search suggestions
        searchInput.addEventListener('input', debounce(handleSearchSuggestions, 300));
    }
}

function handleSupportSearch() {
    const searchInput = document.getElementById('supportSearch');
    const query = searchInput.value.trim().toLowerCase();
    
    if (!query) return;
    
    // Track search
    trackSupportAction('search', { query: query });
    
    // Highlight matching content
    highlightSearchResults(query);
    
    // Scroll to first match
    const firstMatch = document.querySelector('.search-highlight');
    if (firstMatch) {
        firstMatch.scrollIntoView({ behavior: 'smooth', block: 'center' });
    } else {
        showNoResultsMessage();
    }
}

function handleSearchSuggestions(e) {
    const query = e.target.value.trim().toLowerCase();
    
    if (query.length < 2) {
        clearSearchHighlights();
        return;
    }
    
    // Simple client-side search
    const searchableElements = document.querySelectorAll('h3, p, .troubleshooting-question h3, .error-description strong');
    let foundMatches = false;
    
    searchableElements.forEach(element => {
        const text = element.textContent.toLowerCase();
        if (text.includes(query)) {
            element.classList.add('search-preview');
            foundMatches = true;
        } else {
            element.classList.remove('search-preview');
        }
    });
    
    // Update search button state
    const searchBtn = document.querySelector('.support-search-btn');
    if (foundMatches) {
        searchBtn.style.background = '#10B981';
    } else {
        searchBtn.style.background = '';
    }
}

function highlightSearchResults(query) {
    clearSearchHighlights();
    
    const searchableElements = document.querySelectorAll('h3, p, .troubleshooting-question h3, .error-description strong');
    
    searchableElements.forEach(element => {
        const text = element.textContent.toLowerCase();
        if (text.includes(query)) {
            element.classList.add('search-highlight');
            // Add temporary highlight styling
            element.style.backgroundColor = 'rgba(139, 92, 246, 0.2)';
            element.style.borderRadius = '4px';
            element.style.padding = '4px 8px';
            element.style.margin = '2px 0';
        }
    });
}

function clearSearchHighlights() {
    const highlighted = document.querySelectorAll('.search-highlight, .search-preview');
    highlighted.forEach(element => {
        element.classList.remove('search-highlight', 'search-preview');
        element.style.backgroundColor = '';
        element.style.borderRadius = '';
        element.style.padding = '';
        element.style.margin = '';
    });
}

function showNoResultsMessage() {
    // Remove existing no-results message
    const existingMessage = document.querySelector('.no-results-message');
    if (existingMessage) {
        existingMessage.remove();
    }
    
    const message = document.createElement('div');
    message.className = 'no-results-message';
    message.innerHTML = `
        <div style="
            background: var(--bg-secondary);
            border: 1px solid var(--border-primary);
            border-radius: var(--radius-lg);
            padding: var(--space-xl);
            text-align: center;
            margin: var(--space-xl) 0;
        ">
            <h3 style="color: var(--white); margin-bottom: var(--space-md);">No results found</h3>
            <p style="color: var(--gray-300); margin-bottom: var(--space-lg);">
                We couldn't find any content matching your search. Try different keywords or browse our help topics above.
            </p>
            <div style="display: flex; gap: var(--space-md); justify-content: center; flex-wrap: wrap;">
                <a href="contact.html" class="btn btn--primary">Contact Support</a>
                <a href="docs.html" class="btn btn--secondary">Browse Documentation</a>
            </div>
        </div>
    `;
    
    const firstSection = document.querySelector('.support-section');
    if (firstSection) {
        firstSection.appendChild(message);
        message.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
    
    // Auto-remove after 10 seconds
    setTimeout(() => {
        if (message.parentNode) {
            message.remove();
        }
    }, 10000);
}

/**
 * Status Dashboard
 */
function initializeStatusDashboard() {
    updateSystemStatus();
    
    // Refresh status every 5 minutes
    setInterval(updateSystemStatus, 5 * 60 * 1000);
}

async function updateSystemStatus() {
    const statusItems = document.querySelectorAll('.status-item');
    
    // Simulate status checks (replace with real API calls)
    const statuses = await Promise.all([
        checkCoreFrameworkStatus(),
        checkDocumentationStatus(),
        checkGitHubStatus(),
        checkCommunityStatus()
    ]);
    
    statusItems.forEach((item, index) => {
        const indicator = item.querySelector('.status-indicator');
        const label = item.querySelector('.status-label');
        
        if (indicator && label && statuses[index]) {
            updateStatusIndicator(indicator, label, statuses[index]);
        }
    });
}

async function checkCoreFrameworkStatus() {
    // Simulate API check
    return new Promise(resolve => {
        setTimeout(() => {
            resolve({ status: 'operational', message: 'All systems operational' });
        }, 100);
    });
}

async function checkDocumentationStatus() {
    return new Promise(resolve => {
        setTimeout(() => {
            resolve({ status: 'operational', message: 'Documentation accessible' });
        }, 150);
    });
}

async function checkGitHubStatus() {
    return new Promise(resolve => {
        setTimeout(() => {
            resolve({ status: 'operational', message: 'Repository accessible' });
        }, 200);
    });
}

async function checkCommunityStatus() {
    return new Promise(resolve => {
        setTimeout(() => {
            resolve({ status: 'operational', message: 'Community forums active' });
        }, 250);
    });
}

function updateStatusIndicator(indicator, label, status) {
    // Remove existing status classes
    indicator.classList.remove('status-operational', 'status-degraded', 'status-outage');
    
    // Add new status class
    indicator.classList.add(`status-${status.status}`);
    
    // Update label text
    const statusTexts = {
        operational: 'Operational',
        degraded: 'Degraded Performance',
        outage: 'Service Outage'
    };
    
    label.textContent = statusTexts[status.status] || 'Unknown';
    
    // Update tooltip
    indicator.title = status.message;
}

/**
 * Support Action Tracking
 */
function initializeSupportTracking() {
    // Track help card clicks
    const helpCards = document.querySelectorAll('.help-card');
    helpCards.forEach(card => {
        card.addEventListener('click', function() {
            const title = this.querySelector('h3').textContent;
            trackSupportAction('help_card_click', { card_title: title });
        });
    });
    
    // Track support channel interactions
    const channelButtons = document.querySelectorAll('.support-channel .btn');
    channelButtons.forEach(button => {
        button.addEventListener('click', function() {
            const channel = this.closest('.support-channel').querySelector('h3').textContent;
            const action = this.textContent.trim();
            trackSupportAction('support_channel_click', { 
                channel: channel, 
                action: action 
            });
        });
    });
    
    // Track troubleshooting item views
    const troubleshootingItems = document.querySelectorAll('.troubleshooting-item');
    troubleshootingItems.forEach((item, index) => {
        // Use Intersection Observer to track when items come into view
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const title = entry.target.querySelector('h3').textContent;
                    trackSupportAction('troubleshooting_view', { 
                        item_title: title,
                        item_index: index 
                    });
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.5 });
        
        observer.observe(item);
    });
}

function trackSupportAction(action, data = {}) {
    // Log locally for development
    console.log('Support action:', action, data);
    
    // Send to analytics service (example)
    // if (typeof gtag !== 'undefined') {
    //     gtag('event', action, {
    //         event_category: 'Support',
    //         ...data
    //     });
    // }
    
    // Send to internal tracking API
    // fetch('/api/track', {
    //     method: 'POST',
    //     headers: { 'Content-Type': 'application/json' },
    //     body: JSON.stringify({ action, data, timestamp: Date.now() })
    // }).catch(console.error);
}

/**
 * Accessibility Enhancements
 */
function initializeAccessibilityEnhancements() {
    // Add keyboard navigation for status dashboard
    const statusItems = document.querySelectorAll('.status-item');
    statusItems.forEach(item => {
        item.setAttribute('tabindex', '0');
        item.setAttribute('role', 'button');
        item.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                // Show detailed status information
                showStatusDetails(this);
            }
        });
    });
    
    // Enhance error code accessibility
    const errorCodes = document.querySelectorAll('.error-code');
    errorCodes.forEach(code => {
        code.setAttribute('aria-label', `Error code ${code.textContent}`);
    });
    
    // Add skip links for long content sections
    addSkipLinks();
}

function showStatusDetails(statusItem) {
    const title = statusItem.querySelector('h3').textContent;
    const status = statusItem.querySelector('.status-label').textContent;
    const indicator = statusItem.querySelector('.status-indicator');
    
    // Create modal with detailed status information
    const modal = document.createElement('div');
    modal.className = 'status-detail-modal';
    modal.innerHTML = `
        <div class="modal-backdrop"></div>
        <div class="modal-content">
            <div class="modal-header">
                <h3>${title} Status</h3>
                <button class="modal-close" aria-label="Close status details">×</button>
            </div>
            <div class="modal-body">
                <div class="status-detail">
                    <div class="status-indicator ${indicator.className}" style="margin-right: 12px;"></div>
                    <div>
                        <strong>${status}</strong>
                        <p>Last checked: ${new Date().toLocaleTimeString()}</p>
                        <p>Response time: &lt; 100ms</p>
                        <p>Uptime: 99.9%</p>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Add modal styles
    const styles = `
        <style>
        .status-detail-modal {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            z-index: 10000;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: var(--space-lg);
        }
        .modal-backdrop {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(4px);
        }
        .modal-content {
            position: relative;
            background: var(--bg-secondary);
            border: 1px solid var(--border-primary);
            border-radius: var(--radius-lg);
            width: 90%;
            max-width: 500px;
            overflow: hidden;
        }
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: var(--space-lg);
            border-bottom: 1px solid var(--border-primary);
            background: var(--bg-primary);
        }
        .modal-header h3 {
            color: var(--white);
            margin: 0;
        }
        .modal-close {
            background: none;
            border: none;
            color: var(--gray-400);
            font-size: 1.5rem;
            cursor: pointer;
            padding: var(--space-xs);
        }
        .modal-body {
            padding: var(--space-lg);
        }
        .status-detail {
            display: flex;
            align-items: flex-start;
            gap: var(--space-md);
        }
        .status-detail strong {
            color: var(--white);
            display: block;
            margin-bottom: var(--space-sm);
        }
        .status-detail p {
            color: var(--gray-300);
            margin: 0 0 var(--space-xs) 0;
            font-size: 0.875rem;
        }
        </style>
    `;
    
    modal.insertAdjacentHTML('beforeend', styles);
    document.body.appendChild(modal);
    
    // Close modal functionality
    modal.addEventListener('click', function(e) {
        if (e.target === modal || e.target.classList.contains('modal-backdrop') || e.target.classList.contains('modal-close')) {
            document.body.removeChild(modal);
        }
    });
    
    // Focus management
    const closeButton = modal.querySelector('.modal-close');
    closeButton.focus();
    
    // Escape key to close
    function handleEscape(e) {
        if (e.key === 'Escape') {
            document.body.removeChild(modal);
            document.removeEventListener('keydown', handleEscape);
            statusItem.focus();
        }
    }
    
    document.addEventListener('keydown', handleEscape);
}

function addSkipLinks() {
    const skipLinks = document.createElement('div');
    skipLinks.className = 'skip-links';
    skipLinks.innerHTML = `
        <a href="#troubleshooting" class="skip-link">Skip to Troubleshooting</a>
        <a href="#error-codes" class="skip-link">Skip to Error Codes</a>
        <style>
        .skip-links {
            position: absolute;
            top: -100px;
            left: 0;
            z-index: 1000;
        }
        .skip-link {
            position: absolute;
            top: -100px;
            left: 0;
            background: var(--framework-purple);
            color: var(--white);
            padding: var(--space-sm) var(--space-md);
            text-decoration: none;
            border-radius: var(--radius-md);
            font-weight: 600;
            transition: top 0.3s ease;
        }
        .skip-link:focus {
            top: var(--space-md);
        }
        </style>
    `;
    
    document.body.insertBefore(skipLinks, document.body.firstChild);
}

/**
 * Utility Functions
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Auto-refresh Support Content
 */
function initializeContentRefresh() {
    // Check for updates every 30 minutes
    setInterval(async () => {
        try {
            // Check if there are new troubleshooting items or status updates
            // This would typically call an API to check for new content
            console.log('Checking for support content updates...');
            
            // If updates are found, show a notification
            // showUpdateNotification();
            
        } catch (error) {
            console.error('Error checking for updates:', error);
        }
    }, 30 * 60 * 1000);
}

function showUpdateNotification() {
    const notification = document.createElement('div');
    notification.className = 'update-notification';
    notification.innerHTML = `
        <div class="notification-content">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z"/>
            </svg>
            <span>New support content available. <a href="#" onclick="location.reload()">Refresh page</a></span>
            <button onclick="this.parentElement.parentElement.remove()">×</button>
        </div>
        <style>
        .update-notification {
            position: fixed;
            top: var(--space-lg);
            right: var(--space-lg);
            background: var(--framework-purple);
            color: var(--white);
            border-radius: var(--radius-lg);
            padding: var(--space-md);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            z-index: 1000;
            animation: slideIn 0.3s ease;
        }
        .notification-content {
            display: flex;
            align-items: center;
            gap: var(--space-sm);
        }
        .notification-content a {
            color: var(--white);
            text-decoration: underline;
        }
        .notification-content button {
            background: none;
            border: none;
            color: var(--white);
            cursor: pointer;
            padding: 0;
            margin-left: var(--space-sm);
        }
        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        </style>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 10 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 10000);
}

// Initialize content refresh
document.addEventListener('DOMContentLoaded', initializeContentRefresh);