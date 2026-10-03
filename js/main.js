/* ============================================
   Remi Portfolio 2.0 — Interactive JavaScript
   升级版交互脚本 - 高级背景动画 + 鼠标跟随
   ============================================ */

// 性能优化：检测低端设备，降低动画复杂度
const isLowEndDevice = () => {
    const cores = navigator.hardwareConcurrency || 4;
    const memory = navigator.deviceMemory || 4;
    return cores < 4 || memory < 4;
};

// 性能优化：页面可见性检测，隐藏时暂停动画
let canvasAnimationId = null;
let canvasAnimationRunning = true;

document.addEventListener('DOMContentLoaded', () => {
    initCanvas();
    initNavbar();
    initMobileMenu();
    initScrollAnimations();
    initCounterAnimation();
    initPortfolioFilter();
    initSmoothScroll();
    initContactForm();
    initCursorGlow();
    initJourneyCards();
    initWeChat();
    
    // 页面可见性变化时暂停/恢复动画
    document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
            canvasAnimationRunning = false;
        } else {
            canvasAnimationRunning = true;
        }
    });
});

/* ============================================
   Canvas Background Animation - 升级版
   粒子系统 + 鼠标跟随 + 联动光晕
   ============================================ */
function initCanvas() {
    const canvas = document.getElementById('bg-canvas');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    let particles = [];
    let mouseParticles = [];
    let mouse = { x: null, y: null, radius: 150 };
    let hue = 0;

    // 性能优化：检测低端设备，降低动画复杂度
    const lowEnd = isLowEndDevice();
    const maxParticles = lowEnd ? 50 : 100;
    const maxMouseParticles = lowEnd ? 30 : 60;
    const hueSpeed = lowEnd ? 0.8 : 1.5;

    const colors = {
        primary: '255, 140, 66',    // 暖橙色
        secondary: '255, 215, 0',   // 金色
        accent: '255, 107, 53'      // 橙红色
    };

    function resize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }

    resize();
    window.addEventListener('resize', resize);

    // 性能优化：低端设备减少鼠标粒子生成
    const mouseParticlesPerMove = lowEnd ? 1 : 2;
    const maxMouseParticlesGlobal = lowEnd ? 30 : 60;

    // 鼠标移动追踪
    window.addEventListener('mousemove', (e) => {
        mouse.x = e.x;
        mouse.y = e.y;

        // 创建鼠标跟随粒子
        for (let i = 0; i < mouseParticlesPerMove; i++) {
            mouseParticles.push(new MouseParticle(
                e.x + (Math.random() - 0.5) * 20,
                e.y + (Math.random() - 0.5) * 20,
                Math.random() * 2 + 1
            ));
        }

        // 限制粒子数量
        if (mouseParticles.length > maxMouseParticlesGlobal) {
            mouseParticles.splice(0, mouseParticles.length - maxMouseParticlesGlobal);
        }
    });

    // 粒子类
    class Particle {
        constructor() {
            this.reset();
        }

        reset() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.size = Math.random() * 2 + 1;
            this.speedX = (Math.random() - 0.5) * 0.5;
            this.speedY = (Math.random() - 0.5) * 0.5;
            this.hue = hue + Math.random() * 60;
            this.opacity = Math.random() * 0.3 + 0.15;
            this.pulseSpeed = 0.02 + Math.random() * 0.03;
            this.pulseOffset = Math.random() * Math.PI * 2;
        }

        update(time) {
            this.x += this.speedX;
            this.y += this.speedY;

            // 脉冲效果
            this.opacity = 0.15 + 0.15 * Math.sin(time * this.pulseSpeed + this.pulseOffset);

            // 边界处理
            if (this.x < 0) this.x = canvas.width;
            if (this.x > canvas.width) this.x = 0;
            if (this.y < 0) this.y = canvas.height;
            if (this.y > canvas.height) this.y = 0;

            // 鼠标互动 - 排斥效果
            if (mouse.x) {
                const dx = mouse.x - this.x;
                const dy = mouse.y - this.y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                
                if (dist < mouse.radius) {
                    const force = (mouse.radius - dist) / mouse.radius;
                    const angle = Math.atan2(dy, dx);
                    this.x -= Math.cos(angle) * force * 2;
                    this.y -= Math.sin(angle) * force * 2;
                }
            }
        }

        draw() {
            const gradient = ctx.createRadialGradient(
                this.x, this.y, 0,
                this.x, this.y, this.size * 3
            );
            gradient.addColorStop(0, `hsla(${this.hue}, 80%, 60%, ${this.opacity * 0.5})`);
            gradient.addColorStop(1, `hsla(${this.hue}, 80%, 60%, 0)`);
            
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size * 3, 0, Math.PI * 2);
            ctx.fillStyle = gradient;
            ctx.fill();
        }
    }

    // 鼠标跟随粒子类
    class MouseParticle {
        constructor(x, y, size) {
            this.x = x;
            this.y = y;
            this.size = size;
            this.life = 1;
            this.decay = 0.02 + Math.random() * 0.02;
            this.speedX = (Math.random() - 0.5) * 2;
            this.speedY = (Math.random() - 0.5) * 2;
            this.hue = hue + Math.random() * 60;
        }

        update() {
            this.x += this.speedX;
            this.y += this.speedY;
            this.life -= this.decay;
            this.size *= 0.95;
        }

        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fillStyle = `hsla(${this.hue}, 80%, 60%, ${this.life * 0.4})`;
            ctx.fill();
            
            // 外发光
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size * 1.5, 0, Math.PI * 2);
            ctx.fillStyle = `hsla(${this.hue}, 80%, 60%, ${this.life * 0.15})`;
            ctx.fill();
        }
    }

    // 初始化粒子
    for (let i = 0; i < maxParticles; i++) {
        particles.push(new Particle());
    }

    // 连线效果
    function connect() {
        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                const dx = particles[i].x - particles[j].x;
                const dy = particles[i].y - particles[j].y;
                const dist = Math.sqrt(dx * dx + dy * dy);

                if (dist < 150) {
                    const opacity = (1 - dist / 150) * 0.08;
                    ctx.beginPath();
                    ctx.strokeStyle = `hsla(${hue}, 80%, 60%, ${opacity})`;
                    ctx.lineWidth = 0.5;
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.stroke();
                }
            }
        }
    }

    // 鼠标光晕环
    function drawMouseGlow() {
        if (!mouse.x || !mouse.y) return;

        const gradient = ctx.createRadialGradient(
            mouse.x, mouse.y, 0,
            mouse.x, mouse.y, mouse.radius
        );
        gradient.addColorStop(0, `hsla(${hue}, 80%, 60%, 0.04)`);
        gradient.addColorStop(0.5, `hsla(${hue}, 80%, 60%, 0.015)`);
        gradient.addColorStop(1, `hsla(${hue}, 80%, 60%, 0)`);

        ctx.beginPath();
        ctx.arc(mouse.x, mouse.y, mouse.radius, 0, Math.PI * 2);
        ctx.fillStyle = gradient;
        ctx.fill();

        // 中心亮点
        ctx.beginPath();
        ctx.arc(mouse.x, mouse.y, 6, 0, Math.PI * 2);
        ctx.fillStyle = `hsla(${hue}, 90%, 70%, 0.4)`;
        ctx.fill();
    }

    // 动画循环
    let time = 0;
    function animate() {
        // 页面隐藏时暂停动画，节省资源
        if (!canvasAnimationRunning) {
            canvasAnimationId = requestAnimationFrame(animate);
            return;
        }

        // 轻微拖尾效果
        ctx.fillStyle = 'rgba(18, 18, 20, 0.2)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        time += 16;
        hue = (hue + hueSpeed) % 360;

        // 更新和绘制粒子
        particles.forEach(p => {
            p.update(time);
            p.draw();
        });

        // 更新和绘制鼠标粒子
        mouseParticles = mouseParticles.filter(p => p.life > 0);
        if (mouseParticles.length > maxMouseParticles) {
            mouseParticles.splice(0, mouseParticles.length - maxMouseParticles);
        }
        mouseParticles.forEach(p => {
            p.update();
            p.draw();
        });

        // 绘制连线
        connect();

        // 绘制鼠标光晕
        drawMouseGlow();

        canvasAnimationId = requestAnimationFrame(animate);
    }

    animate();
}

