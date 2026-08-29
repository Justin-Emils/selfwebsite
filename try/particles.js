/**
 * 星辰宇宙粒子背景动画系统
 * 颜色匹配Three.js版本：粉紫色(220, 84, 190) -> 蓝紫色(67, 11, 245)
 */

class ParticleBackground {
  constructor(options = {}) {
    // 配置参数
    this.config = {
      particleCount: options.particleCount || 60,
      minSize: options.minSize || 2,
      maxSize: options.maxSize || 6,
      minDuration: options.minDuration || 8,
      maxDuration: options.maxDuration || 20,
      // 匹配Three.js星辰颜色：粉色到蓝紫色渐变
      colors: options.colors || [
        'rgba(220, 84, 190, 0.9)',   // 粉色 #dc54be
        'rgba(240, 147, 251, 0.8)',  // 亮粉 #f093fb
        'rgba(102, 126, 234, 0.7)',  // 中间紫蓝 #667eea
        'rgba(67, 11, 245, 0.8)',    // 蓝紫 #430bf5
        'rgba(192, 38, 211, 0.7)',   // 深粉紫 #c026d3
        'rgba(118, 75, 162, 0.6)'    // 中紫
      ]
    };

    this.container = null;
    this.particles = [];
    this.isInitialized = false;
  }

  /**
   * 初始化粒子系统
   */
  init() {
    if (this.isInitialized) return;

    // 创建粒子容器
    this.createContainer();

    // 生成粒子
    this.generateParticles();

    // 监听窗口大小变化
    window.addEventListener('resize', () => this.handleResize());

    this.isInitialized = true;
  }

  /**
   * 创建粒子容器
   */
  createContainer() {
    // 检查是否已存在
    let container = document.getElementById('particles-background');

    if (!container) {
      container = document.createElement('div');
      container.id = 'particles-background';
      document.body.insertBefore(container, document.body.firstChild);
    }

    this.container = container;
  }

  /**
   * 生成粒子
   */
  generateParticles() {
    if (!this.container) return;

    // 清空现有粒子
    this.container.innerHTML = '';
    this.particles = [];

    // 创建新粒子
    for (let i = 0; i < this.config.particleCount; i++) {
      this.createParticle();
    }
  }

  /**
   * 创建单个粒子
   */
  createParticle() {
    const particle = document.createElement('div');
    particle.className = 'particle';

    // 随机属性
    const size = this.randomBetween(this.config.minSize, this.config.maxSize);
    const startX = this.randomBetween(0, 100);
    const startY = this.randomBetween(0, 100);
    const endX = this.randomBetween(-50, 50);
    const duration = this.randomBetween(this.config.minDuration, this.config.maxDuration);
    const delay = this.randomBetween(0, duration);
    const color = this.config.colors[Math.floor(Math.random() * this.config.colors.length)];

    // 设置样式
    particle.style.cssText = `
      width: ${size}px;
      height: ${size}px;
      left: ${startX}vw;
      top: ${startY}vh;
      background: ${color};
      box-shadow: 0 0 ${size * 3}px ${color}, 0 0 ${size * 5}px ${color};
      --tx: ${endX}vw;
      animation: particleFloat ${duration}s linear ${delay}s infinite;
    `;

    this.container.appendChild(particle);
    this.particles.push(particle);
  }

  /**
   * 处理窗口大小变化
   */
  handleResize() {
    // 重新生成粒子以适应新的窗口大小
    clearTimeout(this.resizeTimeout);
    this.resizeTimeout = setTimeout(() => {
      this.generateParticles();
    }, 250);
  }

  /**
   * 生成随机数
   */
  randomBetween(min, max) {
    return Math.random() * (max - min) + min;
  }

  /**
   * 更新配置
   */
  updateConfig(newConfig) {
    this.config = { ...this.config, ...newConfig };
    this.generateParticles();
  }

  /**
   * 销毁粒子系统
   */
  destroy() {
    if (this.container && this.container.parentNode) {
      this.container.parentNode.removeChild(this.container);
    }
    this.particles = [];
    this.isInitialized = false;
    window.removeEventListener('resize', this.handleResize);
  }

  /**
   * 暂停动画
   */
  pause() {
    if (!this.container) return;
    this.particles.forEach(particle => {
      particle.style.animationPlayState = 'paused';
    });
  }

  /**
   * 恢复动画
   */
  resume() {
    if (!this.container) return;
    this.particles.forEach(particle => {
      particle.style.animationPlayState = 'running';
    });
  }
}

// 自动初始化（在 DOM 加载完成后）
if (typeof window !== 'undefined') {
  let particleSystem = null;

  const initParticles = () => {
    // 避免重复初始化
    if (particleSystem) return;

    particleSystem = new ParticleBackground({
      particleCount: 60,
      minSize: 2,
      maxSize: 6,
      minDuration: 8,
      maxDuration: 20
    });

    particleSystem.init();

    // 将实例暴露到全局，方便控制
    window.particleSystem = particleSystem;
  };

  // DOM 加载完成后初始化
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initParticles);
  } else {
    initParticles();
  }

  // 页面可见性变化时暂停/恢复动画（性能优化）
  document.addEventListener('visibilitychange', () => {
    if (particleSystem) {
      if (document.hidden) {
        particleSystem.pause();
      } else {
        particleSystem.resume();
      }
    }
  });
}

// 导出类（用于模块化环境）
if (typeof module !== 'undefined' && module.exports) {
  module.exports = ParticleBackground;
}
