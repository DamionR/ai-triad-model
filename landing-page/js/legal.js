/**
 * Legal Pages JavaScript
 * Handles table of contents navigation, scroll tracking, and legal page interactions
 */

// Wait for DOM to be ready
document.addEventListener('DOMContentLoaded', function() {
    initializeLegalPage();
});

function initializeLegalPage() {
    initializeTableOfContents();
    initializeScrollTracking();
    initializeLegalInteractions();
    initializeAccessibilityEnhancements();
}

/**
 * Table of Contents Navigation
 */
function initializeTableOfContents() {
    const tocLinks = document.querySelectorAll('.toc-link');
    const sections = document.querySelectorAll('.legal-section[id]');
    
    if (tocLinks.length === 0 || sections.length === 0) {
        return;
    }
    
    // Handle TOC link clicks
    tocLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href').substring(1);
            const targetSection = document.getElementById(targetId);
            
            if (targetSection) {
                // Smooth scroll to section
                targetSection.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
                
                // Update active link
                updateActiveTocLink(this);
                
                // Track navigation
                trackLegalAction('toc_navigation', { section: targetId });
            }
        });
    });
    
    // Handle keyboard navigation
    tocLinks.forEach((link, index) => {
        link.addEventListener('keydown', function(e) {
            let targetIndex = -1;
            
            switch (e.key) {
                case 'ArrowDown':
                    e.preventDefault();
                    targetIndex = Math.min(index + 1, tocLinks.length - 1);
                    break;
                case 'ArrowUp':
                    e.preventDefault();
                    targetIndex = Math.max(index - 1, 0);
                    break;
                case 'Home':
                    e.preventDefault();
                    targetIndex = 0;
                    break;
                case 'End':
                    e.preventDefault();
                    targetIndex = tocLinks.length - 1;
                    break;
            }
            
            if (targetIndex >= 0) {
                tocLinks[targetIndex].focus();
            }
        });
    });
}

function updateActiveTocLink(activeLink) {
    // Remove active class from all links
    document.querySelectorAll('.toc-link').forEach(link => {
        link.classList.remove('active');
    });
    
    // Add active class to clicked link
    activeLink.classList.add('active');
}

/**
 * Scroll Tracking and TOC Highlighting
 */
function initializeScrollTracking() {
    const sections = document.querySelectorAll('.legal-section[id]');
    const tocLinks = document.querySelectorAll('.toc-link');
    
    if (sections.length === 0 || tocLinks.length === 0) {
        return;
    }
    
    // Create intersection observer for section visibility
    const observerOptions = {
        rootMargin: '-20% 0px -70% 0px',
        threshold: 0
    };
    
    const sectionObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const sectionId = entry.target.id;
                const correspondingTocLink = document.querySelector(`.toc-link[href="#${sectionId}"]`);
                
                if (correspondingTocLink) {
                    updateActiveTocLink(correspondingTocLink);
                }
                
                // Track section view
                trackLegalAction('section_view', { 
                    section: sectionId,
                    title: entry.target.querySelector('h2')?.textContent || sectionId
                });
            }
        });
    }, observerOptions);
    
    // Observe all sections
    sections.forEach(section => {
        sectionObserver.observe(section);
    });
    
    // Track scroll depth
    let maxScrollDepth = 0;
    let scrollDepthReported = new Set();
    
    window.addEventListener('scroll', debounce(() => {
        const scrollTop = window.pageYOffset;
        const docHeight = document.documentElement.scrollHeight - window.innerHeight;
        const scrollPercent = Math.round((scrollTop / docHeight) * 100);
        
        maxScrollDepth = Math.max(maxScrollDepth, scrollPercent);
        
        // Report scroll depth milestones
        const milestones = [25, 50, 75, 90, 100];
        milestones.forEach(milestone => {
            if (scrollPercent >= milestone && !scrollDepthReported.has(milestone)) {
                scrollDepthReported.add(milestone);
                trackLegalAction('scroll_depth', { 
                    depth: milestone,
                    page: document.title
                });
            }
        });
    }, 250));
}

/**
 * Legal Page Interactions
 */
