/**
 * AI Triad Model - Landing Page JavaScript
 * Modern interactive elements and animations for 2025 design patterns
 */

// DOM Content Loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

/**
 * Initialize all application functionality
 */
function initializeApp() {
    initializeNavigation();
    initializeHero();
    initializeParticles();
    initializeAgentConnections();
    initializeScrollAnimations();
    initializeCodeTabs();
    initializeModal();
    initializeLoadingScreen();
    initializeSmoothScrolling();
    initializeThemeSystem();
}

/**
 * Navigation functionality
 */
function initializeNavigation() {
    const nav = document.getElementById('navigation');
    const navToggle = document.getElementById('navToggle');
    const navMenu = document.getElementById('navMenu');
    
    // Scroll detection for navigation styling
    let lastScrollY = window.scrollY;
    
    window.addEventListener('scroll', () => {
        const currentScrollY = window.scrollY;
        
        // Add scrolled class when scrolling down
        if (currentScrollY > 100) {
            nav.classList.add('scrolled');
        } else {
            nav.classList.remove('scrolled');
        }
        
        // Hide/show navigation on scroll
        if (currentScrollY > lastScrollY && currentScrollY > 200) {
            nav.style.transform = 'translateY(-100%)';
        } else {
            nav.style.transform = 'translateY(0)';
        }
        
        lastScrollY = currentScrollY;
    });
    
    // Mobile navigation toggle
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', () => {
            navToggle.classList.toggle('active');
            navMenu.classList.toggle('active');
            document.body.classList.toggle('nav-open');
        });
        
        // Close mobile nav when clicking on links
        const navLinks = navMenu.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                navToggle.classList.remove('active');
                navMenu.classList.remove('active');
                document.body.classList.remove('nav-open');
            });
        });
    }
}

/**
 * Hero section animations and interactions
 */
function initializeHero() {
    const heroStats = document.querySelectorAll('.hero-stat-number');
    
    // Animate stats when they come into view
    const animateStats = () => {
        heroStats.forEach(stat => {
            const targetText = stat.textContent;
            const isInfinite = targetText === '∞';
            const targetNumber = isInfinite ? 0 : parseInt(targetText.replace('%', ''));
            
            if (isInfinite) {
                // Special animation for infinity symbol
                stat.style.animation = 'infinite-pulse 2s ease-in-out infinite';
                return;
            }
            
            let current = 0;
            const increment = targetNumber / 60; // 60 frames animation
            const isPercentage = targetText.includes('%');
            
            const timer = setInterval(() => {
                current += increment;
                if (current >= targetNumber) {
                    current = targetNumber;
                    clearInterval(timer);
                }
                
                stat.textContent = Math.floor(current) + (isPercentage ? '%' : '');
            }, 16); // ~60fps
        });
    };
    
    // Trigger animation when hero section is visible
    const heroObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                setTimeout(animateStats, 1000); // Delay to match CSS animations
                heroObserver.unobserve(entry.target);
            }
        });
    });
    
    const heroSection = document.querySelector('.hero');
    if (heroSection) {
        heroObserver.observe(heroSection);
    }
}

/**
 * Particle system for hero background
 */
function initializeParticles() {
    const particlesContainer = document.getElementById('heroParticles');
    if (!particlesContainer) return;
    
    const particles = [];
    const particleCount = 50;
    
    // Create particles
    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.cssText = `
            position: absolute;
            width: 2px;
            height: 2px;
            background: rgba(139, 92, 246, 0.6);
            border-radius: 50%;
            pointer-events: none;
        `;
        
        particles.push({
            element: particle,
            x: Math.random() * window.innerWidth,
            y: Math.random() * window.innerHeight,
            vx: (Math.random() - 0.5) * 0.5,
            vy: (Math.random() - 0.5) * 0.5,
            opacity: Math.random() * 0.8 + 0.2
        });
        
        particlesContainer.appendChild(particle);
    }
    
    // Animate particles
    function animateParticles() {
        particles.forEach(particle => {
            particle.x += particle.vx;
            particle.y += particle.vy;
            
            // Wrap around screen
            if (particle.x < 0) particle.x = window.innerWidth;
            if (particle.x > window.innerWidth) particle.x = 0;
            if (particle.y < 0) particle.y = window.innerHeight;
            if (particle.y > window.innerHeight) particle.y = 0;
            
            // Update position
            particle.element.style.transform = `translate(${particle.x}px, ${particle.y}px)`;
            particle.element.style.opacity = particle.opacity;
        });
        
        requestAnimationFrame(animateParticles);
    }
    
    animateParticles();
    
    // Handle window resize
    window.addEventListener('resize', () => {
        particles.forEach(particle => {
            if (particle.x > window.innerWidth) particle.x = window.innerWidth;
            if (particle.y > window.innerHeight) particle.y = window.innerHeight;
        });
    });
}

/**
 * Agent connections visualization
 */
