// Global variables
let currentUser = null;
let isLoggedIn = false;

// Initialize application
$(document).ready(function() {
    initializeApp();
    setupEventListeners();
    checkAuthStatus();
});

function initializeApp() {
    // Add loading animations
    $('body').addClass('fade-in-up');
    
    // Initialize tooltips
    if (typeof bootstrap !== 'undefined') {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // Initialize smooth scrolling
    $('a[href^="#"]').on('click', function(event) {
        var target = $(this.getAttribute('href'));
        if (target.length) {
            event.preventDefault();
            $('html, body').stop().animate({
                scrollTop: target.offset().top - 100
            }, 1000);
        }
    });
}

function setupEventListeners() {
    // Login form
    $('#loginForm').on('submit', function(e) {
        e.preventDefault();
        handleLogin();
    });
    
    // Register form
    $('#registerForm').on('submit', function(e) {
        e.preventDefault();
        handleRegister();
    });
    
    // Add scroll effects
    $(window).scroll(function() {
        handleScrollEffects();
    });
    
    // Add hover effects to cards
    $('.feature-card, .artisan-card, .step-card').hover(
        function() {
            $(this).addClass('shadow-medium');
        },
        function() {
            $(this).removeClass('shadow-medium');
        }
    );
}

function checkAuthStatus() {
    // Check if user is logged in (simplified - in real app would check session/token)
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('logged_in') === 'true') {
        isLoggedIn = true;
        updateUIForLoggedInUser();
    }
}

function updateUIForLoggedInUser() {
    // Update navigation and UI elements for logged in users
    $('.login-required').show();
    $('.guest-only').hide();
}

function handleLogin() {
    const username = $('#loginUsername').val();
    const password = $('#loginPassword').val();
    
    if (!username || !password) {
        showAlert('Please fill in all fields', 'error');
        return;
    }
    
    // Show loading state
    const submitBtn = $('#loginForm button[type="submit"]');
    const originalText = submitBtn.html();
    submitBtn.html('<i class="fas fa-spinner fa-spin me-2"></i>Logging in...').prop('disabled', true);
    
    $.ajax({
        url: '/login',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            username: username,
            password: password
        }),
        success: function(response) {
            if (response.success) {
                $('#loginModal').modal('hide');
                showAlert('Login successful! Redirecting...', 'success');
                
                setTimeout(() => {
                    window.location.reload();
                }, 1500);
            } else {
                showAlert(response.message || 'Login failed', 'error');
            }
        },
        error: function() {
            showAlert('An error occurred. Please try again.', 'error');
        },
        complete: function() {
            submitBtn.html(originalText).prop('disabled', false);
        }
    });
}

function handleRegister() {
    const username = $('#registerUsername').val();
    const email = $('#registerEmail').val();
    const password = $('#registerPassword').val();
    const userType = $('#userType').val();
    
    if (!username || !email || !password || !userType) {
        showAlert('Please fill in all fields', 'error');
        return;
    }
    
    // Validate email
    if (!isValidEmail(email)) {
        showAlert('Please enter a valid email address', 'error');
        return;
    }
    
    // Validate password strength
    if (password.length < 6) {
        showAlert('Password must be at least 6 characters long', 'error');
        return;
    }
    
    // Show loading state
    const submitBtn = $('#registerForm button[type="submit"]');
    const originalText = submitBtn.html();
    submitBtn.html('<i class="fas fa-spinner fa-spin me-2"></i>Creating Account...').prop('disabled', true);
    
    $.ajax({
        url: '/register',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            username: username,
            email: email,
            password: password,
            user_type: userType
        }),
        success: function(response) {
            if (response.success) {
                $('#registerModal').modal('hide');
                showAlert('Account created successfully!', 'success');
                
                // Redirect based on user type
                setTimeout(() => {
                    if (userType === 'artisan') {
                        window.location.href = '/artisan/onboard';
                    } else {
                        window.location.reload();
                    }
                }, 1500);
            } else {
                showAlert(response.message || 'Registration failed', 'error');
            }
        },
        error: function() {
            showAlert('An error occurred. Please try again.', 'error');
        },
        complete: function() {
            submitBtn.html(originalText).prop('disabled', false);
        }
    });
}

function showLoginModal() {
    $('#loginModal').modal('show');
}

function showRegisterModal() {
    $('#registerModal').modal('show');
}

