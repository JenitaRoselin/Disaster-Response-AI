/**
 * Disaster Response AI - Navigation & Interactions
 */

/**
 * Typing animation effect for hero title
 */
function typeWriter(element, text, speed = 50) {
    let index = 0;
    element.innerHTML = '';
    element.classList.add('typing');
    
    function type() {
        if (index < text.length) {
            const char = text.charAt(index);
            if (char === '\n') {
                element.innerHTML += '<br>';
            } else {
                element.innerHTML += char;
            }
            index++;
            setTimeout(type, speed);
        } else {
            element.classList.remove('typing');
        }
    }
    
    type();
}

/**
 * Handle login form submission
 * Redirects to the ticket dashboard on login
 */
function handleLogin(event) {
    event.preventDefault();
    
    // Get form values
    const employeeId = document.getElementById('employee-id').value;
    const password = document.getElementById('password').value;
    
    // Simple validation
    if (!employeeId.trim() || !password.trim()) {
        alert('Please fill in all fields');
        return;
    }
    
    // Store user info in sessionStorage (for demo purposes)
    sessionStorage.setItem('userLoggedIn', 'true');
    sessionStorage.setItem('userId', employeeId);
    
    // Redirect to dashboard
    window.location.href = 'dashboard.html';
}

/**
 * Initialize the page - check navigation states
 */
document.addEventListener('DOMContentLoaded', function() {
    // Start typing animation if on home page
    const typingTitle = document.getElementById('typingTitle');
    if (typingTitle) {
        const text = 'Disaster Response AI:\n4-Phase Integrated Pipeline';
        typeWriter(typingTitle, text, 50);
    }
    
    // Update navigation active states
    updateNavigation();
    
    // Add smooth scroll behavior for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});

/**
 * Update navigation active states based on current page
 */
function updateNavigation() {
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    
    // Get all navigation links
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        link.classList.remove('active');
        
        // Check if link href matches current page
        const href = link.getAttribute('href');
        if (href === currentPage || (currentPage === '' && href === 'index.html')) {
            link.classList.add('active');
        }
    });
}

/**
 * Smooth scroll to top on page load
 */
window.addEventListener('load', function() {
    window.scrollTo(0, 0);
});

/**
 * Debounce utility function
 */
function debounce(func, delay) {
    let timeoutId;
    return function(...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func(...args), delay);
    };
}

/**
 * Handle window resize for responsive features
 */
const handleResize = debounce(function() {
    // Add any resize-specific logic here if needed
}, 250);

window.addEventListener('resize', handleResize);

/**
 * Add keyboard navigation support
 */
document.addEventListener('keydown', function(event) {
    // Press 'H' to go home
    if (event.key === 'h' || event.key === 'H') {
        if (event.ctrlKey || event.metaKey) {
            window.location.href = 'index.html';
        }
    }
    
    // Press 'L' to go to login
    if (event.key === 'l' || event.key === 'L') {
        if (event.ctrlKey || event.metaKey) {
            window.location.href = 'login.html';
        }
    }
    
    // Press 'D' to go to dashboard
    if (event.key === 'd' || event.key === 'D') {
        if (event.ctrlKey || event.metaKey) {
            window.location.href = 'dashboard.html';
        }
    }
});

/**
 * Logout function (for future use)
 */
function logout() {
    sessionStorage.clear();
    window.location.href = 'index.html';
}

/**
 * Format urgency level for display
 */
function formatUrgency(urgency) {
    const urgencyMap = {
        'critical': 'CRITICAL',
        'high': 'HIGH',
        'medium': 'MEDIUM'
    };
    return urgencyMap[urgency] || urgency.toUpperCase();
}

/**
 * Animate elements on scroll
 */
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.animation = 'fadeIn 0.6s ease-in-out';
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

// Observe all feature cards and ticket cards
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.feature-card, .ticket-card').forEach(el => {
        observer.observe(el);
    });
});