function initializeLegalInteractions() {
    // Track email clicks
    const emailLinks = document.querySelectorAll('a[href^="mailto:"]');
    emailLinks.forEach(link => {
        link.addEventListener('click', function() {
            const email = this.href.replace('mailto:', '');
            trackLegalAction('email_click', { email: email });
        });
    });
    
    // Track external link clicks
    const externalLinks = document.querySelectorAll('a[href^="http"], a[target="_blank"]');
    externalLinks.forEach(link => {
        link.addEventListener('click', function() {
            trackLegalAction('external_link_click', { 
                url: this.href,
                text: this.textContent.trim()
            });
        });
    });
    
    // Track print attempts
    window.addEventListener('beforeprint', function() {
        trackLegalAction('print_attempt', { page: document.title });
    });
    
    // Track copy attempts
    document.addEventListener('copy', function() {
        const selection = window.getSelection().toString();
        if (selection.length > 10) {
            trackLegalAction('text_copy', { 
                length: selection.length,
                sample: selection.substring(0, 50) + (selection.length > 50 ? '...' : '')
            });
        }
    });
    
    // Initialize rights request functionality
    initializeRightsRequest();
}

function initializeRightsRequest() {
    const rightsButton = document.querySelector('.rights-request-card .btn');
    
    if (rightsButton) {
        rightsButton.addEventListener('click', function(e) {
            // Check if this is a contact form link
            if (this.href && this.href.includes('contact.html')) {
                // Pre-populate subject if supported
                const url = new URL(this.href, window.location.origin);
                if (!url.searchParams.has('subject')) {
                    url.searchParams.set('subject', 'data-rights');
                    this.href = url.toString();
                }
            }
            
            trackLegalAction('rights_request', { 
                type: 'button_click',
                page: document.title
            });
        });
    }
}

/**
 * Accessibility Enhancements
 */
function initializeAccessibilityEnhancements() {
    // Add skip links for long legal content
    addSkipToContentLink();
    
    // Enhance heading navigation
    enhanceHeadingNavigation();
    
    // Add reading time estimate
    addReadingTimeEstimate();
    
    // Add language toggle if needed
    initializeLanguageSupport();
}

function addSkipToContentLink() {
    const skipLink = document.createElement('a');
    skipLink.href = '#legal-content';
    skipLink.className = 'skip-to-content';
    skipLink.textContent = 'Skip to main content';
    skipLink.style.cssText = `
        position: absolute;
        top: -100px;
        left: 10px;
        background: var(--framework-purple);
        color: white;
        padding: 8px 16px;
        text-decoration: none;
        border-radius: 4px;
        z-index: 1000;
        font-weight: 600;
        transition: top 0.3s ease;
    `;
    
    skipLink.addEventListener('focus', function() {
        this.style.top = '10px';
    });
    
    skipLink.addEventListener('blur', function() {
        this.style.top = '-100px';
    });
    
    document.body.insertBefore(skipLink, document.body.firstChild);
    
    // Add ID to legal content for skip link target
    const legalContent = document.querySelector('.legal-content');
    if (legalContent && !legalContent.id) {
        legalContent.id = 'legal-content';
    }
}

function enhanceHeadingNavigation() {
    const headings = document.querySelectorAll('.legal-section h2, .legal-section h3');
    
    headings.forEach(heading => {
        // Add tabindex for keyboard navigation
        heading.setAttribute('tabindex', '0');
        
        // Add anchor links
        if (heading.parentElement.id) {
            const anchorLink = document.createElement('a');
            anchorLink.href = `#${heading.parentElement.id}`;
            anchorLink.className = 'heading-anchor';
            anchorLink.innerHTML = '🔗';
            anchorLink.style.cssText = `
                opacity: 0;
                margin-left: 0.5rem;
                text-decoration: none;
                font-size: 0.8em;
                transition: opacity 0.2s ease;
            `;
            
            heading.appendChild(anchorLink);
            
            heading.addEventListener('mouseenter', () => {
                anchorLink.style.opacity = '0.6';
            });
            
            heading.addEventListener('mouseleave', () => {
                anchorLink.style.opacity = '0';
            });
            
            anchorLink.addEventListener('click', (e) => {
                e.preventDefault();
                navigator.clipboard.writeText(window.location.origin + window.location.pathname + anchorLink.href);
                
                // Show feedback
                anchorLink.innerHTML = '✓';
                setTimeout(() => {
                    anchorLink.innerHTML = '🔗';
                }, 1000);
            });
        }
    });
}