function initializeAgentConnections() {
    const connectionsContainer = document.getElementById('agentConnections');
    const agentCards = document.querySelectorAll('.agent-card');
    
    if (!connectionsContainer || !agentCards.length) return;
    
    const svg = connectionsContainer.querySelector('.connections-svg');
    if (!svg) return;
    
    // Create animated connections between agents
    const connections = [
        { from: 0, to: 1 },
        { from: 1, to: 2 },
        { from: 2, to: 3 },
        { from: 3, to: 0 }
    ];
    
    connections.forEach((_, index) => {
        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        path.setAttribute('stroke', '#8B5CF6');
        path.setAttribute('stroke-width', '2');
        path.setAttribute('fill', 'none');
        path.setAttribute('opacity', '0.6');
        path.style.animation = `connection-pulse 3s ease-in-out infinite ${index * 0.5}s`;
        
        // Simple connection path (would be calculated based on agent positions)
        const pathData = `M50,50 Q150,100 250,150`;
        path.setAttribute('d', pathData);
        
        svg.appendChild(path);
    });
    
    // Agent card hover effects
    agentCards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-8px) scale(1.02)';
            
            // Highlight connections from this agent
            const connections = svg.querySelectorAll('path');
            connections.forEach(path => {
                path.style.stroke = '#F59E0B';
                path.style.opacity = '1';
            });
        });
        
        card.addEventListener('mouseleave', () => {
            card.style.transform = '';
            
            // Reset connections
            const connections = svg.querySelectorAll('path');
            connections.forEach(path => {
                path.style.stroke = '#8B5CF6';
                path.style.opacity = '0.6';
            });
        });
    });
}

/**
 * Scroll-triggered animations
 */
function initializeScrollAnimations() {
    const animatedElements = document.querySelectorAll('.framework-card, .feature-item, .principle-card, .feature-card');
    
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animation = 'fadeInUp 0.6s ease-out forwards';
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    animatedElements.forEach(element => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(30px)';
        observer.observe(element);
    });
}

/**
 * Code tabs functionality
 */
function initializeCodeTabs() {
    const codeTabs = document.querySelectorAll('.code-tab');
    const codePanels = document.querySelectorAll('.code-panel');
    
    if (!codeTabs.length || !codePanels.length) return;
    
    codeTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const targetTab = tab.dataset.tab;
            
            // Remove active class from all tabs and panels
            codeTabs.forEach(t => t.classList.remove('code-tab--active'));
            codePanels.forEach(p => p.classList.remove('code-panel--active'));
            
            // Add active class to clicked tab and corresponding panel
            tab.classList.add('code-tab--active');
            const targetPanel = document.querySelector(`[data-panel="${targetTab}"]`);
            if (targetPanel) {
                targetPanel.classList.add('code-panel--active');
            }
        });
    });
    
    // Add syntax highlighting animation
    const codeBlocks = document.querySelectorAll('pre code');
    codeBlocks.forEach(block => {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    animateCodeTyping(entry.target);
                    observer.unobserve(entry.target);
                }
            });
        });
        
        observer.observe(block);
    });
}

/**
 * Animate code typing effect
 */
function animateCodeTyping(codeElement) {
    const originalText = codeElement.textContent;
    codeElement.textContent = '';
    
    let i = 0;
    const typeWriter = () => {
        if (i < originalText.length) {
            codeElement.textContent += originalText.charAt(i);
            i++;
            setTimeout(typeWriter, 10);
        }
    };
    
    // Small delay before starting animation
    setTimeout(typeWriter, 200);
}

/**
 * Modal functionality
 */
function initializeModal() {
    const modal = document.getElementById('demoModal');
    const modalTriggers = document.querySelectorAll('[data-modal="demo"]');
    const modalClose = document.querySelector('.modal-close');
    const modalBackdrop = document.querySelector('.modal-backdrop');
    
    if (!modal) return;
    
    // Open modal
    modalTriggers.forEach(trigger => {
        trigger.addEventListener('click', () => {
            modal.classList.add('active');
            document.body.style.overflow = 'hidden';
            
            // Start demo simulation
            setTimeout(() => {
                simulateDemoAgentResponses();
            }, 500);
        });
    });
    
    // Close modal
    const closeModal = () => {
        modal.classList.remove('active');
        document.body.style.overflow = '';
        resetDemoInterface();
    };
    
    modalClose?.addEventListener('click', closeModal);
    modalBackdrop?.addEventListener('click', closeModal);
    
    // Close on escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modal.classList.contains('active')) {
            closeModal();
        }
    });
}

/**
 * Simulate demo agent responses
 */
function simulateDemoAgentResponses() {
    const agentResponses = document.querySelectorAll('.agent-response');
    const responses = [
        { agent: 'legislative', response: 'Planning phase complete. Policy framework established for optimal resource allocation.', delay: 1000 },
        { agent: 'executive', response: 'Implementation approved. Executing planned operations with constitutional oversight.', delay: 2500 },
        { agent: 'judicial', response: 'Constitutional review passed. All operations comply with framework principles.', delay: 4000 },
        { agent: 'crown', response: 'Final oversight complete. System integrity maintained. Request approved.', delay: 5500 }
    ];
    
    responses.forEach(({ agent, response, delay }) => {
        setTimeout(() => {
            const agentElement = document.querySelector(`[data-agent="${agent}"] .response-content`);
            if (agentElement) {
                agentElement.textContent = response;
                agentElement.parentElement.style.borderColor = '#10B981';
            }
        }, delay);
    });
}

