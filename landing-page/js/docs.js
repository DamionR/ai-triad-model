/**
 * Documentation Page JavaScript
 * Handles navigation, code copying, and interactive features
 */

// Wait for DOM to be ready
document.addEventListener('DOMContentLoaded', function() {
    initializeDocumentation();
});

function initializeDocumentation() {
    initializeSidebarNavigation();
    initializeCodeCopying();
    initializeScrollSpy();
    initializeSearch();
}

/**
 * Sidebar Navigation
 */
function initializeSidebarNavigation() {
    const navLinks = document.querySelectorAll('.docs-nav-link');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all links
            navLinks.forEach(l => l.classList.remove('active'));
            
            // Add active class to clicked link
            this.classList.add('active');
            
            // Smooth scroll to section
            const targetId = this.getAttribute('href').substring(1);
            const targetSection = document.getElementById(targetId);
            
            if (targetSection) {
                const navHeight = document.querySelector('.nav').offsetHeight;
                const offsetTop = targetSection.offsetTop - navHeight - 32;
                
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }
        });
    });
}

/**
 * Code Copying Functionality
 */
function initializeCodeCopying() {
    const copyButtons = document.querySelectorAll('.docs-code-copy');
    
    copyButtons.forEach(button => {
        button.addEventListener('click', async function() {
            const targetId = this.getAttribute('data-copy-target');
            const codeElement = document.querySelector(targetId);
            
            if (codeElement) {
                try {
                    const codeText = codeElement.textContent;
                    await navigator.clipboard.writeText(codeText);
                    
                    // Visual feedback
                    const originalText = this.textContent;
                    this.textContent = 'Copied!';
                    this.style.background = '#10B981';
                    
                    setTimeout(() => {
                        this.textContent = originalText;
                        this.style.background = '';
                    }, 2000);
                    
                } catch (err) {
                    console.error('Failed to copy code:', err);
                    
                    // Fallback for older browsers
                    const textArea = document.createElement('textarea');
                    textArea.value = codeElement.textContent;
                    document.body.appendChild(textArea);
                    textArea.select();
                    document.execCommand('copy');
                    document.body.removeChild(textArea);
                    
                    // Visual feedback
                    const originalText = this.textContent;
                    this.textContent = 'Copied!';
                    this.style.background = '#10B981';
                    
                    setTimeout(() => {
                        this.textContent = originalText;
                        this.style.background = '';
                    }, 2000);
                }
            }
        });
    });
}

/**
 * Scroll Spy for Navigation
 */
function initializeScrollSpy() {
    const sections = document.querySelectorAll('.docs-section');
    const navLinks = document.querySelectorAll('.docs-nav-link');
    const navHeight = document.querySelector('.nav').offsetHeight;
    
    function updateActiveNavLink() {
        let activeSection = null;
        const scrollPosition = window.scrollY + navHeight + 100;
        
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionBottom = sectionTop + section.offsetHeight;
            
            if (scrollPosition >= sectionTop && scrollPosition < sectionBottom) {
                activeSection = section;
            }
        });
        
        if (activeSection) {
            const activeId = activeSection.getAttribute('id');
            
            navLinks.forEach(link => {
                link.classList.remove('active');
                if (link.getAttribute('href') === `#${activeId}`) {
                    link.classList.add('active');
                }
            });
        }
    }
    
    // Throttle scroll events for performance
    let ticking = false;
    
    window.addEventListener('scroll', function() {
        if (!ticking) {
            requestAnimationFrame(function() {
                updateActiveNavLink();
                ticking = false;
            });
            ticking = true;
        }
    });
    
    // Initial check
    updateActiveNavLink();
}

/**
 * Search Functionality
 */
function initializeSearch() {
    const searchButton = document.querySelector('.nav-actions .btn--secondary');
    
    if (searchButton && searchButton.textContent.includes('Search')) {
        searchButton.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Create search modal
            const modal = createSearchModal();
            document.body.appendChild(modal);
            
            // Focus on search input
            const searchInput = modal.querySelector('.search-input');
            searchInput.focus();
            
            // Close modal on escape or backdrop click
            modal.addEventListener('click', function(e) {
                if (e.target === modal || e.target.classList.contains('search-close')) {
                    document.body.removeChild(modal);
                }
            });
            
            document.addEventListener('keydown', function handleEscape(e) {
                if (e.key === 'Escape') {
                    if (document.body.contains(modal)) {
                        document.body.removeChild(modal);
                    }
                    document.removeEventListener('keydown', handleEscape);
                }
            });
        });
    }
}

/**
 * Create Search Modal
 */