function addReadingTimeEstimate() {
    const content = document.querySelector('.legal-content');
    if (!content) return;
    
    const text = content.textContent;
    const wordCount = text.split(/\s+/).length;
    const readingTime = Math.ceil(wordCount / 200); // Average reading speed: 200 words per minute
    
    const estimate = document.createElement('div');
    estimate.className = 'reading-time-estimate';
    estimate.innerHTML = `
        <div style="
            background: var(--bg-secondary);
            border: 1px solid var(--border-primary);
            border-radius: var(--radius-md);
            padding: var(--space-md);
            margin-bottom: var(--space-xl);
            display: flex;
            align-items: center;
            gap: var(--space-sm);
            color: var(--gray-300);
            font-size: 0.875rem;
        ">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <polyline points="12,6 12,12 16,14"></polyline>
            </svg>
            <span>Estimated reading time: ${readingTime} minute${readingTime !== 1 ? 's' : ''}</span>
        </div>
    `;
    
    const legalContent = document.querySelector('.legal-content');
    if (legalContent) {
        legalContent.insertBefore(estimate, legalContent.firstChild);
    }
}

function initializeLanguageSupport() {
    // Add language selector if multiple languages are supported
    const currentLang = document.documentElement.lang || 'en';
    
    // This would be expanded if multiple languages are supported
    if (currentLang !== 'en') {
        const langNotice = document.createElement('div');
        langNotice.className = 'language-notice';
        langNotice.innerHTML = `
            <div style="
                background: rgba(245, 158, 11, 0.1);
                border: 1px solid rgba(245, 158, 11, 0.2);
                border-radius: var(--radius-md);
                padding: var(--space-md);
                margin-bottom: var(--space-xl);
                color: var(--system-gold);
                font-size: 0.875rem;
                text-align: center;
            ">
                This document is available in English. 
                <a href="?lang=en" style="color: var(--framework-purple-light); text-decoration: underline;">
                    Switch to English
                </a>
            </div>
        `;
        
        const legalContent = document.querySelector('.legal-content');
        if (legalContent) {
            legalContent.insertBefore(langNotice, legalContent.firstChild);
        }
    }
}

/**
 * Analytics and Tracking
 */
function trackLegalAction(action, data = {}) {
    // Log locally for development
    console.log('Legal page action:', action, data);
    
    // Send to analytics service
    if (typeof gtag !== 'undefined') {
        gtag('event', action, {
            event_category: 'Legal Pages',
            page_title: document.title,
            page_location: window.location.href,
            ...data
        });
    }
    
    // Send to internal tracking if available
    if (window.trackEvent) {
        window.trackEvent('legal', action, data);
    }
}

/**
 * Search Functionality (for long legal documents)
 */
function initializeLegalSearch() {
    const searchContainer = document.createElement('div');
    searchContainer.className = 'legal-search';
    searchContainer.innerHTML = `
        <div style="
            background: var(--bg-secondary);
            border: 1px solid var(--border-primary);
            border-radius: var(--radius-lg);
            padding: var(--space-md);
            margin-bottom: var(--space-xl);
            display: flex;
            align-items: center;
            gap: var(--space-sm);
        ">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="11" cy="11" r="8"></circle>
                <path d="M21 21L16.65 16.65"></path>
            </svg>
            <input 
                type="text" 
                placeholder="Search this document..." 
                id="legalSearch"
                style="
                    flex: 1;
                    background: none;
                    border: none;
                    color: var(--white);
                    font-size: 0.875rem;
                    outline: none;
                "
            >
            <button id="clearSearch" style="
                background: none;
                border: none;
                color: var(--gray-400);
                cursor: pointer;
                display: none;
            ">×</button>
        </div>
    `;
    
    const toc = document.querySelector('.legal-toc');
    if (toc) {
        toc.parentNode.insertBefore(searchContainer, toc);
        
        const searchInput = document.getElementById('legalSearch');
        const clearButton = document.getElementById('clearSearch');
        
        searchInput.addEventListener('input', debounce(performLegalSearch, 300));
        clearButton.addEventListener('click', clearLegalSearch);
    }
}

