/* ═══════════════════════════════════════════════════════════════
   Job Recommendation System — JavaScript
   Handles tabs, drag-and-drop, form submission, and result animations
   ═══════════════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {
    initNavbar();
    initTabs();
    initFileUpload();
    initFormSubmission();
    initFlashMessages();
    initResultAnimations();
    initExpandCards();
    initSortControls();
});

/* ─── Navbar Scroll Effect ────────────────────────────────────── */
function initNavbar() {
    const navbar = document.querySelector('.nav-bar');
    if (!navbar) return;

    window.addEventListener('scroll', () => {
        if (window.scrollY > 30) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
}

/* ─── Tab Switching ───────────────────────────────────────────── */
function initTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');
    const inputModeField = document.getElementById('input-mode');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const target = btn.dataset.tab;

            // Update buttons
            tabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Update panes
            tabPanes.forEach(p => p.classList.remove('active'));
            const targetPane = document.getElementById(target);
            if (targetPane) targetPane.classList.add('active');

            // Update hidden field
            if (inputModeField) {
                inputModeField.value = target === 'tab-upload' ? 'upload' : 'manual';
            }
        });
    });
}

/* ─── File Upload (Drag & Drop) ───────────────────────────────── */
function initFileUpload() {
    const uploadZone = document.querySelector('.upload-zone');
    const fileInput = document.getElementById('resume-file');
    const fileName = document.querySelector('.file-name');

    if (!uploadZone || !fileInput) return;

    // Drag events
    ['dragenter', 'dragover'].forEach(event => {
        uploadZone.addEventListener(event, (e) => {
            e.preventDefault();
            e.stopPropagation();
            uploadZone.classList.add('drag-over');
        });
    });

    ['dragleave', 'drop'].forEach(event => {
        uploadZone.addEventListener(event, (e) => {
            e.preventDefault();
            e.stopPropagation();
            uploadZone.classList.remove('drag-over');
        });
    });

    // Handle drop
    uploadZone.addEventListener('drop', (e) => {
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            fileInput.files = files;
            updateFileName(files[0]);
        }
    });

    // Handle file input change
    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            updateFileName(fileInput.files[0]);
        }
    });

    function updateFileName(file) {
        if (fileName) {
            fileName.textContent = `📄 ${file.name}`;
            uploadZone.classList.add('has-file');

            // Validate file type
            if (!file.name.toLowerCase().endsWith('.pdf')) {
                fileName.textContent = '⚠️ Please select a PDF file';
                fileName.style.color = '#e17055';
                uploadZone.classList.remove('has-file');
            } else {
                fileName.style.color = '';
            }
        }
    }
}

/* ─── Form Submission ─────────────────────────────────────────── */
function initFormSubmission() {
    const form = document.getElementById('recommend-form');
    if (!form) return;

    form.addEventListener('submit', (e) => {
        const inputMode = document.getElementById('input-mode')?.value;
        const submitBtn = form.querySelector('.btn-submit');

        if (inputMode === 'upload') {
            const fileInput = document.getElementById('resume-file');
            if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
                e.preventDefault();
                showToast('Please upload a PDF resume file.', 'error');
                return;
            }
        } else {
            const skills = document.getElementById('skills-input')?.value?.trim();
            const experience = document.getElementById('experience-input')?.value?.trim();
            const qualifications = document.getElementById('qualifications-input')?.value?.trim();

            if (!skills && !experience && !qualifications) {
                e.preventDefault();
                showToast('Please enter at least your skills or experience.', 'error');
                return;
            }
        }

        // Show loading state
        if (submitBtn) {
            submitBtn.classList.add('loading');
            const btnText = submitBtn.querySelector('.btn-text');
            if (btnText) btnText.textContent = 'Analyzing...';
        }
    });
}

/* ─── Toast Notifications ─────────────────────────────────────── */
function showToast(message, type = 'info') {
    let container = document.querySelector('.flash-messages');
    if (!container) {
        container = document.createElement('div');
        container.className = 'flash-messages';
        document.body.appendChild(container);
    }

    const icons = {
        error: '❌',
        warning: '⚠️',
        success: '✅',
        info: 'ℹ️'
    };

    const msg = document.createElement('div');
    msg.className = `flash-msg ${type}`;
    msg.innerHTML = `<span>${icons[type] || ''}</span> ${message}`;
    container.appendChild(msg);

    setTimeout(() => {
        msg.style.opacity = '0';
        msg.style.transform = 'translateX(40px)';
        msg.style.transition = '0.3s ease-out';
        setTimeout(() => msg.remove(), 300);
    }, 4000);
}

