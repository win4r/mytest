/* AI博客主题脚本 - blog-theme.js */

// 博客主题初始化
class BlogTheme {
    constructor() {
        this.init();
    }

    init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setup());
        } else {
            this.setup();
        }
    }

    setup() {
        this.initAOS();
        this.initProgressBar();
        this.initSmoothScroll();
        this.initTagEffects();
        this.initCardEffects();
    }

    initAOS() {
        if (typeof AOS !== 'undefined') {
            AOS.init({
                duration: 800,
                once: true,
                offset: 100
            });
        }
    }

    initProgressBar() {
        const progressBar = document.getElementById('progress');
        if (!progressBar) return;

        const updateProgress = () => {
            const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
            const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
            const scrolled = (winScroll / height) * 100;
            progressBar.style.transform = `scaleX(${Math.min(scrolled / 100, 1)})`;
        };

        window.addEventListener('scroll', updateProgress);
        updateProgress();
    }

    initSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', (e) => {
                e.preventDefault();
                const targetId = anchor.getAttribute('href');
                
                if (targetId === '#top' || targetId === '#') {
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                } else {
                    const target = document.querySelector(targetId);
                    if (target) {
                        target.scrollIntoView({
                            behavior: 'smooth',
                            block: 'start'
                        });
                    }
                }
            });
        });
    }

    initTagEffects() {
        document.querySelectorAll('.tag').forEach(tag => {
            tag.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-2px) scale(1.05)';
            });
            
            tag.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0) scale(1)';
            });
        });
    }

    initCardEffects() {
        const blogCard = document.querySelector('.blog-card');
        if (!blogCard) return;

        blogCard.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });

        blogCard.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    }
}

// 初始化博客主题
const blogTheme = new BlogTheme();