function performLegalSearch(e) {
    const query = e.target.value.trim().toLowerCase();
    const clearButton = document.getElementById('clearSearch');
    
    if (query.length === 0) {
        clearLegalSearch();
        return;
    }
    
    clearButton.style.display = 'block';
    
    // Remove existing highlights
    clearSearchHighlights();
    
    if (query.length < 2) return;
    
    // Find and highlight matches
    const textNodes = getTextNodes(document.querySelector('.legal-content'));
    let matchCount = 0;
    
    textNodes.forEach(node => {
        const text = node.textContent.toLowerCase();
        if (text.includes(query)) {
            highlightTextInNode(node, query);
            matchCount++;
        }
    });
    
    // Show search results
    showSearchResults(matchCount);
    
    // Track search
    trackLegalAction('document_search', { 
        query: query, 
        results: matchCount 
    });
}

function clearLegalSearch() {
    const searchInput = document.getElementById('legalSearch');
    const clearButton = document.getElementById('clearSearch');
    
    if (searchInput) searchInput.value = '';
    if (clearButton) clearButton.style.display = 'none';
    
    clearSearchHighlights();
    hideSearchResults();
}

function clearSearchHighlights() {
    const highlights = document.querySelectorAll('.search-highlight');
    highlights.forEach(highlight => {
        const parent = highlight.parentNode;
        parent.replaceChild(document.createTextNode(highlight.textContent), highlight);
        parent.normalize();
    });
}

function getTextNodes(element) {
    const textNodes = [];
    const walker = document.createTreeWalker(
        element,
        NodeFilter.SHOW_TEXT,
        {
            acceptNode: function(node) {
                // Skip text nodes in script and style elements
                const parent = node.parentElement;
                if (parent && (parent.tagName === 'SCRIPT' || parent.tagName === 'STYLE')) {
                    return NodeFilter.FILTER_REJECT;
                }
                // Only include text nodes with meaningful content
                return node.textContent.trim().length > 0 ? 
                    NodeFilter.FILTER_ACCEPT : 
                    NodeFilter.FILTER_REJECT;
            }
        }
    );
    
    let node;
    while (node = walker.nextNode()) {
        textNodes.push(node);
    }
    
    return textNodes;
}

function highlightTextInNode(textNode, query) {
    const text = textNode.textContent;
    const regex = new RegExp(`(${escapeRegExp(query)})`, 'gi');
    
    if (regex.test(text)) {
        const highlightedHTML = text.replace(regex, '<mark class="search-highlight" style="background: rgba(245, 158, 11, 0.3); color: var(--system-gold); padding: 2px 4px; border-radius: 2px;">$1</mark>');
        
        const wrapper = document.createElement('span');
        wrapper.innerHTML = highlightedHTML;
        
        textNode.parentNode.replaceChild(wrapper, textNode);
    }
}

function showSearchResults(count) {
    let resultsDiv = document.getElementById('searchResults');
    
    if (!resultsDiv) {
        resultsDiv = document.createElement('div');
        resultsDiv.id = 'searchResults';
        resultsDiv.style.cssText = `
            background: var(--bg-tertiary);
            border: 1px solid var(--border-primary);
            border-radius: var(--radius-md);
            padding: var(--space-sm);
            margin-bottom: var(--space-md);
            color: var(--gray-300);
            font-size: 0.875rem;
            text-align: center;
        `;
        
        const searchContainer = document.querySelector('.legal-search');
        if (searchContainer) {
            searchContainer.appendChild(resultsDiv);
        }
    }
    
    resultsDiv.textContent = `${count} result${count !== 1 ? 's' : ''} found`;
    resultsDiv.style.display = 'block';
}

function hideSearchResults() {
    const resultsDiv = document.getElementById('searchResults');
    if (resultsDiv) {
        resultsDiv.style.display = 'none';
    }
}

function escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
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

// Initialize search for long documents
document.addEventListener('DOMContentLoaded', function() {
    // Only add search for documents longer than 3000 words
    const content = document.querySelector('.legal-content');
    if (content && content.textContent.split(/\s+/).length > 3000) {
        initializeLegalSearch();
    }
});