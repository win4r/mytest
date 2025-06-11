/* AI博客主题脚本 - blog-theme.js */

// 博客主题初始化
class BlogTheme {
    constructor() {
        this.init();
    }

    init() {
        // 等待DOM加载完成
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

    // 初始化AOS动画库
    initAOS() {
        if (typeof AOS !== 'undefined') {
            AOS.init({
                duration: 800,
                once: true,
                offset: 100
            });
        }
    }

    // 阅读进度条
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
        updateProgress(); // 初始化
    }

    // 平滑滚动
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

    // 标签交互效果
    initTagEffects() {
        document.querySelectorAll('.tag').forEach(tag => {
            tag.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-2px) scale(1.05)';
            });
            
            tag.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0) scale(1)';
            });

            tag.addEventListener('click', function(e) {
                // 添加点击波纹效果
                const ripple = document.createElement('span');
                ripple.classList.add('ripple');
                this.appendChild(ripple);
                
                setTimeout(() => {
                    ripple.remove();
                }, 600);
            });
        });
    }

    // 博客卡片效果
    initCardEffects() {
        const blogCard = document.querySelector('.blog-card');
        if (!blogCard) return;

        // 鼠标进入效果
        blogCard.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });

        blogCard.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });

        // 添加观察者，实现滚动动画
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate__animated', 'animate__fadeInUp');
                }
            });
        }, {
            threshold: 0.1
        });

        observer.observe(blogCard);
    }

    // 添加返回顶部按钮
    addBackToTop() {
        const backToTop = document.createElement('button');
        backToTop.innerHTML = '<i class="fas fa-arrow-up"></i>';
        backToTop.className = 'btn btn-primary position-fixed bottom-0 end-0 m-3 rounded-circle';
        backToTop.style.display = 'none';
        backToTop.style.zIndex = '1040';
        
        document.body.appendChild(backToTop);

        window.addEventListener('scroll', () => {
            if (window.pageYOffset > 300) {
                backToTop.style.display = 'block';
            } else {
                backToTop.style.display = 'none';
            }
        });

        backToTop.addEventListener('click', () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    // 添加阅读时间估算
    estimateReadingTime() {
        const content = document.querySelector('.blog-content');
        if (!content) return;

        const text = content.innerText || content.textContent;
        const wordsPerMinute = 200; // 中文阅读速度
        const words = text.length;
        const readingTime = Math.ceil(words / wordsPerMinute);

        // 更新阅读时间显示
        const timeElement = document.querySelector('[data-reading-time]');
        if (timeElement) {
            timeElement.textContent = `${readingTime} 分钟阅读`;
        }
    }
}

// 初始化博客主题
const blogTheme = new BlogTheme();
