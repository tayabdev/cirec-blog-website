// Main JavaScript for CIREC Blog

document.addEventListener('DOMContentLoaded', function () {
    // Initialize all components
    initSearchSuggestions();
    initFormValidation();
    initFileUpload();
    initTooltips();
    initLoadingStates();
    initScrollEffects();
    initThemeToggle();
});

// Search Suggestions
function initSearchSuggestions() {
    const searchInput = document.getElementById('searchInput');
    if (!searchInput) return;

    let suggestionsContainer = null;
    let currentSuggestions = [];
    let selectedIndex = -1;
    let searchTimeout;

    // Create suggestions container
    function createSuggestionsContainer() {
        const container = document.createElement('div');
        container.className = 'search-suggestions';
        container.style.display = 'none';
        searchInput.parentElement.appendChild(container);
        searchInput.parentElement.style.position = 'relative';
        return container;
    }

    // Fetch suggestions from API
    async function fetchSuggestions(query) {
        try {
            const response = await fetch(`/search/api/suggestions?q=${encodeURIComponent(query)}&limit=5`);
            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.error('Error fetching suggestions:', error);
        }
        return [];
    }

    // Display suggestions
    function showSuggestions(suggestions) {
        if (!suggestionsContainer) {
            suggestionsContainer = createSuggestionsContainer();
        }

        if (suggestions.length === 0) {
            suggestionsContainer.style.display = 'none';
            return;
        }

        currentSuggestions = suggestions;
        selectedIndex = -1;

        suggestionsContainer.innerHTML = suggestions.map((suggestion, index) => `
            <div class="search-suggestion" data-index="${index}">
                <div class="search-suggestion-type">${suggestion.type}</div>
                <div>${suggestion.text}</div>
            </div>
        `).join('');

        suggestionsContainer.style.display = 'block';

        // Add click handlers
        suggestionsContainer.querySelectorAll('.search-suggestion').forEach((item, index) => {
            item.addEventListener('click', () => selectSuggestion(index));
        });
    }

    // Select suggestion
    function selectSuggestion(index) {
        if (index >= 0 && index < currentSuggestions.length) {
            const suggestion = currentSuggestions[index];
            if (suggestion.url) {
                window.location.href = suggestion.url;
            } else {
                searchInput.value = suggestion.text;
                hideSuggestions();
            }
        }
    }

    // Hide suggestions
    function hideSuggestions() {
        if (suggestionsContainer) {
            suggestionsContainer.style.display = 'none';
        }
    }

    // Update selected suggestion
    function updateSelection() {
        if (!suggestionsContainer) return;

        suggestionsContainer.querySelectorAll('.search-suggestion').forEach((item, index) => {
            if (index === selectedIndex) {
                item.style.backgroundColor = '#e9ecef';
            } else {
                item.style.backgroundColor = '';
            }
        });
    }

    // Event listeners
    searchInput.addEventListener('input', function () {
        clearTimeout(searchTimeout);
        const query = this.value.trim();

        if (query.length < 2) {
            hideSuggestions();
            return;
        }

        searchTimeout = setTimeout(async () => {
            const suggestions = await fetchSuggestions(query);
            showSuggestions(suggestions);
        }, 300);
    });

    searchInput.addEventListener('keydown', function (e) {
        if (!suggestionsContainer || suggestionsContainer.style.display === 'none') return;

        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                selectedIndex = Math.min(selectedIndex + 1, currentSuggestions.length - 1);
                updateSelection();
                break;
            case 'ArrowUp':
                e.preventDefault();
                selectedIndex = Math.max(selectedIndex - 1, -1);
                updateSelection();
                break;
            case 'Enter':
                e.preventDefault();
                if (selectedIndex >= 0) {
                    selectSuggestion(selectedIndex);
                } else {
                    this.closest('form').submit();
                }
                break;
            case 'Escape':
                hideSuggestions();
                break;
        }
    });

    // Hide suggestions when clicking outside
    document.addEventListener('click', function (e) {
        if (!searchInput.parentElement.contains(e.target)) {
            hideSuggestions();
        }
    });
}

// Form Validation
function initFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');

    forms.forEach(form => {
        form.addEventListener('submit', function (e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });

        // Real-time validation
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('blur', function () {
                validateField(this);
            });

            input.addEventListener('input', function () {
                if (this.classList.contains('is-invalid')) {
                    validateField(this);
                }
            });
        });
    });
}

function validateField(field) {
    const isValid = field.checkValidity();
    field.classList.toggle('is-valid', isValid);
    field.classList.toggle('is-invalid', !isValid);

    // Custom validation messages
    const feedback = field.parentElement.querySelector('.invalid-feedback');
    if (feedback && !isValid) {
        if (field.type === 'email') {
            feedback.textContent = 'Please enter a valid email address.';
        } else if (field.type === 'password') {
            feedback.textContent = 'Password must be at least 8 characters long.';
        } else if (field.required && !field.value) {
            feedback.textContent = 'This field is required.';
        }
    }
}

