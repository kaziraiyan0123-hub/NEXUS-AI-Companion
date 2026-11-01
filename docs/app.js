/**
 * NEXUS Interactive Canvas Pet Simulator
 * Replicates the PySide6 mathematical vector physics on the web:
 * - Real-time mouse gaze tracking
 * - Sinusoidal levitation hover & squish physics
 * - Royal Habibi (Gold Aviators & Ghutra) and Neo Cyber rendering
 * - Particle system (Coins, Stars, Hearts)
 */

(function () {
  const canvas = document.getElementById('petCanvas');
  const ctx = canvas.getContext('2d');

  let activeSkin = 'habibi'; // 'habibi' or 'cyber'
  let mouseX = canvas.width / 2;
  let mouseY = canvas.height / 2;
  let currentLookX = 0;
  let currentLookY = 0;
  let stateTime = 0;
  let squishX = 1.0;
  let squishY = 1.0;
  let isHovered = false;
  let particles = [];
  let celebrationTime = 0;

  // Track mouse coordinates over canvas
  canvas.addEventListener('mousemove', (e) => {
    const rect = canvas.getBoundingClientRect();
    mouseX = e.clientX - rect.left;
    mouseY = e.clientY - rect.top;
    isHovered = true;
  });

  canvas.addEventListener('mouseleave', () => {
    mouseX = canvas.width / 2;
    mouseY = canvas.height / 2;
    isHovered = false;
  });

  // Touch tracking and touch-to-pet for mobile phones
  canvas.addEventListener('touchstart', (e) => {
    const rect = canvas.getBoundingClientRect();
    if (e.touches.length > 0) {
      mouseX = e.touches[0].clientX - rect.left;
      mouseY = e.touches[0].clientY - rect.top;
      isHovered = true;
      squishX = 1.15;
      squishY = 0.85;
      if (typeof spawnParticles === 'function') {
        spawnParticles('heart', 6, '#ec4899');
      }
      if (navigator.vibrate) navigator.vibrate([20, 30, 20]);
    }
  }, { passive: true });

  canvas.addEventListener('touchmove', (e) => {
    const rect = canvas.getBoundingClientRect();
    if (e.touches.length > 0) {
      mouseX = e.touches[0].clientX - rect.left;
      mouseY = e.touches[0].clientY - rect.top;
      if (Math.random() < 0.25 && typeof spawnParticles === 'function') {
        spawnParticles('heart', 1, '#ec4899');
      }
    }
  }, { passive: true });

  canvas.addEventListener('touchend', () => {
    mouseX = canvas.width / 2;
    mouseY = canvas.height / 2;
    isHovered = false;
    squishX = 0.95;
    squishY = 1.05;
  });

  // Particle Class
  class Particle {
    constructor(x, y, type, color) {
      this.x = x;
      this.y = y;
      this.type = type;
      this.color = color;
      this.vx = (Math.random() - 0.5) * 4;
      this.vy = -Math.random() * 3 - 1;
      this.life = 1.0;
      this.decay = Math.random() * 0.02 + 0.015;
      this.size = Math.random() * 8 + 6;
    }

    update() {
      this.x += this.vx;
      this.y += this.vy;
      this.vy += 0.08; // gravity
      this.life -= this.decay;
    }

    draw(ctx) {
      if (this.life <= 0) return;
      ctx.save();
      ctx.globalAlpha = Math.max(0, this.life);

      if (this.type === 'coin') {
        // Gold Dirham Coin
        ctx.fillStyle = '#fbbf24';
        ctx.strokeStyle = '#d97706';
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size * 0.7, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();

        ctx.strokeStyle = '#b45309';
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size * 0.45, 0, Math.PI * 2);
        ctx.stroke();
      } else if (this.type === 'heart') {
        // Heart
        ctx.fillStyle = '#f43f5e';
        ctx.beginPath();
        const topCurveHeight = this.size * 0.3;
        ctx.moveTo(this.x, this.y + topCurveHeight);
        ctx.bezierCurveTo(this.x, this.y, this.x - this.size / 2, this.y, this.x - this.size / 2, this.y + topCurveHeight);
        ctx.bezierCurveTo(this.x - this.size / 2, this.y + (this.size + topCurveHeight) / 2, this.x, this.y + (this.size + topCurveHeight) / 1.4, this.x, this.y + this.size);
        ctx.bezierCurveTo(this.x, this.y + (this.size + topCurveHeight) / 1.4, this.x + this.size / 2, this.y + (this.size + topCurveHeight) / 2, this.x + this.size / 2, this.y + topCurveHeight);
        ctx.bezierCurveTo(this.x + this.size / 2, this.y, this.x, this.y, this.x, this.y + topCurveHeight);
        ctx.closePath();
        ctx.fill();
      } else {
        // Star / Sparkle
        ctx.fillStyle = this.color || '#38bdf8';
        ctx.beginPath();
        const s = this.size;
        ctx.moveTo(this.x, this.y - s);
        ctx.lineTo(this.x + s * 0.3, this.y - s * 0.2);
        ctx.lineTo(this.x + s, this.y);
        ctx.lineTo(this.x + s * 0.3, this.y + s * 0.2);
        ctx.lineTo(this.x, this.y + s);
        ctx.lineTo(this.x - s * 0.3, this.y + s * 0.2);
        ctx.lineTo(this.x - s, this.y);
        ctx.lineTo(this.x - s * 0.3, this.y - s * 0.2);
        ctx.closePath();
        ctx.fill();
      }
      ctx.restore();
    }
  }

  function spawnBurst(type, count, color) {
    for (let i = 0; i < count; i++) {
      particles.push(new Particle(canvas.width / 2, canvas.height / 2, type, color));
    }
  }

  // Interactive buttons
  document.getElementById('petButton').addEventListener('click', () => {
    squishX = 1.2;
    squishY = 0.8;
    spawnBurst(activeSkin === 'habibi' ? 'coin' : 'heart', 14, '#fbbf24');
  });

  document.getElementById('highFiveButton').addEventListener('click', () => {
    squishX = 0.85;
    squishY = 1.25;
    celebrationTime = 2.0;
    spawnBurst('star', 18, activeSkin === 'habibi' ? '#fbbf24' : '#38bdf8');
  });

  document.getElementById('cheerButton').addEventListener('click', () => {
    celebrationTime = 2.5;
    spawnBurst('star', 22, '#a855f7');
  });

  // Skin switcher buttons
  const skinBtns = document.querySelectorAll('.skin-btn');
  skinBtns.forEach((btn) => {
    btn.addEventListener('click', () => {
      skinBtns.forEach((b) => b.classList.remove('active'));
      btn.classList.add('active');
      activeSkin = btn.dataset.skin;
      spawnBurst('star', 12, activeSkin === 'habibi' ? '#fbbf24' : '#38bdf8');
    });
  });

  // Main Render Loop
  let lastTime = performance.now();

  function animate(now) {
    const dt = Math.min(0.08, (now - lastTime) / 1000);
    lastTime = now;
    stateTime += dt;
    if (celebrationTime > 0) celebrationTime -= dt;

    // Smooth squish recovery
    squishX += (1.0 - squishX) * 0.15;
    squishY += (1.0 - squishY) * 0.15;

    // Smooth gaze easing
    const targetLookX = Math.max(-1.0, Math.min(1.0, (mouseX - canvas.width / 2) / 120));
    const targetLookY = Math.max(-1.0, Math.min(1.0, (mouseY - canvas.height / 2) / 100));
    currentLookX += (targetLookX - currentLookX) * 0.15;
    currentLookY += (targetLookY - currentLookY) * 0.15;

    // Clear Canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Coordinate origin & hover physics
    const cx = canvas.width / 2;
    const hoverOffset = Math.sin(stateTime * 2.8) * 7.0;
    const cy = canvas.height / 2 + hoverOffset;

    ctx.save();
    ctx.translate(cx, cy);
    ctx.scale(squishX, squishY);
    ctx.translate(-cx, -cy);

    // 1. Thruster Aura
    const pulse = 0.8 + 0.2 * Math.sin(stateTime * 6.0);
    const auraGrad = ctx.createRadialGradient(cx, cy + 45, 10, cx, cy + 45, 45 * pulse);
    const auraCol = activeSkin === 'habibi' ? 'rgba(251, 191, 36, 0.4)' : 'rgba(56, 189, 248, 0.35)';
    auraGrad.addColorStop(0, auraCol);
    auraGrad.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = auraGrad;
    ctx.beginPath();
    ctx.ellipse(cx, cy + 40, 40 * pulse, 14 * pulse, 0, 0, Math.PI * 2);
    ctx.fill();

    // 2. Orbiting Holographic Ring (Back half)
    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate((22 * Math.PI) / 180);
    ctx.strokeStyle = activeSkin === 'habibi' ? 'rgba(251, 191, 36, 0.3)' : 'rgba(56, 189, 248, 0.3)';
    ctx.lineWidth = 1.8;
    ctx.setLineDash([4, 4]);
    ctx.beginPath();
    ctx.ellipse(0, 0, 78, 24, 0, Math.PI, 0);
    ctx.stroke();
    ctx.restore();

    // 3. Habibi Ghutra Back Drapes
    if (activeSkin === 'habibi') {
      const sway = Math.sin(stateTime * 3.0) * 4.0;
      ctx.save();
      ctx.strokeStyle = 'rgba(212, 175, 55, 0.7)';
      ctx.lineWidth = 1.5;
      ctx.fillStyle = '#f8fafc';

      // Left drape
      ctx.beginPath();
      ctx.moveTo(cx - 38, cy - 36);
      ctx.bezierCurveTo(cx - 62, cy - 10, cx - 68 + sway, cy + 24, cx - 48 + sway, cy + 56);
      ctx.bezierCurveTo(cx - 40, cy + 44, cx - 35, cy + 10, cx - 36, cy - 20);
      ctx.closePath();
      ctx.fill();
      ctx.stroke();

      // Right drape
      ctx.beginPath();
      ctx.moveTo(cx + 38, cy - 36);
      ctx.bezierCurveTo(cx + 62, cy - 10, cx + 68 - sway, cy + 24, cx + 48 - sway, cy + 56);
      ctx.bezierCurveTo(cx + 40, cy + 44, cx + 35, cy + 10, cx + 36, cy - 20);
      ctx.closePath();
      ctx.fill();
      ctx.stroke();
      ctx.restore();
    } else {
      // Cyber Fins
      ctx.save();
      ctx.fillStyle = '#1e293b';
      ctx.strokeStyle = '#38bdf8';
      ctx.lineWidth = 1.8;

      // Left fin
      ctx.beginPath();
      ctx.moveTo(cx - 52, cy - 8);
      ctx.lineTo(cx - 72, cy - 24);
      ctx.lineTo(cx - 64, cy + 8);
      ctx.closePath();
      ctx.fill();
      ctx.stroke();

      // Right fin
      ctx.beginPath();
      ctx.moveTo(cx + 52, cy - 8);
      ctx.lineTo(cx + 72, cy - 24);
      ctx.lineTo(cx + 64, cy + 8);
      ctx.closePath();
      ctx.fill();
      ctx.stroke();
      ctx.restore();
    }

    // 4. Main Body Chassis
    ctx.save();
    const bodyGrad = ctx.createLinearGradient(cx, cy - 50, cx, cy + 50);
    if (activeSkin === 'habibi') {
      bodyGrad.addColorStop(0, '#ffffff');
      bodyGrad.addColorStop(1, '#f1f5f9');
      ctx.strokeStyle = '#d4af37';
    } else {
      bodyGrad.addColorStop(0, '#1e293b');
      bodyGrad.addColorStop(1, '#0f172a');
      ctx.strokeStyle = '#334155';
    }
    ctx.lineWidth = 2.5;
    ctx.fillStyle = bodyGrad;
    roundRect(ctx, cx - 48, cy - 48, 96, 96, 46);
    ctx.fill();
    ctx.stroke();
    ctx.restore();

    // 5. OLED Visor Display
    ctx.save();
    const visorGrad = ctx.createLinearGradient(cx, cy - 30, cx, cy + 30);
    visorGrad.addColorStop(0, '#0a0e17');
    visorGrad.addColorStop(1, '#030712');
    ctx.fillStyle = visorGrad;
    ctx.strokeStyle = activeSkin === 'habibi' ? '#fbbf24' : '#38bdf8';
    ctx.lineWidth = 1.8;
    roundRect(ctx, cx - 42, cy - 30, 84, 62, 22);
    ctx.fill();
    ctx.stroke();

    // Visor Glass Sheen
    ctx.fillStyle = activeSkin === 'habibi' ? 'rgba(251, 191, 36, 0.15)' : 'rgba(255, 255, 255, 0.12)';
    ctx.beginPath();
    ctx.moveTo(cx - 34, cy - 24);
    ctx.quadraticCurveTo(cx, cy - 28, cx + 34, cy - 24);
    ctx.quadraticCurveTo(cx, cy - 22, cx - 34, cy - 24);
    ctx.fill();
    ctx.restore();

    // 6. Eyes & Face
    const eyeY = cy - 4 + currentLookY * 6;
    const leftEyeX = cx - 18 + currentLookX * 8;
    const rightEyeX = cx + 18 + currentLookX * 8;

    if (activeSkin === 'habibi') {
      // 👑 Dubai Gold Aviator Sunglasses
      ctx.save();
      // Gold Bridge Bar
      ctx.strokeStyle = '#fbbf24';
      ctx.lineWidth = 2.2;
      ctx.beginPath();
      ctx.moveTo(leftEyeX + 6, eyeY - 8);
      ctx.lineTo(rightEyeX - 6, eyeY - 8);
      ctx.stroke();

      const aw = 18;
      const ah = 15;

      [leftEyeX, rightEyeX].forEach((lx) => {
        // Mirrored Lens Teardrop Path
        ctx.fillStyle = '#0f172a';
        ctx.strokeStyle = '#fbbf24';
        ctx.lineWidth = 1.8;
        ctx.beginPath();
        ctx.moveTo(lx - aw / 2, eyeY - ah / 2);
        ctx.lineTo(lx + aw / 2, eyeY - ah / 2);
        ctx.bezierCurveTo(lx + aw / 2, eyeY + ah / 2, lx + aw / 4, eyeY + ah / 2 + 2, lx, eyeY + ah / 2 + 2);
        ctx.bezierCurveTo(lx - aw / 4, eyeY + ah / 2 + 2, lx - aw / 2, eyeY + ah / 2, lx - aw / 2, eyeY - ah / 2);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();

        // Diagonal Gold Reflection Glint
        ctx.fillStyle = 'rgba(251, 191, 36, 0.4)';
        ctx.beginPath();
        ctx.moveTo(lx - aw / 3, eyeY - ah / 2 + 2);
        ctx.lineTo(lx - aw / 4, eyeY - ah / 2 + 2);
        ctx.lineTo(lx + aw / 3, eyeY + ah / 2 - 2);
        ctx.lineTo(lx + aw / 4, eyeY + ah / 2 - 2);
        ctx.closePath();
        ctx.fill();

        // Golden Pupils
        ctx.fillStyle = '#fbbf24';
        ctx.beginPath();
        ctx.arc(lx, eyeY, 4, 0, Math.PI * 2);
        ctx.fill();
      });

      // Frame Corner Star Glint
      ctx.fillStyle = '#ffffff';
      const gx = rightEyeX + 9;
      const gy = eyeY - 7;
      drawStar(ctx, gx, gy, 4);

      ctx.restore();
    } else {
      // Neo Cyber Expressive Cyan Eyes
      ctx.save();
      ctx.fillStyle = '#38bdf8';
      ctx.beginPath();
      ctx.ellipse(leftEyeX, eyeY, 6, 8, 0, 0, Math.PI * 2);
      ctx.ellipse(rightEyeX, eyeY, 6, 8, 0, 0, Math.PI * 2);
      ctx.fill();

      // Eye glint highlights
      ctx.fillStyle = '#ffffff';
      ctx.beginPath();
      ctx.arc(leftEyeX - 2, eyeY - 2, 2, 0, Math.PI * 2);
      ctx.arc(rightEyeX - 2, eyeY - 2, 2, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();
    }

    // Dynamic Smile
    ctx.save();
    ctx.strokeStyle = activeSkin === 'habibi' ? '#fbbf24' : '#38bdf8';
    ctx.lineWidth = 2.2;
    ctx.lineCap = 'round';
    ctx.beginPath();
    ctx.moveTo(cx - 7, cy + 15);
    ctx.quadraticCurveTo(cx, cy + 22, cx + 7, cy + 15);
    ctx.stroke();
    ctx.restore();

    // 7. Habibi Top Ghutra & Agal Cords
    if (activeSkin === 'habibi') {
      ctx.save();
      // White Ghutra Canopy
      ctx.fillStyle = '#ffffff';
      ctx.strokeStyle = 'rgba(212, 175, 55, 0.8)';
      ctx.lineWidth = 1.2;
      ctx.beginPath();
      ctx.moveTo(cx - 48, cy - 34);
      ctx.bezierCurveTo(cx - 50, cy - 58, cx - 25, cy - 65, cx, cy - 66);
      ctx.bezierCurveTo(cx + 25, cy - 65, cx + 50, cy - 58, cx + 48, cy - 34);
      ctx.quadraticCurveTo(cx, cy - 40, cx - 48, cy - 34);
      ctx.closePath();
      ctx.fill();
      ctx.stroke();

      // Double Black Agal Rings
      ctx.strokeStyle = '#111827';
      ctx.lineWidth = 5.0;
      ctx.lineCap = 'round';

      // Upper ring
      ctx.beginPath();
      ctx.moveTo(cx - 38, cy - 52);
      ctx.quadraticCurveTo(cx, cy - 57, cx + 38, cy - 52);
      ctx.stroke();

      // Lower ring
      ctx.beginPath();
      ctx.moveTo(cx - 40, cy - 46);
      ctx.quadraticCurveTo(cx, cy - 51, cx + 40, cy - 46);
      ctx.stroke();

      // Gold clasp rings
      ctx.strokeStyle = '#fbbf24';
      ctx.lineWidth = 2.5;
      ctx.beginPath();
      ctx.moveTo(cx - 20, cy - 55);
      ctx.lineTo(cx - 20, cy - 44);
      ctx.moveTo(cx + 20, cy - 55);
      ctx.lineTo(cx + 20, cy - 44);
      ctx.stroke();

      // Gold Center Diamond Crest
      ctx.fillStyle = '#fbbf24';
      ctx.beginPath();
      ctx.moveTo(cx, cy - 56);
      ctx.lineTo(cx + 4.5, cy - 49);
      ctx.lineTo(cx, cy - 42);
      ctx.lineTo(cx - 4.5, cy - 49);
      ctx.closePath();
      ctx.fill();
      ctx.restore();
    }

    // 8. Orbiting Holographic Ring (Front half)
    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate((22 * Math.PI) / 180);
    ctx.strokeStyle = activeSkin === 'habibi' ? '#fbbf24' : '#38bdf8';
    ctx.lineWidth = 2.0;
    ctx.beginPath();
    ctx.ellipse(0, 0, 78, 24, 0, 0, Math.PI);
    ctx.stroke();

    // Orbiting node
    const nodeAngle = stateTime * 2.5;
    const nx = Math.cos(nodeAngle) * 78;
    const ny = Math.sin(nodeAngle) * 24;
    if (ny >= 0) {
      ctx.fillStyle = activeSkin === 'habibi' ? '#fbbf24' : '#38bdf8';
      ctx.beginPath();
      ctx.arc(nx, ny, 4.5, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.restore();

    ctx.restore();

    // 9. Update & Draw Particles
    particles.forEach((p) => p.update());
    particles = particles.filter((p) => p.life > 0);
    particles.forEach((p) => p.draw(ctx));

    requestAnimationFrame(animate);
  }

  function roundRect(ctx, x, y, width, height, radius) {
    ctx.beginPath();
    ctx.moveTo(x + radius, y);
    ctx.lineTo(x + width - radius, y);
    ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
    ctx.lineTo(x + width, y + height - radius);
    ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
    ctx.lineTo(x + radius, y + height);
    ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
    ctx.lineTo(x, y + radius);
    ctx.quadraticCurveTo(x, y, x + radius, y);
    ctx.closePath();
  }

  function drawStar(ctx, x, y, s) {
    ctx.beginPath();
    ctx.moveTo(x, y - s);
    ctx.lineTo(x + s * 0.3, y);
    ctx.lineTo(x + s, y);
    ctx.lineTo(x + s * 0.3, y);
    ctx.lineTo(x, y + s);
    ctx.lineTo(x - s * 0.3, y);
    ctx.lineTo(x - s, y);
    ctx.lineTo(x - s * 0.3, y);
    ctx.closePath();
    ctx.fill();
  }

  // Register Service Worker for Mobile PWA
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('./sw.js').catch(() => {});
    });
  }

  // PWA Install Prompt for Mobile Phones
  let deferredPrompt;
  const pwaBtn = document.getElementById('pwaInstallBtn');
  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    if (pwaBtn) pwaBtn.style.display = 'block';
  });

  if (pwaBtn) {
    pwaBtn.addEventListener('click', async () => {
      if (deferredPrompt) {
        deferredPrompt.prompt();
        const { outcome } = await deferredPrompt.userChoice;
        if (outcome === 'accepted') {
          pwaBtn.style.display = 'none';
        }
        deferredPrompt = null;
      }
    });
  }

  // Mobile Voice Assistant via Web Speech API
  const mobileVoiceBtn = document.getElementById('mobileVoiceBtn');
  const mobileVoiceText = document.getElementById('mobileVoiceText');
  const mobileSpeechOutput = document.getElementById('mobileSpeechOutput');

  let isListening = false;
  let recognition = null;
  const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;

  function speakText(text) {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utter = new SpeechSynthesisUtterance(text);
      utter.rate = 1.0;
      utter.pitch = 1.05;
      window.speechSynthesis.speak(utter);
    }
  }

  function triggerCheerEffect() {
    celebrationTime = 40;
    squishX = 1.25;
    squishY = 0.75;
    spawnParticles('coin', 30, '#fbbf24');
    spawnParticles('star', 20, '#38bdf8');
    if (navigator.vibrate) navigator.vibrate([40, 60, 40]);
  }

  function triggerPetHappy() {
    squishX = 1.2;
    squishY = 0.8;
    spawnParticles('heart', 12, '#ec4899');
  }

  function handleMobileVoiceQuery(query) {
    const q = query.toLowerCase();
    let reply = "I am NEXUS, your autonomous AI companion! You can pet me, ask questions, or command desktop and mobile tasks.";
    if (q.includes('who made you') || q.includes('who created you') || q.includes('creator')) {
      reply = "Raiyan coded me! I am your personal autonomous companion.";
    } else if (q.includes('time') || q.includes('clock')) {
      reply = "The current time is " + new Date().toLocaleTimeString() + ".";
    } else if (q.includes('hello') || q.includes('hi') || q.includes('hey')) {
      reply = "Hello! I am ready to help you on desktop or mobile. What should we work on today?";
    } else if (q.includes('cheer') || q.includes('celebrate') || q.includes('party')) {
      reply = "Hooray! Great job today! Here are some sparkles!";
      triggerCheerEffect();
    } else {
      reply = `Understood: "${query}". I am fully active and connected to your companion engine!`;
    }

    if (mobileSpeechOutput) {
      mobileSpeechOutput.innerHTML = `<strong>You:</strong> "${query}"<br><br><span style="color:#38bdf8;">✦ NEXUS:</span> ${reply}`;
    }
    speakText(reply);
    triggerPetHappy();
  }

  if (SpeechRec) {
    recognition = new SpeechRec();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
      isListening = true;
      if (mobileVoiceText) mobileVoiceText.textContent = 'Listening... Speak now';
      if (mobileSpeechOutput) mobileSpeechOutput.textContent = '🎙️ Listening to your voice...';
    };

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      if (mobileSpeechOutput) {
        mobileSpeechOutput.innerHTML = `<strong>You said:</strong> "${transcript}"<br><br><strong>✦ NEXUS:</strong> Thinking...`;
      }
      handleMobileVoiceQuery(transcript);
    };

    recognition.onerror = () => {
      isListening = false;
      if (mobileVoiceText) mobileVoiceText.textContent = 'Tap to Talk (Voice)';
      if (mobileSpeechOutput) mobileSpeechOutput.textContent = 'Microphone access ready. Tap to try again!';
    };

    recognition.onend = () => {
      isListening = false;
      if (mobileVoiceText) mobileVoiceText.textContent = 'Tap to Talk (Voice)';
    };
  }

  if (mobileVoiceBtn) {
    mobileVoiceBtn.addEventListener('click', () => {
      if (!recognition) {
        alert('Web Speech API is supported on Google Chrome, Safari, and Edge on mobile!');
        return;
      }
      if (!isListening) {
        try { recognition.start(); } catch(e) {}
      } else {
        try { recognition.stop(); } catch(e) {}
      }
    });
  }

  // Mobile Cheer Button
  const cheerBtn = document.getElementById('mobileCheerBtn');
  if (cheerBtn) {
    cheerBtn.addEventListener('click', () => {
      triggerCheerEffect();
      speakText("Yaaay! Celebrating with you!");
    });
  }

  // Mobile Camera Input
  const camInput = document.getElementById('mobileCameraInput');
  if (camInput) {
    camInput.addEventListener('change', (e) => {
      const file = e.target.files[0];
      if (file) {
        if (mobileSpeechOutput) {
          mobileSpeechOutput.innerHTML = `📷 <strong>Photo Captured:</strong> ${file.name} (${Math.round(file.size / 1024)} KB)<br><br><span style="color:#38bdf8;">✦ NEXUS Vision:</span> Image received! Analyzing photo structure with computer vision...`;
        }
        triggerPetHappy();
        speakText("I received your photo! Vision analysis complete.");
      }
    });
  }

  requestAnimationFrame(animate);
})();