/**
 * Reset demo interface
 */
function resetDemoInterface() {
    const responses = ['Processing...', 'Waiting...', 'Waiting...', 'Waiting...'];
    const agentResponses = document.querySelectorAll('.agent-response');
    
    agentResponses.forEach((response, index) => {
        const content = response.querySelector('.response-content');
        if (content) {
            content.textContent = responses[index];
            response.style.borderColor = '';
        }
    });
    
    const demoInput = document.getElementById('demoRequest');
    if (demoInput) {
        demoInput.value = '';
    }
}

/**
 * Loading screen functionality
 */
function initializeLoadingScreen() {
    const loadingOverlay = document.getElementById('loadingOverlay');
    
    if (!loadingOverlay) return;
    
    // Hide loading screen after page load
    window.addEventListener('load', () => {
        setTimeout(() => {
            loadingOverlay.classList.add('hidden');
            
            // Remove from DOM after transition
            setTimeout(() => {
                loadingOverlay.remove();
            }, 300);
        }, 1000);
    });
}

/**
 * Smooth scrolling for navigation links
 */
function initializeSmoothScrolling() {
    const scrollTriggers = document.querySelectorAll('[data-scroll-to]');
    
    scrollTriggers.forEach(trigger => {
        trigger.addEventListener('click', (e) => {
            e.preventDefault();
            
            const targetId = trigger.dataset.scrollTo;
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                const offsetTop = targetElement.offsetTop - 80; // Account for fixed navigation
                
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Also handle regular anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            const href = link.getAttribute('href');
            if (href === '#' || href === '#home') return;
            
            e.preventDefault();
            
            const targetElement = document.querySelector(href);
            if (targetElement) {
                const offsetTop = targetElement.offsetTop - 80;
                
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }
        });
    });
}

/**
 * Theme system for potential dark/light mode toggle
 */
function initializeThemeSystem() {
    // Set initial theme (currently always dark for the landing page)
    document.documentElement.setAttribute('data-theme', 'dark');
    
    // Listen for system theme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
        // Could implement theme switching here if needed
    });
}

/**
 * Performance optimizations
 */
function optimizePerformance() {
    // Lazy load images when they come into view
    const lazyImages = document.querySelectorAll('img[data-src]');
    
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        lazyImages.forEach(img => imageObserver.observe(img));
    } else {
        // Fallback for older browsers
        lazyImages.forEach(img => {
            img.src = img.dataset.src;
        });
    }
}

/**
 * Accessibility enhancements
 */
function enhanceAccessibility() {
    // Add skip link for keyboard navigation
    const skipLink = document.createElement('a');
    skipLink.href = '#main-content';
    skipLink.textContent = 'Skip to main content';
    skipLink.className = 'skip-link';
    skipLink.style.cssText = `
        position: absolute;
        top: -40px;
        left: 6px;
        z-index: 1000;
        background: var(--constitutional-purple);
        color: white;
        padding: 8px;
        text-decoration: none;
        border-radius: 4px;
        transition: top 0.3s;
    `;
    
    skipLink.addEventListener('focus', () => {
        skipLink.style.top = '6px';
    });
    
    skipLink.addEventListener('blur', () => {
        skipLink.style.top = '-40px';
    });
    
    document.body.prepend(skipLink);
    
    // Add main content landmark
    const heroSection = document.querySelector('.hero');
    if (heroSection) {
        heroSection.id = 'main-content';
        heroSection.setAttribute('tabindex', '-1');
    }
    
    // Improve focus management for modal
    const modal = document.getElementById('demoModal');
    if (modal) {
        modal.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                trapFocus(e, modal);
            }
        });
    }
}

/**
 * Trap focus within modal
 */
function trapFocus(e, container) {
    const focusableElements = container.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    
    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];
    
    if (e.shiftKey) {
        if (document.activeElement === firstElement) {
            lastElement.focus();
            e.preventDefault();
        }
    } else {
        if (document.activeElement === lastElement) {
            firstElement.focus();
            e.preventDefault();
        }
    }
}

/**
 * Error handling
 */
window.addEventListener('error', (e) => {
    console.error('JavaScript error:', e.error);
    // Could send error reports to analytics service
});

// Add CSS animations that couldn't be included in CSS file
const additionalStyles = `
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes infinite-pulse {
        0%, 100% {
            transform: scale(1);
            opacity: 1;
        }
        50% {
            transform: scale(1.1);
            opacity: 0.8;
        }
    }
    
    @keyframes connection-pulse {
        0%, 100% {
            stroke-dasharray: 0, 100;
        }
        50% {
            stroke-dasharray: 50, 50;
        }
    }
    
    .skip-link:focus {
        top: 6px !important;
    }
`;

// Inject additional styles
const styleSheet = document.createElement('style');
styleSheet.textContent = additionalStyles;
document.head.appendChild(styleSheet);

// Initialize performance optimizations and accessibility
document.addEventListener('DOMContentLoaded', () => {
    optimizePerformance();
    enhanceAccessibility();
});