// File Upload Enhancement
function initFileUpload() {
    const fileInputs = document.querySelectorAll('input[type="file"]');

    fileInputs.forEach(input => {
        const label = input.nextElementSibling;
        const originalText = label ? label.textContent : 'Choose file';

        input.addEventListener('change', function () {
            if (this.files && this.files.length > 0) {
                const fileName = this.files[0].name;
                if (label) {
                    label.textContent = fileName;
                }
            } else {
                if (label) {
                    label.textContent = originalText;
                }
            }
        });

        // Drag and drop
        if (label) {
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                label.addEventListener(eventName, preventDefaults, false);
            });

            ['dragenter', 'dragover'].forEach(eventName => {
                label.addEventListener(eventName, () => label.classList.add('drag-over'), false);
            });

            ['dragleave', 'drop'].forEach(eventName => {
                label.addEventListener(eventName, () => label.classList.remove('drag-over'), false);
            });

            label.addEventListener('drop', handleDrop, false);

            function handleDrop(e) {
                const dt = e.dataTransfer;
                const files = dt.files;
                input.files = files;

                if (files.length > 0) {
                    label.textContent = files[0].name;
                }
            }
        }
    });
}

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

// Initialize tooltips
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Loading states
function initLoadingStates() {
    const forms = document.querySelectorAll('form');

    forms.forEach(form => {
        form.addEventListener('submit', function () {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<span class="loading"></span> Processing...';
                submitBtn.disabled = true;

                // Re-enable after 10 seconds as fallback
                setTimeout(() => {
                    submitBtn.innerHTML = originalText;
                    submitBtn.disabled = false;
                }, 10000);
            }
        });
    });
}

// Scroll effects
function initScrollEffects() {
    // Back to top button
    const backToTop = document.createElement('button');
    backToTop.innerHTML = '<i class="fas fa-chevron-up"></i>';
    backToTop.className = 'btn btn-primary back-to-top';
    backToTop.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 1000;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        display: none;
        opacity: 0;
        transition: all 0.3s ease;
    `;
    document.body.appendChild(backToTop);

    // Show/hide back to top button
    window.addEventListener('scroll', () => {
        if (window.pageYOffset > 300) {
            backToTop.style.display = 'block';
            setTimeout(() => backToTop.style.opacity = '1', 10);
        } else {
            backToTop.style.opacity = '0';
            setTimeout(() => backToTop.style.display = 'none', 300);
        }
    });

    // Smooth scroll to top
    backToTop.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    // Parallax effect for hero sections
    const heroSections = document.querySelectorAll('.hero-section');
    heroSections.forEach(section => {
        window.addEventListener('scroll', () => {
            const scrolled = window.pageYOffset;
            const parallax = scrolled * 0.5;
            section.style.transform = `translateY(${parallax}px)`;
        });
    });
}

// Theme toggle
function initThemeToggle() {
    const themeToggle = document.getElementById('theme-toggle');
    if (!themeToggle) return;

    const currentTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', currentTheme);

    themeToggle.addEventListener('click', function () {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);

        // Update icon
        const icon = this.querySelector('i');
        if (newTheme === 'dark') {
            icon.className = 'fas fa-sun';
        } else {
            icon.className = 'fas fa-moon';
        }
    });
}

// Utility functions
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;

    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container';
        document.body.appendChild(toastContainer);
    }

    toastContainer.appendChild(toast);

    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();

    toast.addEventListener('hidden.bs.toast', () => toast.remove());
}

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

// Lazy loading for images
function initLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');

    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                observer.unobserve(img);
            }
        });
    });

    images.forEach(img => imageObserver.observe(img));
}

// AJAX form submission
function submitFormAjax(form, callback) {
    const formData = new FormData(form);
    const url = form.action || window.location.href;
    const method = form.method || 'POST';

    fetch(url, {
        method: method,
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
        .then(response => response.json())
        .then(data => {
            if (callback) callback(data);
        })
        .catch(error => {
            console.error('Form submission error:', error);
            showToast('An error occurred. Please try again.', 'error');
        });
}

// Search functionality enhancements
function initAdvancedSearch() {
    const searchForm = document.getElementById('advanced-search-form');
    if (!searchForm) return;

    const searchTypeRadios = searchForm.querySelectorAll('input[name="search_type"]');
    const semanticOptions = document.getElementById('semantic-options');

    searchTypeRadios.forEach(radio => {
        radio.addEventListener('change', function () {
            if (this.value === 'semantic' || this.value === 'hybrid') {
                semanticOptions.style.display = 'block';
            } else {
                semanticOptions.style.display = 'none';
            }
        });
    });
}

// Export functions for use in other scripts
window.CIREC = {
    showToast,
    debounce,
    submitFormAjax,
    initLazyLoading,
    validateField
};