function createSearchModal() {
    const modal = document.createElement('div');
    modal.className = 'search-modal';
    modal.innerHTML = `
        <div class="search-modal-backdrop"></div>
        <div class="search-modal-content">
            <div class="search-modal-header">
                <h3>Search Documentation</h3>
                <button class="search-close">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                </button>
            </div>
            <div class="search-modal-body">
                <input type="text" class="search-input" placeholder="Search for topics, code examples, or concepts...">
                <div class="search-results">
                    <div class="search-results-empty">
                        <p>Start typing to search through the documentation...</p>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Add search functionality
    const searchInput = modal.querySelector('.search-input');
    const searchResults = modal.querySelector('.search-results');
    
    searchInput.addEventListener('input', function() {
        const query = this.value.toLowerCase().trim();
        
        if (query.length < 2) {
            searchResults.innerHTML = `
                <div class="search-results-empty">
                    <p>Start typing to search through the documentation...</p>
                </div>
            `;
            return;
        }
        
        // Simple search through page content
        const results = performSearch(query);
        displaySearchResults(results, searchResults);
    });
    
    // Add modal styles
    const styles = `
        <style>
        .search-modal {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            z-index: 10000;
            display: flex;
            align-items: flex-start;
            justify-content: center;
            padding-top: 10vh;
        }
        
        .search-modal-backdrop {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(4px);
        }
        
        .search-modal-content {
            position: relative;
            background: var(--bg-secondary);
            border: 1px solid var(--border-primary);
            border-radius: var(--radius-lg);
            width: 90%;
            max-width: 600px;
            max-height: 70vh;
            overflow: hidden;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
        }
        
        .search-modal-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: var(--space-lg);
            border-bottom: 1px solid var(--border-primary);
        }
        
        .search-modal-header h3 {
            color: var(--white);
            margin: 0;
            font-size: 1.25rem;
        }
        
        .search-close {
            background: none;
            border: none;
            color: var(--gray-400);
            cursor: pointer;
            padding: var(--space-xs);
            border-radius: var(--radius-sm);
            transition: all 0.2s ease;
        }
        
        .search-close:hover {
            color: var(--framework-purple-light);
            background: var(--bg-tertiary);
        }
        
        .search-modal-body {
            padding: var(--space-lg);
        }
        
        .search-input {
            width: 100%;
            background: var(--bg-primary);
            border: 1px solid var(--border-primary);
            border-radius: var(--radius-lg);
            padding: var(--space-md) var(--space-lg);
            color: var(--white);
            font-size: 1rem;
            margin-bottom: var(--space-lg);
        }
        
        .search-input:focus {
            outline: none;
            border-color: var(--framework-purple);
            box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1);
        }
        
        .search-results {
            max-height: 400px;
            overflow-y: auto;
        }
        
        .search-results-empty {
            text-align: center;
            padding: var(--space-xl);
            color: var(--gray-400);
        }
        
        .search-result-item {
            padding: var(--space-md);
            border-radius: var(--radius-md);
            margin-bottom: var(--space-sm);
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .search-result-item:hover {
            background: var(--bg-tertiary);
        }
        
        .search-result-title {
            color: var(--framework-purple-light);
            font-weight: 500;
            margin-bottom: var(--space-xs);
        }
        
        .search-result-snippet {
            color: var(--gray-300);
            font-size: 0.875rem;
            line-height: 1.5;
        }
        </style>
    `;
    
    modal.insertAdjacentHTML('beforeend', styles);
    
    return modal;
}

/**
 * Perform Search
 */
function performSearch(query) {
    const sections = document.querySelectorAll('.docs-section');
    const results = [];
    
    sections.forEach(section => {
        const sectionId = section.getAttribute('id');
        const title = section.querySelector('h2')?.textContent || '';
        const content = section.textContent.toLowerCase();
        
        if (content.includes(query)) {
            // Find snippet around the match
            const index = content.indexOf(query);
            const start = Math.max(0, index - 50);
            const end = Math.min(content.length, index + query.length + 50);
            const snippet = content.substring(start, end).trim();
            
            results.push({
                id: sectionId,
                title: title,
                snippet: '...' + snippet + '...',
                relevance: calculateRelevance(query, title, content)
            });
        }
    });
    
    // Sort by relevance
    return results.sort((a, b) => b.relevance - a.relevance).slice(0, 10);
}

/**
 * Calculate Search Relevance
 */
function calculateRelevance(query, title, content) {
    let score = 0;
    const titleLower = title.toLowerCase();
    
    // Title matches are more important
    if (titleLower.includes(query)) {
        score += 10;
    }
    
    // Count occurrences in content
    const matches = (content.match(new RegExp(query, 'g')) || []).length;
    score += matches;
    
    return score;
}

/**
 * Display Search Results
 */
function displaySearchResults(results, container) {
    if (results.length === 0) {
        container.innerHTML = `
            <div class="search-results-empty">
                <p>No results found. Try different keywords.</p>
            </div>
        `;
        return;
    }
    
    const resultsHTML = results.map(result => `
        <div class="search-result-item" data-section="${result.id}">
            <div class="search-result-title">${result.title}</div>
            <div class="search-result-snippet">${result.snippet}</div>
        </div>
    `).join('');
    
    container.innerHTML = resultsHTML;
    
    // Add click handlers
    container.querySelectorAll('.search-result-item').forEach(item => {
        item.addEventListener('click', function() {
            const sectionId = this.getAttribute('data-section');
            const section = document.getElementById(sectionId);
            
            if (section) {
                // Close modal
                const modal = document.querySelector('.search-modal');
                if (modal) {
                    document.body.removeChild(modal);
                }
                
                // Navigate to section
                const navHeight = document.querySelector('.nav').offsetHeight;
                const offsetTop = section.offsetTop - navHeight - 32;
                
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
                
                // Update active nav link
                const navLinks = document.querySelectorAll('.docs-nav-link');
                navLinks.forEach(link => {
                    link.classList.remove('active');
                    if (link.getAttribute('href') === `#${sectionId}`) {
                        link.classList.add('active');
                    }
                });
            }
        });
    });
}