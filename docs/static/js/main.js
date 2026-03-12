// SpeechParaling-Bench - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize
    initNavigation();
    initLeaderboardTabs();
    initSmoothScroll();
});

// Navigation functionality
function initNavigation() {
    const header = document.querySelector('.header');
    
    // Add shadow on scroll
    window.addEventListener('scroll', function() {
        if (window.scrollY > 10) {
            header.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1)';
        } else {
            header.style.boxShadow = '0 1px 2px 0 rgba(0, 0, 0, 0.05)';
        }
    });
}

// Leaderboard tab switching
function initLeaderboardTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tables = document.querySelectorAll('.leaderboard-table');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const tabId = this.getAttribute('data-tab');
            
            // Update active button
            tabBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            // Show corresponding table
            tables.forEach(table => {
                table.classList.remove('active');
                if (table.id === tabId) {
                    table.classList.add('active');
                }
            });
        });
    });
}

// Smooth scroll for anchor links
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                const headerOffset = 80;
                const elementPosition = target.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - headerOffset;
                
                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
}

// Add animation on scroll (optional enhancement)
function initScrollAnimation() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);
    
    document.querySelectorAll('.dimension-card, .example-card, .composition-item').forEach(el => {
        observer.observe(el);
    });
}
