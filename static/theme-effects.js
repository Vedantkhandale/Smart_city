// Nagpur Pulse — shared micro-interaction effects
// Click ripple on buttons/links + a small confetti helper used after a
// successful submit or login. Kept deliberately small: one responsibility,
// no dependency on page-specific markup.
(() => {
  function injectStyleOnce(id, css) {
    if (document.querySelector(`style[data-${id}]`)) return;
    const style = document.createElement('style');
    style.setAttribute(`data-${id}`, 'true');
    style.textContent = css;
    document.head.appendChild(style);
  }

  function createRipple(event, el) {
    const rect = el.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const ripple = document.createElement('span');
    ripple.className = 'np-ripple';
    ripple.style.width = ripple.style.height = size + 'px';
    ripple.style.left = (event.clientX - rect.left - size / 2) + 'px';
    ripple.style.top = (event.clientY - rect.top - size / 2) + 'px';

    injectStyleOnce('np-ripple', `
      .control-button, .submit, .mic-button, .admin-link, .tracker-form button { position: relative; overflow: hidden; }
      .np-ripple {
        position: absolute; border-radius: 50%; background: rgba(255,255,255,.35);
        transform: scale(0); animation: npRippleAnim .55s ease-out; pointer-events: none;
      }
      @keyframes npRippleAnim { to { transform: scale(4); opacity: 0; } }
    `);

    el.appendChild(ripple);
    setTimeout(() => ripple.remove(), 550);
  }

  document.addEventListener('click', (e) => {
    const el = e.target.closest('.control-button, .submit, .mic-button, .admin-link, .tracker-form button');
    if (el) createRipple(e, el);
  });

  // Small celebratory burst — call window.npCelebrate(x, y) after a
  // verified submit or a successful login.
  window.npCelebrate = function (x = window.innerWidth / 2, y = window.innerHeight / 2) {
    injectStyleOnce('np-confetti', `
      @keyframes npConfettiFall {
        to { transform: translate(var(--dx), var(--dy)); opacity: 0; }
      }
    `);
    const marks = ['✓', '✦', '●'];
    for (let i = 0; i < 16; i++) {
      const bit = document.createElement('div');
      bit.textContent = marks[i % marks.length];
      const angle = (Math.PI * 2 * i) / 16;
      const dist = 60 + Math.random() * 90;
      bit.style.cssText = `
        position:fixed; left:${x}px; top:${y}px; pointer-events:none; z-index:9999;
        font-size:${10 + Math.random() * 10}px; color:#FF5500;
        animation: npConfettiFall 900ms ease-out forwards;
      `;
      bit.style.setProperty('--dx', `${Math.cos(angle) * dist}px`);
      bit.style.setProperty('--dy', `${Math.sin(angle) * dist + 40}px`);
      document.body.appendChild(bit);
      setTimeout(() => bit.remove(), 900);
    }
  };
})();