/* ============================================
   Navbar Scroll Effect
   ============================================ */
function initNavbar() {
    const nav = document.getElementById('nav');

    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            nav.classList.add('scrolled');
        } else {
            nav.classList.remove('scrolled');
        }
    });
}

/* ============================================
   Mobile Menu
   ============================================ */
function initMobileMenu() {
    const menuBtn = document.getElementById('menuBtn');
    const mobileMenu = document.getElementById('mobileMenu');
    const mobileLinks = document.querySelectorAll('.mobile-link');

    if (!menuBtn || !mobileMenu) return;

    menuBtn.addEventListener('click', () => {
        menuBtn.classList.toggle('active');
        mobileMenu.classList.toggle('active');
        document.body.style.overflow = mobileMenu.classList.contains('active') ? 'hidden' : '';
    });

    mobileLinks.forEach(link => {
        link.addEventListener('click', () => {
            menuBtn.classList.remove('active');
            mobileMenu.classList.remove('active');
            document.body.style.overflow = '';
        });
    });
}

/* ============================================
   Scroll Reveal Animations
   ============================================ */
function initScrollAnimations() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -100px 0px'
    });

    document.querySelectorAll('.fade-in-up').forEach(el => observer.observe(el));
}

/* ============================================
   Counter Animation
   ============================================ */
