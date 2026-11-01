/**
 * NEXUS Mobile Companion Controller & Vector Pet Engine
 * Optimized for mobile touchscreens, Web Speech API, and haptic feedback.
 */

(function () {
  // Elements
  const canvas = document.getElementById('mobilePetCanvas');
  const ctx = canvas.getContext('2d');
  const bubbleText = document.getElementById('bubbleText');
  const chatMessages = document.getElementById('chatMessages');
  const chatInput = document.getElementById('chatInput');
  const sendBtn = document.getElementById('sendBtn');
  const micBtn = document.getElementById('micBtn');
  const skinToggleBtn = document.getElementById('skinToggleBtn');
  const skinIcon = document.getElementById('skinIcon');
  const skinLabel = document.getElementById('skinLabel');
  const voiceToggleBtn = document.getElementById('voiceToggleBtn');
  const voiceStatusIcon = document.getElementById('voiceStatusIcon');
  const settingsBtn = document.getElementById('settingsBtn');
  const settingsModal = document.getElementById('settingsModal');
  const closeModalBtn = document.getElementById('closeModalBtn');
  const saveSettingsBtn = document.getElementById('saveSettingsBtn');
  const geminiKeyInput = document.getElementById('geminiKeyInput');
  const groqKeyInput = document.getElementById('groqKeyInput');
  const personaSelect = document.getElementById('personaSelect');
  const cameraUpload = document.getElementById('cameraUpload');
  const repeatSpeechBtn = document.getElementById('repeatSpeechBtn');

  // Pet State
  let activeSkin = localStorage.getItem('nexus_mobile_skin') || 'habibi'; // 'habibi' or 'cyber'
  let voiceEnabled = localStorage.getItem('nexus_mobile_voice') !== 'false';
  let activePersona = localStorage.getItem('nexus_mobile_persona') || 'companion';
  let touchX = canvas.width / 2;
  let touchY = canvas.height / 2;
  let currentLookX = 0;
  let currentLookY = 0;
  let stateTime = 0;
  let squishX = 1.0;
  let squishY = 1.0;
  let particles = [];
  let celebrationTime = 0;
  let isSpeaking = false;
  let lastSpokenText = bubbleText.textContent;

  // Initialize UI
  updateSkinUI();
  updateVoiceUI();
  geminiKeyInput.value = localStorage.getItem('nexus_gemini_key') || '';
  groqKeyInput.value = localStorage.getItem('nexus_groq_key') || '';
  personaSelect.value = activePersona;

  // Touch Events on Pet Canvas
  canvas.addEventListener('touchstart', (e) => {
    handleTouch(e);
    triggerPetAction();
  }, { passive: true });

  canvas.addEventListener('touchmove', (e) => {
    handleTouch(e);
  }, { passive: true });

  canvas.addEventListener('touchend', () => {
    touchX = canvas.width / 2;
    touchY = canvas.height / 2;
    squishX = 0.95;
    squishY = 1.05;
  });

  // Mouse fallback for testing on desktop
  canvas.addEventListener('mousemove', (e) => {
    const rect = canvas.getBoundingClientRect();
    touchX = e.clientX - rect.left;
    touchY = e.clientY - rect.top;
  });
  canvas.addEventListener('click', () => {
    triggerPetAction();
  });

  function handleTouch(e) {
    if (e.touches && e.touches.length > 0) {
      const rect = canvas.getBoundingClientRect();
      touchX = e.touches[0].clientX - rect.left;
      touchY = e.touches[0].clientY - rect.top;
      if (Math.random() < 0.2) {
        spawnParticles('heart', 1, '#ec4899');
      }
    }
  }

  // Particle System
  class MobileParticle {
    constructor(x, y, type, color) {
      this.x = x;
      this.y = y;
      this.type = type;
      this.color = color;
      this.vx = (Math.random() - 0.5) * 4;
      this.vy = -Math.random() * 3.5 - 1;
      this.life = 1.0;
      this.decay = Math.random() * 0.025 + 0.02;
      this.size = Math.random() * 8 + 6;
    }

    update() {
      this.x += this.vx;
      this.y += this.vy;
      this.vy += 0.08;
      this.life -= this.decay;
    }

    draw(ctx) {
      ctx.save();
      ctx.globalAlpha = Math.max(0, this.life);
      ctx.fillStyle = this.color;
      if (this.type === 'coin') {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size * 0.7, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 1;
        ctx.stroke();
      } else if (this.type === 'heart') {
        const s = this.size * 0.6;
        ctx.beginPath();
        ctx.moveTo(this.x, this.y);
        ctx.bezierCurveTo(this.x - s, this.y - s, this.x - s * 1.5, this.y + s * 0.5, this.x, this.y + s * 1.4);
        ctx.bezierCurveTo(this.x + s * 1.5, this.y + s * 0.5, this.x + s, this.y - s, this.x, this.y);
        ctx.fill();
      } else {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size * 0.5, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.restore();
    }
  }

  function spawnParticles(type, count, color) {
    const cx = canvas.width / 2;
    const cy = canvas.height / 2;
    for (let i = 0; i < count; i++) {
      particles.push(new MobileParticle(cx, cy, type, color));
    }
  }

  // Animation Loop
  function animate() {
    stateTime += 0.035;

    // Levitation Physics
    const levitateY = Math.sin(stateTime * 2.5) * 8;
    const bodyW = 100 * squishX;
    const bodyH = 92 * squishY;
    const cx = canvas.width / 2;
    const cy = canvas.height / 2 + levitateY;

    // Smooth eye tracking
    const targetLookX = (touchX - cx) / (canvas.width * 0.4);
    const targetLookY = (touchY - cy) / (canvas.height * 0.4);
    currentLookX += (Math.max(-1, Math.min(1, targetLookX)) - currentLookX) * 0.12;
    currentLookY += (Math.max(-1, Math.min(1, targetLookY)) - currentLookY) * 0.12;

    // Decay squish
    squishX += (1.0 - squishX) * 0.08;
    squishY += (1.0 - squishY) * 0.08;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // 1. Soft Shadow
    ctx.save();
    ctx.fillStyle = 'rgba(0, 0, 0, 0.35)';
    ctx.beginPath();
    ctx.ellipse(cx, canvas.height - 35, bodyW * 0.65, 12, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();

    ctx.save();
    ctx.translate(cx, cy);

    // 2. Royal Habibi Ghutra (Drapes behind body)
    if (activeSkin === 'habibi') {
      ctx.fillStyle = '#ffffff';
      ctx.beginPath();
      ctx.ellipse(-bodyW * 0.45, 10, 16, 45, -0.15, 0, Math.PI * 2);
      ctx.fill();
      ctx.beginPath();
      ctx.ellipse(bodyW * 0.45, 10, 16, 45, 0.15, 0, Math.PI * 2);
      ctx.fill();
    }

    // 3. Body Capsule
    const bodyGrad = ctx.createLinearGradient(0, -bodyH, 0, bodyH);
    if (activeSkin === 'habibi') {
      bodyGrad.addColorStop(0, '#ffffff');
      bodyGrad.addColorStop(1, '#e2e8f0');
    } else {
      bodyGrad.addColorStop(0, '#0f172a');
      bodyGrad.addColorStop(1, '#0284c7');
    }
    ctx.fillStyle = bodyGrad;
    ctx.strokeStyle = activeSkin === 'habibi' ? '#d4af37' : '#38bdf8';
    ctx.lineWidth = 2.5;

    ctx.beginPath();
    ctx.ellipse(0, 0, bodyW * 0.5, bodyH * 0.5, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();

    // 4. Face Visor
    ctx.fillStyle = '#05070e';
    ctx.beginPath();
    ctx.ellipse(0, -4, bodyW * 0.38, bodyH * 0.28, 0, 0, Math.PI * 2);
    ctx.fill();

    // 5. Eyes or Aviators
    if (activeSkin === 'habibi') {
      // Luxury Gold Aviators
      const eyeOffsetX = currentLookX * 4;
      const eyeOffsetY = currentLookY * 3;
      ctx.fillStyle = '#0f172a';
      ctx.strokeStyle = '#fbbf24';
      ctx.lineWidth = 2.2;

      // Left lens
      ctx.beginPath();
      ctx.roundRect(-24 + eyeOffsetX, -12 + eyeOffsetY, 20, 16, [3, 3, 10, 10]);
      ctx.fill();
      ctx.stroke();

      // Right lens
      ctx.beginPath();
      ctx.roundRect(4 + eyeOffsetX, -12 + eyeOffsetY, 20, 16, [3, 3, 10, 10]);
      ctx.fill();
      ctx.stroke();

      // Golden bridge
      ctx.beginPath();
      ctx.moveTo(-4 + eyeOffsetX, -7 + eyeOffsetY);
      ctx.lineTo(4 + eyeOffsetX, -7 + eyeOffsetY);
      ctx.stroke();

      // Gold Habibi Agal Cord
      ctx.strokeStyle = '#18181b';
      ctx.lineWidth = 4;
      ctx.beginPath();
      ctx.arc(0, -bodyH * 0.42, bodyW * 0.36, Math.PI, 0);
      ctx.stroke();

      ctx.strokeStyle = '#fbbf24';
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.arc(0, -bodyH * 0.42, bodyW * 0.36, Math.PI, 0);
      ctx.stroke();
    } else {
      // Neo Cyber Glowing Visor Eyes
      const blink = (Math.sin(stateTime * 1.5) > 0.96) ? 0.2 : 1.0;
      const eyeOffsetX = currentLookX * 6;
      const eyeOffsetY = currentLookY * 4;

      ctx.fillStyle = '#38bdf8';
      ctx.shadowColor = '#38bdf8';
      ctx.shadowBlur = 10;

      // Left eye
      ctx.beginPath();
      ctx.ellipse(-14 + eyeOffsetX, -5 + eyeOffsetY, 5, 8 * blink, 0, 0, Math.PI * 2);
      ctx.fill();

      // Right eye
      ctx.beginPath();
      ctx.ellipse(14 + eyeOffsetX, -5 + eyeOffsetY, 5, 8 * blink, 0, 0, Math.PI * 2);
      ctx.fill();
      ctx.shadowBlur = 0;
    }

    // 6. Cute Blush
    ctx.fillStyle = 'rgba(244, 114, 182, 0.45)';
    ctx.beginPath();
    ctx.ellipse(-26, 4, 7, 4, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.beginPath();
    ctx.ellipse(26, 4, 7, 4, 0, 0, Math.PI * 2);
    ctx.fill();

    // 7. Cute Mouth
    ctx.strokeStyle = activeSkin === 'habibi' ? '#fbbf24' : '#38bdf8';
    ctx.lineWidth = 2;
    ctx.beginPath();
    if (isSpeaking) {
      const open = (Math.sin(stateTime * 12) + 1) * 3;
      ctx.arc(0, 10, 4 + open, 0, Math.PI);
    } else {
      ctx.arc(0, 8, 4, 0.1 * Math.PI, 0.9 * Math.PI);
    }
    ctx.stroke();

    ctx.restore();

    // 8. Update & Draw Particles
    particles.forEach((p) => p.update());
    particles = particles.filter((p) => p.life > 0);
    particles.forEach((p) => p.draw(ctx));

    requestAnimationFrame(animate);
  }

  // Pet Action Handlers
  function triggerPetAction() {
    squishX = 1.2;
    squishY = 0.8;
    spawnParticles('heart', 10, '#ec4899');
    if (navigator.vibrate) navigator.vibrate([25, 35, 25]);
    updateBubble("I love your touch! 💖 Feeling happy and energized!");
  }

  function triggerHighFive() {
    squishX = 1.25;
    squishY = 0.75;
    spawnParticles('star', 15, '#38bdf8');
    spawnParticles('coin', 10, '#fbbf24');
    if (navigator.vibrate) navigator.vibrate([40, 50, 40]);
    updateBubble("High-five! ✋ +10 XP earned! We make an unbeatable team!");
    speakAloud("High-five! Ten X P earned! We make an unbeatable team!");
  }

  function triggerCheer() {
    spawnParticles('coin', 25, '#fbbf24');
    spawnParticles('star', 20, '#38bdf8');
    if (navigator.vibrate) navigator.vibrate([50, 60, 50]);
    updateBubble("Yaaay! Celebrating you! ⭐ Prosperity and success always!");
    speakAloud("Yaaay! Celebrating you! Prosperity and success always!");
  }

  function triggerKarak() {
    spawnParticles('heart', 8, '#fbbf24');
    updateBubble("Ah, warm Karak Chai with cardamom! ☕ Delicious energy boost!");
    speakAloud("Ah, warm Karak Chai with cardamom! Delicious energy boost!");
  }

  // Bubble & Chat Logic
  function updateBubble(text) {
    bubbleText.textContent = text;
    lastSpokenText = text;
  }

  function appendChatMessage(role, text) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `chat-msg ${role}`;
    
    // Format simple bold and code
    let formatted = text
      .replace(/```([a-z]*)\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    msgDiv.innerHTML = `<div class="msg-bubble">${formatted}</div>`;
    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  async function handleSend() {
    const query = chatInput.value.trim();
    if (!query) return;

    chatInput.value = '';
    appendChatMessage('user', query);
    updateBubble("✦ Thinking...");

    try {
      const answer = await window.NexusMobileAI.queryAI(query, activePersona);
      appendChatMessage('assistant', `✦ NEXUS: ${answer}`);
      updateBubble(answer.length > 120 ? answer.substring(0, 120) + "..." : answer);
      if (voiceEnabled) {
        speakAloud(answer);
      }
    } catch (err) {
      appendChatMessage('assistant', "I encountered an issue processing that. Please try again!");
    }
  }

  // Voice Speech Synthesis
  function speakAloud(text) {
    if (!voiceEnabled || !('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();

    // Clean markdown before speaking
    const cleanText = text
      .replace(/```[\s\S]*?```/g, 'Code block omitted.')
      .replace(/[\*\_#`]/g, '');

    const utter = new SpeechSynthesisUtterance(cleanText);
    utter.rate = 1.0;
    utter.pitch = 1.05;
    utter.onstart = () => { isSpeaking = true; };
    utter.onend = () => { isSpeaking = false; };
    utter.onerror = () => { isSpeaking = false; };

    window.speechSynthesis.speak(utter);
  }

  // Web Speech API Voice Recognition
  let recognition = null;
  const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;

  if (SpeechRec) {
    recognition = new SpeechRec();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
      micBtn.classList.add('active');
      updateBubble("🎙️ Listening to your voice... Speak now!");
    };

    recognition.onresult = (e) => {
      const transcript = e.results[0][0].transcript;
      chatInput.value = transcript;
      handleSend();
    };

    recognition.onend = () => {
      micBtn.classList.remove('active');
    };

    recognition.onerror = () => {
      micBtn.classList.remove('active');
      updateBubble("Could not hear voice. Tap the mic and try again!");
    };
  }

  // UI Event Listeners
  sendBtn.addEventListener('click', handleSend);
  chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleSend();
  });

  micBtn.addEventListener('click', () => {
    if (!recognition) {
      alert("Microphone recognition is supported on Google Chrome and Safari on mobile!");
      return;
    }
    try {
      recognition.start();
    } catch (err) {
      recognition.stop();
    }
  });

  document.getElementById('petBtn').addEventListener('click', triggerPetAction);
  document.getElementById('highFiveBtn').addEventListener('click', triggerHighFive);
  document.getElementById('cheerBtn').addEventListener('click', triggerCheer);
  document.getElementById('karakBtn').addEventListener('click', triggerKarak);

  repeatSpeechBtn.addEventListener('click', () => {
    speakAloud(lastSpokenText);
  });

  skinToggleBtn.addEventListener('click', () => {
    activeSkin = activeSkin === 'habibi' ? 'cyber' : 'habibi';
    localStorage.setItem('nexus_mobile_skin', activeSkin);
    updateSkinUI();
    spawnParticles('coin', 15, activeSkin === 'habibi' ? '#fbbf24' : '#38bdf8');
  });

  function updateSkinUI() {
    if (activeSkin === 'habibi') {
      skinIcon.textContent = '👑';
      skinLabel.textContent = 'Habibi';
      skinToggleBtn.className = 'pill-btn skin-pill';
    } else {
      skinIcon.textContent = '💠';
      skinLabel.textContent = 'Cyber';
      skinToggleBtn.className = 'pill-btn';
    }
  }

  voiceToggleBtn.addEventListener('click', () => {
    voiceEnabled = !voiceEnabled;
    localStorage.setItem('nexus_mobile_voice', voiceEnabled);
    updateVoiceUI();
  });

  function updateVoiceUI() {
    voiceStatusIcon.textContent = voiceEnabled ? '🔊' : '🔇';
    if (!voiceEnabled && 'speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      isSpeaking = false;
    }
  }

  // Camera Upload
  cameraUpload.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
      appendChatMessage('user', `📷 Attached photo: <strong>${file.name}</strong>`);
      updateBubble("Analyzing photo with mobile vision...");
      setTimeout(() => {
        const reply = `I received your photo "${file.name}" (${Math.round(file.size / 1024)} KB)! Looking sharp! What would you like to analyze about this image?`;
        appendChatMessage('assistant', `✦ NEXUS Vision: ${reply}`);
        updateBubble(reply);
        speakAloud(reply);
        triggerPetAction();
      }, 900);
    }
  });

  // Settings Modal
  settingsBtn.addEventListener('click', () => { settingsModal.style.display = 'flex'; });
  closeModalBtn.addEventListener('click', () => { settingsModal.style.display = 'none'; });
  saveSettingsBtn.addEventListener('click', () => {
    localStorage.setItem('nexus_gemini_key', geminiKeyInput.value.trim());
    localStorage.setItem('nexus_groq_key', groqKeyInput.value.trim());
    activePersona = personaSelect.value;
    localStorage.setItem('nexus_mobile_persona', activePersona);
    settingsModal.style.display = 'none';
    updateBubble("Settings saved! Ready to assist you.");
  });

  document.getElementById('clearChatBtn').addEventListener('click', () => {
    chatMessages.innerHTML = `
      <div class="chat-msg assistant">
        <div class="msg-bubble">
          <strong>✦ NEXUS:</strong> Chat history cleared. How can I help you?
        </div>
      </div>
    `;
  });

  // Register PWA service worker
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('./sw.js').catch(() => {});
  }

  // Start Animation
  requestAnimationFrame(animate);
})();
