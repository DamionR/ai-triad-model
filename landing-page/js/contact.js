/**
 * Contact Page JavaScript
 * Handles form submission, FAQ interactions, and contact functionality
 */

// Wait for DOM to be ready
document.addEventListener('DOMContentLoaded', function() {
    initializeContactPage();
});

function initializeContactPage() {
    initializeContactForm();
    initializeFAQ();
    initializeFormValidation();
}

/**
 * Contact Form Handling
 */
function initializeContactForm() {
    const form = document.getElementById('contactForm');
    const successDiv = document.getElementById('formSuccess');
    
    if (form) {
        form.addEventListener('submit', handleFormSubmission);
    }
}

async function handleFormSubmission(e) {
    e.preventDefault();
    
    const form = e.target;
    const submitButton = form.querySelector('.form-submit');
    const formData = new FormData(form);
    
    // Show loading state
    submitButton.classList.add('loading');
    submitButton.disabled = true;
    form.classList.add('form-loading');
    
    try {
        // Simulate form submission (replace with actual endpoint)
        await simulateFormSubmission(formData);
        
        // Show success state
        showFormSuccess();
        
    } catch (error) {
        console.error('Form submission error:', error);
        showFormError();
        
    } finally {
        // Reset loading state
        submitButton.classList.remove('loading');
        submitButton.disabled = false;
        form.classList.remove('form-loading');
    }
}

function simulateFormSubmission(formData) {
    return new Promise((resolve) => {
        // Simulate API call delay
        setTimeout(() => {
            console.log('Form data submitted:', Object.fromEntries(formData));
            resolve();
        }, 2000);
    });
}

function showFormSuccess() {
    const form = document.getElementById('contactForm');
    const successDiv = document.getElementById('formSuccess');
    
    if (form && successDiv) {
        form.style.display = 'none';
        successDiv.style.display = 'block';
        
        // Scroll to success message
        successDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
}

function showFormError() {
    // Create or show error message
    let errorDiv = document.querySelector('.contact-form-error');
    
    if (!errorDiv) {
        errorDiv = document.createElement('div');
        errorDiv.className = 'contact-form-error';
        errorDiv.innerHTML = `
            <div class="error-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="15" y1="9" x2="9" y2="15"></line>
                    <line x1="9" y1="9" x2="15" y2="15"></line>
                </svg>
            </div>
            <h3>Message Failed to Send</h3>
            <p>We're sorry, but there was an error sending your message. Please try again or contact us directly at <a href="mailto:hello@aitriadmodel.com">hello@aitriadmodel.com</a>.</p>
            <button class="btn btn--secondary" onclick="hideFormError()">Try Again</button>
        `;
        
        const formContainer = document.querySelector('.contact-form-container');
        if (formContainer) {
            formContainer.appendChild(errorDiv);
        }
    }
    
    errorDiv.style.display = 'block';
    errorDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function hideFormError() {
    const errorDiv = document.querySelector('.contact-form-error');
    if (errorDiv) {
        errorDiv.style.display = 'none';
    }
}

function resetContactForm() {
    const form = document.getElementById('contactForm');
    const successDiv = document.getElementById('formSuccess');
    
    if (form && successDiv) {
        form.reset();
        form.style.display = 'flex';
        successDiv.style.display = 'none';
        
        // Scroll back to form
        form.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// Make resetContactForm globally available
window.resetContactForm = resetContactForm;

/**
 * Form Validation
 */
function initializeFormValidation() {
    const form = document.getElementById('contactForm');
    if (!form) return;
    
    const inputs = form.querySelectorAll('.form-input, .form-select, .form-textarea');
    
    inputs.forEach(input => {
        input.addEventListener('blur', validateField);
        input.addEventListener('input', clearFieldError);
    });
}

function validateField(e) {
    const field = e.target;
    const value = field.value.trim();
    const fieldName = field.name;
    
    // Remove existing error styling
    clearFieldError(e);
    
    // Validation rules
    let isValid = true;
    let errorMessage = '';
    
    if (field.required && !value) {
        isValid = false;
        errorMessage = 'This field is required.';
    } else if (fieldName === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            isValid = false;
            errorMessage = 'Please enter a valid email address.';
        }
    } else if (fieldName === 'message' && value && value.length < 10) {
        isValid = false;
        errorMessage = 'Please provide a more detailed message (at least 10 characters).';
    }
    
    if (!isValid) {
        showFieldError(field, errorMessage);
    }
    
    return isValid;
}

function showFieldError(field, message) {
    field.style.borderColor = '#EF4444';
    
    // Remove existing error message
    const existingError = field.parentNode.querySelector('.field-error');
    if (existingError) {
        existingError.remove();
    }
    
    // Add error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error';
    errorDiv.textContent = message;
    errorDiv.style.cssText = `
        color: #EF4444;
        font-size: 0.875rem;
        margin-top: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    `;
    
    field.parentNode.appendChild(errorDiv);
}

function clearFieldError(e) {
    const field = e.target;
    field.style.borderColor = '';
    
    const errorDiv = field.parentNode.querySelector('.field-error');
    if (errorDiv) {
        errorDiv.remove();
    }
}

/**
 * FAQ Section
 */
function initializeFAQ() {
    const faqButtons = document.querySelectorAll('.faq-question');
    
    faqButtons.forEach(button => {
        button.addEventListener('click', toggleFAQ);
    });
}

function toggleFAQ(e) {
    const button = e.currentTarget;
    const faqItem = button.closest('.faq-item');
    const isActive = faqItem.classList.contains('active');
    
    // Close all other FAQ items
    document.querySelectorAll('.faq-item.active').forEach(item => {
        if (item !== faqItem) {
            item.classList.remove('active');
        }
    });
    
    // Toggle current item
    if (isActive) {
        faqItem.classList.remove('active');
    } else {
        faqItem.classList.add('active');
    }
}

// Make toggleFAQ globally available for inline onclick handlers
window.toggleFAQ = toggleFAQ;

/**
 * Contact Method Interactions
 */
function initializeContactMethods() {
    const contactEmails = document.querySelectorAll('.contact-email');
    
    contactEmails.forEach(email => {
        email.addEventListener('click', function(e) {
            // Add click tracking or analytics here if needed
            console.log('Email contact clicked:', this.href);
        });
    });
    
    const contactLinks = document.querySelectorAll('.contact-link');
    
    contactLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // Add click tracking or analytics here if needed
            console.log('Contact link clicked:', this.href);
        });
    });
}