function handleScrollEffects() {
    const scrollTop = $(window).scrollTop();
    
    // Navbar background opacity
    if (scrollTop > 50) {
        $('.navbar').addClass('navbar-scrolled');
    } else {
        $('.navbar').removeClass('navbar-scrolled');
    }
    
    // Parallax effect for hero section
    if ($('.hero-section').length) {
        const parallaxSpeed = 0.5;
        $('.hero-section').css('transform', `translateY(${scrollTop * parallaxSpeed}px)`);
    }
    
    // Animate elements on scroll
    $('.feature-card, .artisan-card, .step-card').each(function() {
        const elementTop = $(this).offset().top;
        const elementBottom = elementTop + $(this).outerHeight();
        const viewportTop = scrollTop;
        const viewportBottom = viewportTop + $(window).height();
        
        if (elementBottom > viewportTop && elementTop < viewportBottom) {
            $(this).addClass('fade-in-up');
        }
    });
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function showAlert(message, type = 'info') {
    const alertClass = {
        'success': 'alert-success',
        'error': 'alert-danger',
        'warning': 'alert-warning',
        'info': 'alert-info'
    }[type] || 'alert-info';
    
    const alertIcon = {
        'success': 'fas fa-check-circle',
        'error': 'fas fa-exclamation-circle',
        'warning': 'fas fa-exclamation-triangle',
        'info': 'fas fa-info-circle'
    }[type] || 'fas fa-info-circle';
    
    const alertHtml = `
        <div class="alert ${alertClass} alert-dismissible fade show position-fixed" 
             style="top: 100px; right: 20px; z-index: 9999; min-width: 300px;" role="alert">
            <i class="${alertIcon} me-2"></i>${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    $('body').append(alertHtml);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        $('.alert').fadeOut(500, function() {
            $(this).remove();
        });
    }, 5000);
}

// Utility functions for animations
function animateCounter(element, target, duration = 2000) {
    const start = 0;
    const increment = target / (duration / 16);
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            current = target;
            clearInterval(timer);
        }
        $(element).text(Math.floor(current));
    }, 16);
}

function animateProgressBar(element, percentage, duration = 1000) {
    $(element).animate({
        width: percentage + '%'
    }, duration);
}

// Intersection Observer for scroll animations
if ('IntersectionObserver' in window) {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
                
                // Animate counters
                if (entry.target.classList.contains('stat-value')) {
                    const target = parseInt(entry.target.textContent.replace(/[^\d]/g, ''));
                    if (target) {
                        animateCounter(entry.target, target);
                    }
                }
                
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observe elements
    document.querySelectorAll('.feature-card, .artisan-card, .step-card, .stat-value').forEach(el => {
        observer.observe(el);
    });
}

// Touch and swipe support for mobile
let touchStartX = 0;
let touchEndX = 0;

function handleSwipe() {
    const swipeThreshold = 50;
    const swipeDistance = touchEndX - touchStartX;
    
    if (Math.abs(swipeDistance) > swipeThreshold) {
        if (swipeDistance > 0) {
            // Swipe right
            triggerSwipeRight();
        } else {
            // Swipe left
            triggerSwipeLeft();
        }
    }
}

function triggerSwipeRight() {
    // Handle swipe right actions
    console.log('Swiped right');
}

function triggerSwipeLeft() {
    // Handle swipe left actions
    console.log('Swiped left');
}

// Add touch event listeners
document.addEventListener('touchstart', (e) => {
    touchStartX = e.changedTouches[0].screenX;
});

document.addEventListener('touchend', (e) => {
    touchEndX = e.changedTouches[0].screenX;
    handleSwipe();
});

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + K for search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        // Open search modal or focus search input
        console.log('Search shortcut triggered');
    }
    
    // Escape to close modals
    if (e.key === 'Escape') {
        $('.modal.show').modal('hide');
    }
});

// Performance optimization - lazy loading images
function lazyLoadImages() {
    const images = document.querySelectorAll('img[data-src]');
    
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
    
    images.forEach(img => imageObserver.observe(img));
}

// Initialize lazy loading
if ('IntersectionObserver' in window) {
    lazyLoadImages();
}

// Error handling for AJAX requests
$(document).ajaxError(function(event, xhr, settings, thrownError) {
    console.error('AJAX Error:', {
        url: settings.url,
        status: xhr.status,
        error: thrownError
    });
    
    if (xhr.status === 401) {
        showAlert('Session expired. Please log in again.', 'warning');
        // Redirect to login
        setTimeout(() => {
            window.location.href = '/login';
        }, 2000);
    } else if (xhr.status >= 500) {
        showAlert('Server error. Please try again later.', 'error');
    }
});

// Add CSRF token to all AJAX requests (if using CSRF protection)
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
            const csrfToken = $('meta[name=csrf-token]').attr('content');
            if (csrfToken) {
                xhr.setRequestHeader("X-CSRFToken", csrfToken);
            }
        }
    }
});

// Export functions for use in other scripts
window.PersonaApp = {
    showAlert,
    showLoginModal,
    showRegisterModal,
    animateCounter,
    animateProgressBar,
    isValidEmail
};
