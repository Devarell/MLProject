// Script untuk website Prediksi Nilai

document.addEventListener('DOMContentLoaded', function() {
    // Toggle Menu untuk Perangkat Mobile
    const menuToggle = document.querySelector('.menu-toggle');
    const nav = document.querySelector('nav');
    
    menuToggle.addEventListener('click', function() {
        nav.classList.toggle('active');
    });

    // Menutup menu saat mengklik di luar menu
    document.addEventListener('click', function(event) {
        const isClickInsideNav = nav.contains(event.target);
        const isClickOnToggle = menuToggle.contains(event.target);
        
        if (!isClickInsideNav && !isClickOnToggle && nav.classList.contains('active')) {
            nav.classList.remove('active');
        }
    });

    // Animasi smooth scroll untuk anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 80,
                    behavior: 'smooth'
                });
            }
        });
    });

    // Animasi kemunculan elemen saat di-scroll
    const animateOnScroll = function() {
        const elements = document.querySelectorAll('.feature-card, .about-content, .section-header');
        
        elements.forEach(element => {
            const elementPosition = element.getBoundingClientRect().top;
            const windowHeight = window.innerHeight;
            
            if (elementPosition < windowHeight - 50) {
                element.classList.add('fade-in');
            }
        });
    };

    // Tambahkan class untuk animasi
    const elementsToAnimate = document.querySelectorAll('.feature-card, .about-content, .section-header');
    elementsToAnimate.forEach(element => {
        element.classList.add('to-animate');
    });

    // Tambahkan CSS untuk animasi
    const style = document.createElement('style');
    style.textContent = `
        .to-animate {
            opacity: 0;
            transform: translateY(30px);
            transition: opacity 0.6s ease, transform 0.6s ease;
        }
        
        .fade-in {
            opacity: 1;
            transform: translateY(0);
        }
    `;
    document.head.appendChild(style);

    // Jalankan animasi saat halaman dimuat dan di-scroll
    window.addEventListener('scroll', animateOnScroll);
    animateOnScroll(); // Panggil sekali saat halaman dimuat

    // Header menjadi sticky pada scroll
    const header = document.querySelector('header');
    const makeHeaderSticky = function() {
        if (window.scrollY > 10) {
            header.classList.add('sticky');
            // Tambahkan CSS untuk header sticky
            if (!document.querySelector('.sticky-style')) {
                const stickyStyle = document.createElement('style');
                stickyStyle.classList.add('sticky-style');
                stickyStyle.textContent = `
                    .sticky {
                        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
                        transition: all 0.3s ease;
                    }
                `;
                document.head.appendChild(stickyStyle);
            }
        } else {
            header.classList.remove('sticky');
        }
    };

    window.addEventListener('scroll', makeHeaderSticky);
    makeHeaderSticky(); // Panggil sekali saat halaman dimuat

    // Tambahkan efek hover pada cards
    const featureCards = document.querySelectorAll('.feature-card');
    
    featureCards.forEach(card => {
        card.addEventListener('mouseover', function() {
            this.style.boxShadow = '0 10px 25px rgba(78, 115, 223, 0.15)';
        });
        
        card.addEventListener('mouseout', function() {
            this.style.boxShadow = '0 4px 15px rgba(0, 0, 0, 0.05)';
        });
    });

    // Tambahkan counter untuk statistik (demo)
    const addCounterAnimation = function() {
        // Cek apakah counter sudah ada di halaman
        if (!document.querySelector('.counter-section')) {
            // Counter section bisa ditambahkan melalui JavaScript kalau diperlukan
            console.log('Counter section tidak ada di halaman ini.');
            return;
        }
        
        const counters = document.querySelectorAll('.counter');
        
        counters.forEach(counter => {
            const target = parseInt(counter.getAttribute('data-target'));
            const duration = 2000; // ms
            const steps = 50;
            const stepValue = target / steps;
            let current = 0;
            
            const updateCounter = setInterval(function() {
                current += stepValue;
                
                if (current >= target) {
                    counter.textContent = target;
                    clearInterval(updateCounter);
                } else {
                    counter.textContent = Math.round(current);
                }
            }, duration / steps);
        });
    };
    
    // Panggil fungsi counter jika ada section counter di halaman
    if (document.querySelector('.counter-section')) {
        // Tambahkan observer untuk memulai counter ketika section terlihat
        const counterObserver = new IntersectionObserver(
            (entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        addCounterAnimation();
                        observer.unobserve(entry.target);
                    }
                });
            },
            { threshold: 0.5 }
        );
        
        counterObserver.observe(document.querySelector('.counter-section'));
    }

    // Preloader (opsional)
    const preloader = document.querySelector('.preloader');
    if (preloader) {
        window.addEventListener('load', function() {
            preloader.style.opacity = '0';
            setTimeout(function() {
                preloader.style.display = 'none';
            }, 500);
        });
    }
});