/**
 * Form Analytics and Enhancement
 */
function trackFormInteraction(action, data = {}) {
    // Placeholder for analytics tracking
    console.log('Form interaction:', action, data);
    
    // Example: Google Analytics tracking
    // if (typeof gtag !== 'undefined') {
    //     gtag('event', action, {
    //         event_category: 'Contact Form',
    //         ...data
    //     });
    // }
}

/**
 * Auto-save Form Data (Optional Enhancement)
 */
function initializeFormAutoSave() {
    const form = document.getElementById('contactForm');
    if (!form) return;
    
    const inputs = form.querySelectorAll('.form-input, .form-select, .form-textarea');
    const storageKey = 'contact-form-draft';
    
    // Load saved data
    loadFormData();
    
    // Save data on input
    inputs.forEach(input => {
        input.addEventListener('input', debounce(saveFormData, 1000));
    });
    
    function saveFormData() {
        const formData = new FormData(form);
        const data = Object.fromEntries(formData);
        localStorage.setItem(storageKey, JSON.stringify(data));
    }
    
    function loadFormData() {
        try {
            const saved = localStorage.getItem(storageKey);
            if (saved) {
                const data = JSON.parse(saved);
                Object.keys(data).forEach(key => {
                    const field = form.querySelector(`[name="${key}"]`);
                    if (field && field.type !== 'checkbox') {
                        field.value = data[key];
                    } else if (field && field.type === 'checkbox') {
                        field.checked = data[key] === 'on' || data[key] === '1';
                    }
                });
            }
        } catch (error) {
            console.error('Error loading form data:', error);
        }
    }
    
    // Clear saved data on successful submission
    form.addEventListener('submit', function() {
        setTimeout(() => {
            if (document.getElementById('formSuccess').style.display !== 'none') {
                localStorage.removeItem(storageKey);
            }
        }, 100);
    });
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
 * Accessibility Enhancements
 */
function initializeAccessibility() {
    // Add ARIA labels and descriptions
    const form = document.getElementById('contactForm');
    if (form) {
        form.setAttribute('aria-label', 'Contact form');
        
        const requiredFields = form.querySelectorAll('[required]');
        requiredFields.forEach(field => {
            const label = form.querySelector(`label[for="${field.id}"]`);
            if (label && !label.textContent.includes('*')) {
                label.innerHTML += ' <span aria-label="required" style="color: #EF4444;">*</span>';
            }
        });
    }
    
    // Enhance FAQ accessibility
    const faqButtons = document.querySelectorAll('.faq-question');
    faqButtons.forEach((button, index) => {
        button.setAttribute('aria-expanded', 'false');
        button.setAttribute('aria-controls', `faq-answer-${index}`);
        
        const answer = button.nextElementSibling;
        if (answer) {
            answer.id = `faq-answer-${index}`;
            answer.setAttribute('aria-labelledby', `faq-question-${index}`);
        }
        
        button.id = `faq-question-${index}`;
    });
}

// Initialize all enhancements
document.addEventListener('DOMContentLoaded', function() {
    initializeContactMethods();
    initializeFormAutoSave();
    initializeAccessibility();
});

/**
 * Form Field Enhancements
 */
function initializeFieldEnhancements() {
    // Character counter for message field
    const messageField = document.getElementById('message');
    if (messageField) {
        const maxLength = 1000;
        
        const counter = document.createElement('div');
        counter.className = 'character-counter';
        counter.style.cssText = `
            color: var(--gray-400);
            font-size: 0.8125rem;
            text-align: right;
            margin-top: 0.5rem;
        `;
        
        messageField.parentNode.appendChild(counter);
        
        function updateCounter() {
            const remaining = maxLength - messageField.value.length;
            counter.textContent = `${remaining} characters remaining`;
            
            if (remaining < 100) {
                counter.style.color = '#F59E0B';
            } else if (remaining < 50) {
                counter.style.color = '#EF4444';
            } else {
                counter.style.color = 'var(--gray-400)';
            }
        }
        
        messageField.addEventListener('input', updateCounter);
        messageField.setAttribute('maxlength', maxLength);
        updateCounter();
    }
}

// Initialize field enhancements
document.addEventListener('DOMContentLoaded', initializeFieldEnhancements);