/* ─── Flash Messages Auto-dismiss ─────────────────────────────── */
function initFlashMessages() {
    const flashMsgs = document.querySelectorAll('.flash-msg');
    flashMsgs.forEach((msg, i) => {
        setTimeout(() => {
            msg.style.opacity = '0';
            msg.style.transform = 'translateX(40px)';
            msg.style.transition = '0.3s ease-out';
            setTimeout(() => msg.remove(), 300);
        }, 4000 + i * 500);
    });
}

/* ─── Result Animations (Score circles, staggered fade-in) ────── */
function initResultAnimations() {
    const jobCards = document.querySelectorAll('.job-card');
    if (jobCards.length === 0) return;

    // Stagger card animations
    jobCards.forEach((card, index) => {
        card.style.animationDelay = `${0.1 + index * 0.08}s`;
    });

    // Animate score circles
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const circle = entry.target;
                const progress = circle.querySelector('.progress');
                const scoreNum = circle.querySelector('.score-number');

                if (progress && scoreNum) {
                    const score = parseFloat(scoreNum.dataset.score || scoreNum.textContent);
                    const circumference = 207; // 2 * PI * 33
                    const offset = circumference - (score / 100) * circumference;

                    // Animate the circle
                    setTimeout(() => {
                        progress.style.strokeDashoffset = offset;
                    }, 200);

                    // Animate the number
                    animateCounter(scoreNum, 0, score, 1200);
                }

                observer.unobserve(circle);
            }
        });
    }, { threshold: 0.3 });

    document.querySelectorAll('.score-circle').forEach(circle => {
        observer.observe(circle);
    });

    // Animate skill progress bars
    const barObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const bar = entry.target;
                const targetWidth = bar.dataset.width;
                setTimeout(() => {
                    bar.style.width = targetWidth + '%';
                }, 300);
                barObserver.unobserve(bar);
            }
        });
    }, { threshold: 0.3 });

    document.querySelectorAll('.skills-progress-fill').forEach(bar => {
        barObserver.observe(bar);
    });
}

/* ─── Animate Counter ─────────────────────────────────────────── */
function animateCounter(element, start, end, duration) {
    const startTime = performance.now();

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3); // easeOutCubic

        const current = start + (end - start) * eased;
        element.textContent = current.toFixed(1) + '%';

        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }

    requestAnimationFrame(update);
}

/* ─── Expandable Job Cards ────────────────────────────────────── */
function initExpandCards() {
    const expandBtns = document.querySelectorAll('.job-expand-btn');

    expandBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const card = btn.closest('.job-card');
            const details = card?.querySelector('.job-details');

            if (details) {
                const isExpanded = details.classList.contains('expanded');
                details.classList.toggle('expanded');
                btn.classList.toggle('expanded');

                if (!isExpanded) {
                    // Scroll into view smoothly
                    setTimeout(() => {
                        card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                    }, 100);
                }
            }
        });
    });
}

/* ─── Sort Controls ───────────────────────────────────────────── */
function initSortControls() {
    const sortBtns = document.querySelectorAll('.sort-btn');
    const jobsGrid = document.querySelector('.jobs-grid');

    if (!sortBtns.length || !jobsGrid) return;

    sortBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Update active state
            sortBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const sortBy = btn.dataset.sort;
            const cards = Array.from(jobsGrid.querySelectorAll('.job-card'));

            cards.sort((a, b) => {
                if (sortBy === 'score') {
                    const scoreA = parseFloat(a.dataset.score || 0);
                    const scoreB = parseFloat(b.dataset.score || 0);
                    return scoreB - scoreA;
                } else if (sortBy === 'title') {
                    const titleA = a.dataset.title || '';
                    const titleB = b.dataset.title || '';
                    return titleA.localeCompare(titleB);
                } else if (sortBy === 'skills') {
                    const skillsA = parseInt(a.dataset.matchedSkills || 0);
                    const skillsB = parseInt(b.dataset.matchedSkills || 0);
                    return skillsB - skillsA;
                }
                return 0;
            });

            // Re-render with animation
            cards.forEach((card, i) => {
                card.style.animation = 'none';
                card.offsetHeight; // trigger reflow
                card.style.animation = '';
                card.style.animationDelay = `${i * 0.05}s`;
                jobsGrid.appendChild(card);
            });
        });
    });
}