function initCounterAnimation() {
    const counters = document.querySelectorAll('.stat-number');
    const speed = 2000;
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const counter = entry.target;
                const target = +counter.getAttribute('data-count');
                const increment = target / (speed / 16);
                
                let current = 0;
                const update = () => {
                    current += increment;
                    if (current < target) {
                        counter.textContent = Math.floor(current);
                        requestAnimationFrame(update);
                    } else {
                        counter.textContent = target;
                    }
                };
                
                update();
                observer.unobserve(counter);
            }
        });
    }, { threshold: 0.5 });
    
    counters.forEach(counter => observer.observe(counter));
}

/* ============================================
   Portfolio Filter
   ============================================ */
function initPortfolioFilter() {
    const buttons = document.querySelectorAll('.filter-btn');
    const items = document.querySelectorAll('.work-item');

    buttons.forEach(btn => {
        btn.addEventListener('click', () => {
            buttons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const filter = btn.dataset.filter;

            items.forEach((item, index) => {
                const category = item.dataset.category;

                if (filter === 'all' || category === filter) {
                    item.style.display = 'block';
                    setTimeout(() => {
                        item.style.opacity = '1';
                        item.style.transform = 'translateY(0)';
                    }, 50);
                } else {
                    item.style.opacity = '0';
                    item.style.transform = 'translateY(20px)';
                    setTimeout(() => {
                        item.style.display = 'none';
                    }, 300);
                }
            });
        });
    });
}

/* ============================================
   Smooth Scroll
   ============================================ */
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href === '#') return;
            
            e.preventDefault();
            const target = document.querySelector(href);

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

/* ============================================
   Contact Form - Formspree
   ============================================ */
function initContactForm() {
    const form = document.getElementById('contactForm');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const btn = form.querySelector('.btn');
        const originalText = btn.innerHTML;
        const name = form.querySelector('#name').value.trim();
        const email = form.querySelector('#email').value.trim();
        const message = form.querySelector('#message').value.trim();

        if (!name || !email || !message) {
            alert('请填写完整信息哦～');
            return;
        }

        // 显示发送中状态
        btn.innerHTML = '<span>发送中...</span>';
        btn.disabled = true;

        try {
            // 使用 Formspree AJAX 提交
            const response = await fetch(form.action, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({
                    name: name,
                    email: email,
                    message: message
                })
            });

            if (response.ok) {
                // 发送成功
                btn.innerHTML = '<span>✓ 已发送</span><i class="fas fa-check"></i>';
                btn.classList.add('success');
                form.reset();

                setTimeout(() => {
                    btn.innerHTML = originalText;
                    btn.disabled = false;
                    btn.classList.remove('success');
                }, 3000);
            } else {
                // 发送失败
                const data = await response.json();
                console.error('发送失败:', data);
                btn.innerHTML = '<span>发送失败</span>';
                
                setTimeout(() => {
                    btn.innerHTML = originalText;
                    btn.disabled = false;
                }, 3000);
            }
        } catch (error) {
            console.error('网络错误:', error);
            btn.innerHTML = '<span>发送失败</span>';
            
            setTimeout(() => {
                btn.innerHTML = originalText;
                btn.disabled = false;
            }, 3000);
        }
    });
}

