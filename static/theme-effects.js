// 🎨 NAGPUR PULSE - ENHANCED INTERACTIVE EFFECTS

document.addEventListener('DOMContentLoaded', () => {
  
  // ✨ Smooth scroll behavior
  document.documentElement.style.scrollBehavior = 'smooth';
  
  // 🎯 Add glow effect on click
  document.addEventListener('click', (e) => {
    if (e.target.tagName === 'BUTTON' || e.target.closest('button') || 
        e.target.tagName === 'A' || e.target.closest('.control-button')) {
      createClickGlow(e.pageX, e.pageY);
    }
  });
  
  function createClickGlow(x, y) {
    const glow = document.createElement('div');
    glow.style.position = 'fixed';
    glow.style.left = x + 'px';
    glow.style.top = y + 'px';
    glow.style.width = '20px';
    glow.style.height = '20px';
    glow.style.borderRadius = '50%';
    glow.style.pointerEvents = 'none';
    glow.style.background = 'radial-gradient(circle, rgba(89, 243, 209, 0.6), transparent)';
    glow.style.transform = 'translate(-50%, -50%)';
    glow.style.animation = 'glowExpand 0.8s ease-out forwards';
    
    // Add animation
    if (!document.querySelector('style[data-glow]')) {
      const style = document.createElement('style');
      style.setAttribute('data-glow', 'true');
      style.textContent = `
        @keyframes glowExpand {
          from {
            width: 20px;
            height: 20px;
            opacity: 1;
          }
          to {
            width: 100px;
            height: 100px;
            opacity: 0;
          }
        }
      `;
      document.head.appendChild(style);
    }
    
    document.body.appendChild(glow);
    setTimeout(() => glow.remove(), 800);
  }
  
  // 🌊 Parallax effect on scroll
  const parallaxElements = document.querySelectorAll('[data-parallax]');
  if (parallaxElements.length > 0) {
    window.addEventListener('scroll', () => {
      parallaxElements.forEach(el => {
        const scrollPos = window.scrollY;
        const speed = el.getAttribute('data-parallax') || 0.5;
        el.style.transform = `translateY(${scrollPos * speed}px)`;
      });
    });
  }
  
  // 📍 Add hover ripple effect
  const buttons = document.querySelectorAll('button, .control-button, .admin-link');
  buttons.forEach(button => {
    button.addEventListener('mouseenter', (e) => {
      if (!button.hasAttribute('data-ripple-setup')) {
        button.setAttribute('data-ripple-setup', 'true');
        button.addEventListener('click', createRipple);
      }
    });
  });
  
  function createRipple(event) {
    const button = event.currentTarget;
    const rect = button.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;
    
    const ripple = document.createElement('span');
    ripple.style.width = ripple.style.height = size + 'px';
    ripple.style.left = x + 'px';
    ripple.style.top = y + 'px';
    ripple.className = 'ripple';
    
    // Add ripple style if not exists
    if (!document.querySelector('style[data-ripple]')) {
      const style = document.createElement('style');
      style.setAttribute('data-ripple', 'true');
      style.textContent = `
        button, .control-button {
          position: relative;
          overflow: hidden;
        }
        
        .ripple {
          position: absolute;
          border-radius: 50%;
          background: rgba(255, 255, 255, 0.5);
          transform: scale(0);
          animation: rippleAnimation 0.6s ease-out;
          pointer-events: none;
        }
        
        @keyframes rippleAnimation {
          to {
            transform: scale(4);
            opacity: 0;
          }
        }
      `;
      document.head.appendChild(style);
    }
    
    button.appendChild(ripple);
    setTimeout(() => ripple.remove(), 600);
  }
  
  // 🎨 Animated counters
  function animateCounter(element, target, duration = 2000) {
    const start = parseInt(element.textContent) || 0;
    const increment = (target - start) / (duration / 16);
    let current = start;
    
    const counter = setInterval(() => {
      current += increment;
      if (current >= target) {
        element.textContent = target;
        clearInterval(counter);
      } else {
        element.textContent = Math.floor(current);
      }
    }, 16);
  }
  
  // Observe elements for animation
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.animationPlayState = 'running';
        
        // Animate counters
        if (entry.target.querySelector('strong')) {
          const strong = entry.target.querySelector('strong');
          const text = strong.textContent;
          if (/^\d+/.test(text)) {
            const num = parseInt(text);
            animateCounter(strong, num);
          }
        }
      }
    });
  });
  
  document.querySelectorAll('.metric, .stat, .risk-item').forEach(el => {
    observer.observe(el);
    el.style.animationPlayState = 'paused';
  });
  
  // 🌙 Dark mode toggle (optional)
  const addDarkModeToggle = () => {
    const toggle = document.createElement('button');
    toggle.innerHTML = '🌙';
    toggle.className = 'theme-toggle';
    toggle.style.cssText = `
      position: fixed;
      bottom: 30px;
      right: 30px;
      width: 50px;
      height: 50px;
      border-radius: 50%;
      border: 2px solid rgba(89, 243, 209, 0.3);
      background: rgba(12, 29, 45, 0.9);
      color: var(--aqua);
      cursor: pointer;
      font-size: 20px;
      z-index: 1000;
      transition: all 0.3s ease;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 4px 20px rgba(89, 243, 209, 0.2);
    `;
    
    toggle.addEventListener('mouseenter', () => {
      toggle.style.transform = 'scale(1.1)';
      toggle.style.boxShadow = '0 6px 30px rgba(89, 243, 209, 0.4)';
    });
    
    toggle.addEventListener('mouseleave', () => {
      toggle.style.transform = 'scale(1)';
      toggle.style.boxShadow = '0 4px 20px rgba(89, 243, 209, 0.2)';
    });
    
    toggle.addEventListener('click', () => {
      document.body.classList.toggle('light-mode');
      toggle.innerHTML = document.body.classList.contains('light-mode') ? '☀️' : '🌙';
    });
    
    document.body.appendChild(toggle);
  };
  
  // Optional: uncomment to enable theme toggle
  // addDarkModeToggle();
  
  // 💫 Add sparkle effect on input focus
  const inputs = document.querySelectorAll('input[type="text"], input[type="number"], textarea, select');
  inputs.forEach(input => {
    input.addEventListener('focus', (e) => {
      createSparkles(e.target);
    });
  });
  
  function createSparkles(element) {
    const rect = element.getBoundingClientRect();
    for (let i = 0; i < 3; i++) {
      const sparkle = document.createElement('div');
      sparkle.style.position = 'fixed';
      sparkle.style.left = (rect.left + Math.random() * rect.width) + 'px';
      sparkle.style.top = (rect.top + Math.random() * rect.height) + 'px';
      sparkle.style.width = '4px';
      sparkle.style.height = '4px';
      sparkle.style.borderRadius = '50%';
      sparkle.style.background = 'var(--aqua)';
      sparkle.style.pointerEvents = 'none';
      sparkle.style.opacity = '1';
      sparkle.style.animation = 'sparkleFloat 0.8s ease-out forwards';
      
      if (!document.querySelector('style[data-sparkle]')) {
        const style = document.createElement('style');
        style.setAttribute('data-sparkle', 'true');
        style.textContent = `
          @keyframes sparkleFloat {
            to {
              transform: translateY(-30px);
              opacity: 0;
            }
          }
        `;
        document.head.appendChild(style);
      }
      
      document.body.appendChild(sparkle);
      setTimeout(() => sparkle.remove(), 800);
    }
  }
  
  // 🎯 Smooth link navigation
  document.querySelectorAll('a[href*="#"]').forEach(link => {
    link.addEventListener('click', (e) => {
      const target = document.querySelector(link.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });
  
  // 📊 Add loading animation helper
  window.showLoading = function(element, show = true) {
    if (show) {
      element.classList.add('loading');
    } else {
      element.classList.remove('loading');
    }
  };
  
  // 🎊 Celebration confetti on success (optional)
  window.celebrate = function(x = window.innerWidth / 2, y = window.innerHeight / 2) {
    for (let i = 0; i < 30; i++) {
      const confetti = document.createElement('div');
      const emoji = ['✓', '🎉', '⭐', '💫', '✨'][Math.floor(Math.random() * 5)];
      confetti.innerHTML = emoji;
      confetti.style.position = 'fixed';
      confetti.style.left = x + 'px';
      confetti.style.top = y + 'px';
      confetti.style.pointerEvents = 'none';
      confetti.style.fontSize = Math.random() * 20 + 10 + 'px';
      confetti.style.opacity = '1';
      confetti.style.animation = 'confettiFall 2s ease-out forwards';
      confetti.style.zIndex = '9999';
      
      const angle = (Math.PI * 2 * i) / 30;
      confetti.style.setProperty('--angle', angle);
      confetti.style.setProperty('--distance', Math.random() * 150 + 50);
      
      if (!document.querySelector('style[data-confetti]')) {
        const style = document.createElement('style');
        style.setAttribute('data-confetti', 'true');
        style.textContent = `
          @keyframes confettiFall {
            to {
              transform: translate(
                calc(cos(var(--angle)) * var(--distance)),
                calc(sin(var(--angle)) * var(--distance) + 100px)
              );
              opacity: 0;
            }
          }
        `;
        document.head.appendChild(style);
      }
      
      document.body.appendChild(confetti);
      setTimeout(() => confetti.remove(), 2000);
    }
  };
  
  console.log('🎨 Nagpur Pulse Enhanced Effects Loaded!');
});