/* ============================================
   Cursor Glow Effect
   ============================================ */
function initCursorGlow() {
    const cursor = document.createElement('div');
    cursor.className = 'cursor-glow';
    document.body.appendChild(cursor);

    let mouseX = 0, mouseY = 0;
    let cursorX = 0, cursorY = 0;

    document.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
    });

    function animate() {
        const speed = 0.25;  // 光标跟随速度提升（0.15 → 0.25）
        cursorX += (mouseX - cursorX) * speed;
        cursorY += (mouseY - cursorY) * speed;

        cursor.style.left = cursorX + 'px';
        cursor.style.top = cursorY + 'px';

        requestAnimationFrame(animate);
    }

    animate();
}

/* ============================================
   Journey Cards - Footprint Animation
   ============================================ */
function initJourneyCards() {
    const cards = document.querySelectorAll('.journey-card');

    cards.forEach((card, index) => {
        // 添加序号标记
        card.setAttribute('data-step', index + 1);
    });
}

/* ============================================
   WeChat Popup & Copy
   ============================================ */
function initWeChat() {
    const wechatLink = document.querySelector('.wechat-link');
    const wechatPopup = document.getElementById('wechatPopup');
    
    console.log('===== initWeChat 调试 =====');
    console.log('wechatLink:', wechatLink);
    console.log('wechatPopup:', wechatPopup);
    
    if (!wechatLink) {
        console.error('错误：找不到 .wechat-link 元素');
        return;
    }
    if (!wechatPopup) {
        console.error('错误：找不到 #wechatPopup 元素');
        return;
    }
    
    console.log('微信元素存在，开始绑定事件');
    
    // 点击显示/隐藏弹窗
    wechatLink.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        console.log('微信图标被点击！');
        console.log('当前 popup classList:', wechatPopup.classList);
        wechatPopup.classList.toggle('show');
        console.log('切换后 popup classList:', wechatPopup.classList);
    });
    
    // 点击微信号复制
    const wechatId = wechatPopup.querySelector('.wechat-id');
    if (wechatId) {
        wechatId.addEventListener('click', () => {
            const text = wechatId.textContent;
            navigator.clipboard.writeText(text).then(() => {
                // 显示复制成功提示
                const originalText = wechatId.textContent;
                wechatId.textContent = '✓ 已复制';
                wechatId.style.background = 'var(--accent-glow)';
                wechatId.style.borderColor = 'var(--accent-border)';
                
                setTimeout(() => {
                    wechatId.textContent = originalText;
                    wechatId.style.background = '';
                    wechatId.style.borderColor = '';
                    wechatPopup.classList.remove('show');
                }, 1500);
            }).catch((err) => {
                console.error('复制失败:', err);
                // 复制失败，手动选择
                const range = document.createRange();
                range.selectNode(wechatId);
                window.getSelection().removeAllRanges();
                window.getSelection().addRange(range);
                document.execCommand('copy');
                window.getSelection().removeAllRanges();
                
                wechatId.textContent = '✓ 已复制';
                setTimeout(() => {
                    wechatId.textContent = 'Remi__LIN';
                    wechatPopup.classList.remove('show');
                }, 1500);
            });
        });
    }
    
    // 点击其他地方关闭弹窗
    document.addEventListener('click', () => {
        wechatPopup.classList.remove('show');
    });
    
    // 弹窗内点击不关闭
    wechatPopup.addEventListener('click', (e) => {
        e.stopPropagation();
    });
    
    console.log('===== initWeChat 完成 =====');
}
