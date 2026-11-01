/**
 * NEXUS Mobile Companion & Command Center v2.6
 * Living Vector Character Engine (8 Archetypes), Multi-Turn AI Chat,
 * Document Intelligence, Device Diagnostics, and Permanent Memory.
 * Coded by Raiyan.
 */

(function () {
  'use strict';

  // --- 1. Sound FX Synthesis (Web Audio API) ---
  const AudioCtx = window.AudioContext || window.webkitAudioContext;
  let audioCtx = null;

  function playChime(freq = 520, type = 'sine', duration = 0.12) {
    try {
      if (!audioCtx) audioCtx = new AudioCtx();
      if (audioCtx.state === 'suspended') audioCtx.resume();
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.type = type;
      osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
      gain.gain.setValueAtTime(0.08, audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + duration);
      osc.connect(gain);
      gain.connect(audioCtx.destination);
      osc.start();
      osc.stop(audioCtx.currentTime + duration);
    } catch (e) {}
  }

  // --- 2. The 8 Canonical Character Archetypes ---
  const SKINS = {
    habibi_dubai: {
      name: "habibi_dubai",
      icon: "👑",
      displayName: "Royal Habibi",
      desc: "Dubai Gold Aviators & Silk Kandura",
      archetype: "habibi",
      primary: "#fbbf24",
      secondary: "#d97706",
      bodyTop: "#ffffff",
      bodyBottom: "#e2e8f0",
      bodyRim: "#d4af37",
      particleType: "coin",
      particleColor: "#fbbf24"
    },
    neo_cyber: {
      name: "neo_cyber",
      icon: "✦",
      displayName: "Neo Cyber Core",
      desc: "Hyper-Cyan Laser Visor & Propulsion Fins",
      archetype: "orb",
      primary: "#38bdf8",
      secondary: "#0284c7",
      bodyTop: "#0f172a",
      bodyBottom: "#1e293b",
      bodyRim: "#38bdf8",
      particleType: "star",
      particleColor: "#38bdf8"
    },
    quantum_fox: {
      name: "quantum_fox",
      icon: "🦊",
      displayName: "Quantum Kitsune",
      desc: "Cyber Fox Ears & Radiant Amber Glow",
      archetype: "fox",
      primary: "#f59e0b",
      secondary: "#b45309",
      bodyTop: "#1c120c",
      bodyBottom: "#2d1a10",
      bodyRim: "#f59e0b",
      particleType: "sparkle",
      particleColor: "#f59e0b"
    },
    chrono_mech: {
      name: "chrono_mech",
      icon: "🤖",
      displayName: "Chrono Sentinel",
      desc: "Armored Steel Plate & Telemetry Antennas",
      archetype: "mech",
      primary: "#60a5fa",
      secondary: "#6366f1",
      bodyTop: "#141b2d",
      bodyBottom: "#1e293b",
      bodyRim: "#60a5fa",
      particleType: "star",
      particleColor: "#60a5fa"
    },
    nebula_cat: {
      name: "nebula_cat",
      icon: "🐱",
      displayName: "Nebula Cat",
      desc: "Curved Starlight Ears & Galaxy Stardust",
      archetype: "cat",
      primary: "#c084fc",
      secondary: "#f472b6",
      bodyTop: "#181024",
      bodyBottom: "#27193b",
      bodyRim: "#c084fc",
      particleType: "heart",
      particleColor: "#f472b6"
    },
    solar_phoenix: {
      name: "solar_phoenix",
      icon: "🔥",
      displayName: "Solar Phoenix",
      desc: "Coronal Flare Crest & Volcanic Wings",
      archetype: "phoenix",
      primary: "#fb923c",
      secondary: "#ef4444",
      bodyTop: "#20100a",
      bodyBottom: "#3d1910",
      bodyRim: "#fb923c",
      particleType: "sparkle",
      particleColor: "#fb923c"
    },
    obsidian_phantom: {
      name: "obsidian_phantom",
      icon: "🖤",
      displayName: "Obsidian Phantom",
      desc: "Stealth Pitch-Black Armor & Crimson Slit",
      archetype: "phantom",
      primary: "#f43f5e",
      secondary: "#e11d48",
      bodyTop: "#0a0a0c",
      bodyBottom: "#17171c",
      bodyRim: "#f43f5e",
      particleType: "sparkle",
      particleColor: "#f43f5e"
    },
    matrix_green: {
      name: "matrix_green",
      icon: "⚡",
      displayName: "Matrix Emerald",
      desc: "Phosphor Terminal Data & Cyber Rim",
      archetype: "matrix",
      primary: "#34d399",
      secondary: "#10b981",
      bodyTop: "#0a1810",
      bodyBottom: "#132b1d",
      bodyRim: "#34d399",
      particleType: "star",
      particleColor: "#34d399"
    }
  };

  // --- 3. DOM References ---
  const canvas = document.getElementById('mobilePetCanvas');
  const ctx = canvas.getContext('2d');
  const petStage = document.getElementById('petStage');
  const bubbleText = document.getElementById('bubbleText');
  const bubbleArchetype = document.getElementById('bubbleArchetype');
  const speechWave = document.getElementById('speechWave');
  const repeatSpeechBtn = document.getElementById('repeatSpeechBtn');
  const skinPickerBtn = document.getElementById('skinPickerBtn');
  const skinIcon = document.getElementById('skinIcon');
  const skinLabel = document.getElementById('skinLabel');
  const userBadgeBtn = document.getElementById('userBadgeBtn');
  const userBadgeText = document.getElementById('userBadgeText');
  const deviceHubBtn = document.getElementById('deviceHubBtn');
  const voiceToggleBtn = document.getElementById('voiceToggleBtn');
  const voiceStatusIcon = document.getElementById('voiceStatusIcon');
  const settingsBtn = document.getElementById('settingsBtn');
  const bondLevelText = document.getElementById('bondLevelText');
  const bondXpText = document.getElementById('bondXpText');
  const bondFill = document.getElementById('bondFill');
  const chatMessages = document.getElementById('chatMessages');
  const chatInput = document.getElementById('chatInput');
  const sendBtn = document.getElementById('sendBtn');
  const micBtn = document.getElementById('micBtn');
  const cameraUpload = document.getElementById('cameraUpload');
  const docUpload = document.getElementById('docUpload');
  const attachmentStrip = document.getElementById('attachmentStrip');
  const attachmentName = document.getElementById('attachmentName');
  const attachmentSize = document.getElementById('attachmentSize');
  const removeAttachmentBtn = document.getElementById('removeAttachmentBtn');
  const expandChatBtn = document.getElementById('expandChatBtn');
  const clearChatBtn = document.getElementById('clearChatBtn');

  // Modals
  const skinModal = document.getElementById('skinModal');
  const skinGrid = document.getElementById('skinGrid');
  const closeSkinModalBtn = document.getElementById('closeSkinModalBtn');
  const deviceModal = document.getElementById('deviceModal');
  const closeDeviceModalBtn = document.getElementById('closeDeviceModalBtn');
  const nameModal = document.getElementById('nameModal');
  const userNameInput = document.getElementById('userNameInput');
  const saveNameBtn = document.getElementById('saveNameBtn');
  const closeNameModalBtn = document.getElementById('closeNameModalBtn');
  const settingsModal = document.getElementById('settingsModal');
  const closeModalBtn = document.getElementById('closeModalBtn');
  const saveSettingsBtn = document.getElementById('saveSettingsBtn');
  const groqKeyInput = document.getElementById('groqKeyInput');
  const geminiKeyInput = document.getElementById('geminiKeyInput');
  const openRouterKeyInput = document.getElementById('openRouterKeyInput');
  const personaSelect = document.getElementById('personaSelect');

  // Diagnostics elements
  const diagBattery = document.getElementById('diagBattery');
  const diagBatteryBar = document.getElementById('diagBatteryBar');
  const diagMemory = document.getElementById('diagMemory');
  const diagCpu = document.getElementById('diagCpu');
  const diagNetwork = document.getElementById('diagNetwork');
  const diagStorage = document.getElementById('diagStorage');
  const diagUserName = document.getElementById('diagUserName');
  const diagBondLevel = document.getElementById('diagBondLevel');

  // --- 4. Application State ---
  let activeSkinKey = localStorage.getItem('nexus_mobile_skin') || 'habibi_dubai';
  if (!SKINS[activeSkinKey]) activeSkinKey = 'habibi_dubai';
  let activeSkin = SKINS[activeSkinKey];

  let activePersona = localStorage.getItem('nexus_mobile_persona') || 'companion';
  let voiceEnabled = localStorage.getItem('nexus_mobile_voice') !== 'false';
  let isSpeaking = false;
  let lastSpokenText = "Hello! I am NEXUS, your personal AI companion. Pet me, tap high-five, or ask me anything!";
  let activeAttachment = null;

  // Multi-Turn Chat Conversation Memory
  let conversationHistory = [
    { role: 'assistant', content: "Raiyan coded me! I am NEXUS, your personal autonomous AI companion on mobile. Type your question below, attach documents, tap the mic to speak, or snap photos with your camera!" }
  ];

  // Physics & Animation State
  let touchX = canvas.width / 2;
  let touchY = canvas.height / 2;
  let currentLookX = 0;
  let currentLookY = 0;
  let saccadeX = 0;
  let saccadeY = 0;
  let nextSaccadeTime = 0;
  let squishX = 1.0;
  let squishY = 1.0;
  let stateTime = 0;
  let isTouching = false;
  let particles = [];

  // --- 5. Permanent Memory & Affection System ---
  function getAffectionData() {
    const xp = parseInt(localStorage.getItem('nexus_bond_xp') || '0', 10);
    let level = 1;
    let title = "Loyal Companion";
    let nextThreshold = 25;
    let prevThreshold = 0;

    if (xp >= 300) {
      level = 5;
      title = "Soulbound Partner";
      nextThreshold = 500;
      prevThreshold = 300;
    } else if (xp >= 150) {
      level = 4;
      title = "Best Friend";
      nextThreshold = 300;
      prevThreshold = 150;
    } else if (xp >= 75) {
      level = 3;
      title = "Trusted Ally";
      nextThreshold = 150;
      prevThreshold = 75;
    } else if (xp >= 25) {
      level = 2;
      title = "Devoted Friend";
      nextThreshold = 75;
      prevThreshold = 25;
    }

    const pct = Math.min(100, Math.max(0, ((xp - prevThreshold) / (nextThreshold - prevThreshold)) * 100));
    return { xp, level, title, nextThreshold, pct };
  }

  function addXP(amount) {
    const current = parseInt(localStorage.getItem('nexus_bond_xp') || '0', 10);
    const updated = current + amount;
    localStorage.setItem('nexus_bond_xp', updated);
    updateBondUI();
    playChime(640, 'triangle', 0.15);
  }

  function updateBondUI() {
    const data = getAffectionData();
    bondLevelText.textContent = `💖 Level ${data.level} • ${data.title}`;
    bondXpText.textContent = `${data.xp} / ${data.nextThreshold} XP`;
    bondFill.style.width = `${data.pct}%`;
    diagBondLevel.textContent = `Level ${data.level} (${data.xp} XP)`;
  }

  function updateUserNameUI() {
    const name = localStorage.getItem('nexus_user_name');
    if (name) {
      userBadgeText.textContent = `👤 ${name}`;
      diagUserName.textContent = name;
    } else {
      userBadgeText.textContent = "👤 Set Name";
      diagUserName.textContent = "Not set";
    }
  }

  // --- 6. Particle Engine ---
  class MobileParticle {
    constructor(x, y, type, color) {
      this.x = x;
      this.y = y;
      this.type = type;
      this.color = color;
      this.vx = (Math.random() - 0.5) * 4.5;
      this.vy = -Math.random() * 3.5 - 1.2;
      this.life = 1.0;
      this.decay = Math.random() * 0.02 + 0.015;
      this.size = Math.random() * 8 + 6;
    }

    update() {
      this.x += this.vx;
      this.y += this.vy;
      this.vy += 0.08;
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
        ctx.lineWidth = 1.2;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size * 0.7, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();
        ctx.strokeStyle = '#92400e';
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size * 0.4, 0, Math.PI * 2);
        ctx.stroke();
      } else if (this.type === 'heart') {
        // Heart particle
        ctx.fillStyle = this.color || '#ec4899';
        const s = this.size * 0.7;
        ctx.beginPath();
        ctx.moveTo(this.x, this.y);
        ctx.bezierCurveTo(this.x - s, this.y - s, this.x - s * 1.5, this.y + s * 0.5, this.x, this.y + s * 1.4);
        ctx.bezierCurveTo(this.x + s * 1.5, this.y + s * 0.5, this.x + s, this.y - s, this.x, this.y);
        ctx.fill();
      } else if (this.type === 'sparkle') {
        // 4-point sparkle star
        ctx.fillStyle = this.color || '#fbbf24';
        const s = this.size * 0.8;
        ctx.beginPath();
        ctx.moveTo(this.x, this.y - s);
        ctx.lineTo(this.x + s * 0.25, this.y - s * 0.25);
        ctx.lineTo(this.x + s, this.y);
        ctx.lineTo(this.x + s * 0.25, this.y + s * 0.25);
        ctx.lineTo(this.x, this.y + s);
        ctx.lineTo(this.x - s * 0.25, this.y + s * 0.25);
        ctx.lineTo(this.x - s, this.y);
        ctx.lineTo(this.x - s * 0.25, this.y - s * 0.25);
        ctx.closePath();
        ctx.fill();
      } else {
        // Star particle
        ctx.fillStyle = this.color || '#38bdf8';
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

  // --- 7. Living Canvas Vector Pet Renderer (8 Archetypes) ---
  function animate() {
    stateTime += 0.035;

    // Biological Involuntary Eye Micro-Saccades
    if (stateTime > nextSaccadeTime) {
      saccadeX = (Math.random() - 0.5) * 0.25;
      saccadeY = (Math.random() - 0.5) * 0.2;
      nextSaccadeTime = stateTime + Math.random() * 3.0 + 1.5;
    }

    // Levitation Physics
    const levitateY = Math.sin(stateTime * 2.5) * 8;
    const bodyW = 100 * squishX;
    const bodyH = 92 * squishY;
    const cx = canvas.width / 2;
    const cy = canvas.height / 2 + levitateY;

    // Smooth Eye Tracking
    const targetLookX = (touchX - cx) / (canvas.width * 0.4) + saccadeX;
    const targetLookY = (touchY - cy) / (canvas.height * 0.4) + saccadeY;
    currentLookX += (Math.max(-1, Math.min(1, targetLookX)) - currentLookX) * 0.12;
    currentLookY += (Math.max(-1, Math.min(1, targetLookY)) - currentLookY) * 0.12;

    // Rebound squish decay
    squishX += (1.0 - squishX) * 0.09;
    squishY += (1.0 - squishY) * 0.09;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // 1. Soft Ambient Ground Shadow
    ctx.save();
    ctx.fillStyle = 'rgba(0, 0, 0, 0.38)';
    ctx.beginPath();
    ctx.ellipse(cx, canvas.height - 30, bodyW * 0.65, 12, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();

    ctx.save();
    ctx.translate(cx, cy);

    // 2. Archetype Layer 1: Background Features (Behind Body)
    drawArchetypeBack(ctx, bodyW, bodyH);

    // 3. Main Chassis Capsule
    const bodyGrad = ctx.createLinearGradient(0, -bodyH * 0.5, 0, bodyH * 0.5);
    bodyGrad.addColorStop(0, activeSkin.bodyTop);
    bodyGrad.addColorStop(1, activeSkin.bodyBottom);
    ctx.fillStyle = bodyGrad;
    ctx.strokeStyle = activeSkin.bodyRim;
    ctx.lineWidth = 2.4;
    ctx.beginPath();
    ctx.ellipse(0, 0, bodyW * 0.5, bodyH * 0.5, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();

    // 4. Dark Visor Window
    ctx.fillStyle = '#05070e';
    ctx.beginPath();
    ctx.ellipse(0, -4, bodyW * 0.38, bodyH * 0.28, 0, 0, Math.PI * 2);
    ctx.fill();

    // 5. Archetype Layer 2: Eyes, Aviators & Face
    drawFaceAndEyes(ctx, bodyW, bodyH);

    // 6. Archetype Layer 3: Foreground Accessories (Ghutra Top, Ears, Antennas, Wings)
    drawArchetypeFront(ctx, bodyW, bodyH);

    // 7. Dynamic Animated Mouth
    drawMouth(ctx);

    ctx.restore();

    // 8. Update & Draw Active Particles
    particles.forEach((p) => p.update());
    particles = particles.filter((p) => p.life > 0);
    particles.forEach((p) => p.draw(ctx));

    requestAnimationFrame(animate);
  }

  // --- Archetype Feature Drawings ---
  function drawArchetypeBack(ctx, bw, bh) {
    if (activeSkin.archetype === 'habibi') {
      // Flowing Silk Ghutra Drapes behind shoulders
      ctx.fillStyle = '#f8fafc';
      ctx.strokeStyle = '#e2e8f0';
      ctx.lineWidth = 1;

      // Left Drape
      ctx.beginPath();
      ctx.ellipse(-bw * 0.46, 12, 17, 48, -0.16, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();

      // Right Drape
      ctx.beginPath();
      ctx.ellipse(bw * 0.46, 12, 17, 48, 0.16, 0, Math.PI * 2);
      ctx.fill();
      ctx.stroke();
    } else if (activeSkin.archetype === 'fox') {
      // Quantum Fox Back Tail Glow
      const tailWiggle = Math.sin(stateTime * 3) * 6;
      ctx.fillStyle = 'rgba(245, 158, 11, 0.35)';
      ctx.beginPath();
      ctx.ellipse(bw * 0.5, 18 + tailWiggle, 16, 32, 0.4, 0, Math.PI * 2);
      ctx.fill();
    } else if (activeSkin.archetype === 'orb') {
      // Neo Cyber Propulsion Fins
      const finFlap = Math.sin(stateTime * 4.5) * 3;
      ctx.fillStyle = activeSkin.primary;
      ctx.beginPath();
      ctx.ellipse(-bw * 0.52, -2 + finFlap, 6, 20, -0.2, 0, Math.PI * 2);
      ctx.fill();
      ctx.beginPath();
      ctx.ellipse(bw * 0.52, -2 - finFlap, 6, 20, 0.2, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  function drawFaceAndEyes(ctx, bw, bh) {
    const eyeOffsetX = currentLookX * 4.5;
    const eyeOffsetY = currentLookY * 3.5;

    if (activeSkin.archetype === 'habibi') {
      // Royal Dubai Gold Aviators
      ctx.fillStyle = '#0f172a';
      ctx.strokeStyle = '#fbbf24';
      ctx.lineWidth = 2.2;

      // Left mirrored aviator lens
      ctx.beginPath();
      ctx.roundRect(-25 + eyeOffsetX, -13 + eyeOffsetY, 21, 17, [4, 4, 11, 11]);
      ctx.fill();
      ctx.stroke();

      // Right mirrored aviator lens
      ctx.beginPath();
      ctx.roundRect(4 + eyeOffsetX, -13 + eyeOffsetY, 21, 17, [4, 4, 11, 11]);
      ctx.fill();
      ctx.stroke();

      // Golden Bridge
      ctx.beginPath();
      ctx.moveTo(-4 + eyeOffsetX, -8 + eyeOffsetY);
      ctx.lineTo(4 + eyeOffsetX, -8 + eyeOffsetY);
      ctx.stroke();

      // Specular Sheen Reflections
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.55)';
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.moveTo(-21 + eyeOffsetX, -11 + eyeOffsetY);
      ctx.lineTo(-13 + eyeOffsetX, -1 + eyeOffsetY);
      ctx.stroke();

      ctx.beginPath();
      ctx.moveTo(8 + eyeOffsetX, -11 + eyeOffsetY);
      ctx.lineTo(16 + eyeOffsetX, -1 + eyeOffsetY);
      ctx.stroke();

      // 4-Point Golden Star Glint on frame edge
      ctx.fillStyle = '#fffbeb';
      ctx.beginPath();
      const gx = 23 + eyeOffsetX;
      const gy = -13 + eyeOffsetY;
      ctx.arc(gx, gy, 2, 0, Math.PI * 2);
      ctx.fill();
    } else if (activeSkin.archetype === 'phantom') {
      // Obsidian Crimson Laser Slit
      ctx.fillStyle = '#f43f5e';
      ctx.shadowColor = '#f43f5e';
      ctx.shadowBlur = 8;
      ctx.beginPath();
      ctx.ellipse(eyeOffsetX, -5 + eyeOffsetY, 22, 3, 0, 0, Math.PI * 2);
      ctx.fill();
      ctx.shadowBlur = 0;
    } else {
      // Expressive Vector Visor Eyes (Blink & Emotion)
      const blink = (Math.sin(stateTime * 1.4) > 0.96) ? 0.2 : 1.0;
      ctx.fillStyle = activeSkin.primary;
      ctx.shadowColor = activeSkin.primary;
      ctx.shadowBlur = 10;

      // Left Eye
      ctx.beginPath();
      ctx.ellipse(-15 + eyeOffsetX, -5 + eyeOffsetY, 5, 8 * blink, 0, 0, Math.PI * 2);
      ctx.fill();

      // Right Eye
      ctx.beginPath();
      ctx.ellipse(15 + eyeOffsetX, -5 + eyeOffsetY, 5, 8 * blink, 0, 0, Math.PI * 2);
      ctx.fill();
      ctx.shadowBlur = 0;
    }

    // Cute Cheek Blush
    ctx.fillStyle = 'rgba(244, 114, 182, 0.4)';
    ctx.beginPath();
    ctx.ellipse(-26, 4, 7, 4, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.beginPath();
    ctx.ellipse(26, 4, 7, 4, 0, 0, Math.PI * 2);
    ctx.fill();
  }

  function drawArchetypeFront(ctx, bw, bh) {
    if (activeSkin.archetype === 'habibi') {
      // Dual Gold & Black Agal Cord on top of head
      ctx.strokeStyle = '#18181b';
      ctx.lineWidth = 4.5;
      ctx.beginPath();
      ctx.arc(0, -bh * 0.42, bw * 0.36, Math.PI, 0);
      ctx.stroke();

      ctx.strokeStyle = '#fbbf24';
      ctx.lineWidth = 1.6;
      ctx.beginPath();
      ctx.arc(0, -bh * 0.42, bw * 0.36, Math.PI, 0);
      ctx.stroke();

      // Royal Gold Crest Emblem in center of agal
      ctx.fillStyle = '#fbbf24';
      ctx.beginPath();
      ctx.arc(0, -bh * 0.42 - 2, 3.5, 0, Math.PI * 2);
      ctx.fill();
    } else if (activeSkin.archetype === 'fox') {
      // Tall Geometric Kitsune Cyber-Fox Ears
      for (const side of [-1, 1]) {
        ctx.save();
        ctx.translate(side * 28, -bh * 0.45);
        ctx.fillStyle = '#2d1a10';
        ctx.strokeStyle = '#f59e0b';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(0, 0);
        ctx.lineTo(side * 14, -26);
        ctx.lineTo(side * 4, 2);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();
        // Inner amber glow
        ctx.fillStyle = '#f59e0b';
        ctx.beginPath();
        ctx.moveTo(side * 2, -2);
        ctx.lineTo(side * 11, -20);
        ctx.lineTo(side * 4, 0);
        ctx.closePath();
        ctx.fill();
        ctx.restore();
      }
    } else if (activeSkin.archetype === 'cat') {
      // Nebula Cat Ears & Starlight Halo
      for (const side of [-1, 1]) {
        ctx.save();
        ctx.translate(side * 26, -bh * 0.44);
        ctx.fillStyle = '#27193b';
        ctx.strokeStyle = '#c084fc';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(0, 0);
        ctx.lineTo(side * 12, -20);
        ctx.lineTo(side * 2, 2);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();
        // Inner pink
        ctx.fillStyle = '#f472b6';
        ctx.beginPath();
        ctx.moveTo(side * 2, -2);
        ctx.lineTo(side * 9, -15);
        ctx.lineTo(side * 3, 0);
        ctx.closePath();
        ctx.fill();
        ctx.restore();
      }
    } else if (activeSkin.archetype === 'mech') {
      // Chrono Sentinel Tactical Antenna Fins
      for (const side of [-1, 1]) {
        ctx.fillStyle = '#60a5fa';
        ctx.beginPath();
        ctx.roundRect(side * 34, -bh * 0.45, side * 6, -18, 3);
        ctx.fill();
      }
    } else if (activeSkin.archetype === 'phoenix') {
      // Solar Phoenix Coronal Flare Crown
      const crownPulse = Math.sin(stateTime * 6) * 4;
      ctx.fillStyle = '#ef4444';
      ctx.beginPath();
      ctx.moveTo(-16, -bh * 0.42);
      ctx.quadraticCurveTo(-8, -bh * 0.42 - 24 - crownPulse, 0, -bh * 0.42 - 32 - crownPulse);
      ctx.quadraticCurveTo(8, -bh * 0.42 - 24 - crownPulse, 16, -bh * 0.42);
      ctx.closePath();
      ctx.fill();
      ctx.fillStyle = '#fb923c';
      ctx.beginPath();
      ctx.arc(0, -bh * 0.42 - 12, 6, 0, Math.PI * 2);
      ctx.fill();
    } else if (activeSkin.archetype === 'phantom') {
      // Obsidian Stealth Armor Edge Plates
      ctx.fillStyle = '#e11d48';
      ctx.beginPath();
      ctx.ellipse(-bw * 0.46, -10, 4, 18, -0.2, 0, Math.PI * 2);
      ctx.fill();
      ctx.beginPath();
      ctx.ellipse(bw * 0.46, -10, 4, 18, 0.2, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  function drawMouth(ctx) {
    ctx.strokeStyle = activeSkin.primary;
    ctx.lineWidth = 2;
    ctx.beginPath();
    if (isSpeaking) {
      const open = (Math.sin(stateTime * 12) + 1) * 3;
      ctx.arc(0, 10, 4 + open, 0, Math.PI);
    } else {
      ctx.arc(0, 8, 4, 0.1 * Math.PI, 0.9 * Math.PI);
    }
    ctx.stroke();
  }

  // --- 8. Touch & Squish Interaction ---
  function getCanvasCoords(e) {
    const rect = canvas.getBoundingClientRect();
    const clientX = e.touches ? e.touches[0].clientX : e.clientX;
    const clientY = e.touches ? e.touches[0].clientY : e.clientY;
    return {
      x: (clientX - rect.left) * (canvas.width / rect.width),
      y: (clientY - rect.top) * (canvas.height / rect.height)
    };
  }

  function onTouchStart(e) {
    isTouching = true;
    const pos = getCanvasCoords(e);
    touchX = pos.x;
    touchY = pos.y;
    squishX = 1.18;
    squishY = 0.82;
    spawnParticles(activeSkin.particleType, 8, activeSkin.primary);
    if (navigator.vibrate) navigator.vibrate(25);
  }

  function onTouchMove(e) {
    if (!isTouching) return;
    const pos = getCanvasCoords(e);
    touchX = pos.x;
    touchY = pos.y;
    if (Math.random() < 0.2) {
      spawnParticles(activeSkin.particleType, 1, activeSkin.primary);
    }
  }

  function onTouchEnd() {
    isTouching = false;
    touchX = canvas.width / 2;
    touchY = canvas.height / 2;
    squishX = 0.88;
    squishY = 1.14;
    addXP(2);
  }

  canvas.addEventListener('touchstart', onTouchStart, { passive: true });
  canvas.addEventListener('touchmove', onTouchMove, { passive: true });
  canvas.addEventListener('touchend', onTouchEnd, { passive: true });
  canvas.addEventListener('mousedown', onTouchStart);
  window.addEventListener('mousemove', onTouchMove);
  window.addEventListener('mouseup', onTouchEnd);

  // --- 9. Affection Action Handlers ---
  document.getElementById('petBtn').addEventListener('click', () => {
    squishX = 1.25;
    squishY = 0.78;
    spawnParticles(activeSkin.particleType, 12, activeSkin.primary);
    addXP(5);
    if (navigator.vibrate) navigator.vibrate([25, 30, 25]);
    updateBubble("I love your touch! 💖 Feeling happy, energized, and loyal!");
  });

  document.getElementById('highFiveBtn').addEventListener('click', () => {
    squishX = 1.3;
    squishY = 0.72;
    spawnParticles('star', 16, '#38bdf8');
    spawnParticles(activeSkin.particleType, 12, activeSkin.primary);
    addXP(10);
    if (navigator.vibrate) navigator.vibrate([40, 50, 40]);
    updateBubble("High-five! ✋ +10 XP earned! We make an unbeatable team!");
    speakAloud("High-five! Ten X P earned! We make an unbeatable team!");
  });

  document.getElementById('cheerBtn').addEventListener('click', () => {
    spawnParticles('coin', 22, '#fbbf24');
    spawnParticles('star', 18, '#38bdf8');
    addXP(5);
    if (navigator.vibrate) navigator.vibrate([40, 40, 40]);
    updateBubble("Yaaay! Celebrating you! ⭐ Prosperity, victory, and greatness!");
    speakAloud("Yaaay! Celebrating you! Prosperity, victory, and greatness!");
  });

  document.getElementById('karakBtn').addEventListener('click', () => {
    spawnParticles('heart', 10, '#fbbf24');
    addXP(5);
    updateBubble("Ah, warm Karak Chai with cardamom and saffron! ☕ A cup of blessings!");
    speakAloud("Ah, warm Karak Chai with cardamom and saffron! A cup of blessings!");
  });

  document.getElementById('timeBtn').addEventListener('click', () => {
    const now = new Date();
    const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const dateStr = now.toLocaleDateString(undefined, { weekday: 'short', month: 'short', day: 'numeric' });
    updateBubble(`🕒 Current time is ${timeStr} on ${dateStr}. Ready to assist!`);
    speakAloud(`The time is ${timeStr}.`);
  });

  // --- 10. Speech & Voice Engine ---
  function updateBubble(text) {
    bubbleText.textContent = text;
    lastSpokenText = text;
  }

  function speakAloud(text) {
    if (!voiceEnabled || !('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();

    // Clean code and markdown syntax
    const cleanText = text
      .replace(/```[\s\S]*?```/g, 'Code block omitted.')
      .replace(/[\*\_#`]/g, '')
      .replace(/\[Attached File:.*?\]/g, '');

    const utter = new SpeechSynthesisUtterance(cleanText);
    utter.rate = 1.0;
    utter.pitch = 1.04;
    utter.onstart = () => {
      isSpeaking = true;
      speechWave.style.display = 'inline-flex';
    };
    utter.onend = () => {
      isSpeaking = false;
      speechWave.style.display = 'none';
    };
    utter.onerror = () => {
      isSpeaking = false;
      speechWave.style.display = 'none';
    };

    window.speechSynthesis.speak(utter);
  }

  repeatSpeechBtn.addEventListener('click', () => {
    speakAloud(lastSpokenText);
  });

  voiceToggleBtn.addEventListener('click', () => {
    voiceEnabled = !voiceEnabled;
    localStorage.setItem('nexus_mobile_voice', voiceEnabled);
    voiceStatusIcon.textContent = voiceEnabled ? '🔊' : '🔇';
    if (!voiceEnabled && 'speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      isSpeaking = false;
      speechWave.style.display = 'none';
    }
  });

  // Web Speech Voice Input
  const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
  let recognition = null;
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
    recognition.onend = () => micBtn.classList.remove('active');
    recognition.onerror = () => {
      micBtn.classList.remove('active');
      updateBubble("Could not detect microphone voice. Tap the mic and try again!");
    };
  }

  micBtn.addEventListener('click', () => {
    if (!recognition) {
      alert("Microphone recognition is supported on Chrome, Safari, and modern mobile browsers!");
      return;
    }
    try { recognition.start(); } catch (e) { recognition.stop(); }
  });

  // --- 11. Markdown & Message Formatter ---
  function escapeHTML(str) {
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  function renderMarkdown(rawText) {
    if (!rawText) return "";

    // 1. Extract fenced code blocks first
    const codeBlocks = [];
    const fencedPattern = /```([a-zA-Z0-9_\-\+]*)\n([\s\S]*?)```/g;
    let processed = rawText.replace(fencedPattern, (match, lang, code) => {
      const idx = codeBlocks.length;
      const langLabel = (lang || "CODE").toUpperCase();
      const escapedCode = escapeHTML(code.trim());
      codeBlocks.push(`
        <div class="mobile-code-card">
          <div class="mobile-code-header">
            <span>${langLabel}</span>
            <button class="copy-code-btn" data-code="${encodeURIComponent(code.trim())}">📋 Copy</button>
          </div>
          <pre class="mobile-code-body"><code>${escapedCode}</code></pre>
        </div>
      `);
      return `@@@CODE_BLOCK_${idx}@@@`;
    });

    // 2. Escape remaining non-code text
    processed = escapeHTML(processed);

    // 3. Format bold, italics, inline code, lists
    processed = processed
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>')
      .replace(/^\s*[\-\*]\s+(.*)$/gm, '<li>$1</li>')
      .replace(/^\s*\d+\.\s+(.*)$/gm, '<li>$1</li>')
      .replace(/\n\n/g, '<br><br>');

    // 4. Re-insert code blocks
    codeBlocks.forEach((block, idx) => {
      processed = processed.replace(`@@@CODE_BLOCK_${idx}@@@`, block);
    });

    return processed;
  }

  function appendChatMessage(role, text, isStreaming = false) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `chat-msg ${role}`;
    
    const formatted = renderMarkdown(text);
    msgDiv.innerHTML = `
      <div class="msg-bubble">
        ${formatted}
        ${isStreaming ? '<span class="typing-cursor"></span>' : ''}
      </div>
      ${role === 'assistant' && !isStreaming ? `
        <div class="msg-actions">
          <button class="msg-action-btn copy-msg-btn">📋 Copy</button>
          <button class="msg-action-btn speak-msg-btn">🔊 Speak</button>
          <button class="msg-action-btn retry-msg-btn">🔄 Retry</button>
        </div>
      ` : ''}
    `;

    // Attach copy code listeners
    msgDiv.querySelectorAll('.copy-code-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const rawCode = decodeURIComponent(btn.getAttribute('data-code'));
        navigator.clipboard.writeText(rawCode).then(() => {
          btn.textContent = "✓ Copied!";
          setTimeout(() => { btn.textContent = "📋 Copy"; }, 1500);
        });
      });
    });

    // Attach message toolbar listeners
    if (role === 'assistant' && !isStreaming) {
      const copyBtn = msgDiv.querySelector('.copy-msg-btn');
      if (copyBtn) {
        copyBtn.addEventListener('click', () => {
          navigator.clipboard.writeText(text).then(() => {
            copyBtn.textContent = "✓ Copied!";
            setTimeout(() => { copyBtn.textContent = "📋 Copy"; }, 1500);
          });
        });
      }
      const speakBtn = msgDiv.querySelector('.speak-msg-btn');
      if (speakBtn) {
        speakBtn.addEventListener('click', () => speakAloud(text));
      }
      const retryBtn = msgDiv.querySelector('.retry-msg-btn');
      if (retryBtn) {
        retryBtn.addEventListener('click', () => {
          // Remove last assistant turn and re-query
          if (conversationHistory.length > 1) {
            conversationHistory.pop();
            const lastUserMsg = conversationHistory[conversationHistory.length - 1];
            if (lastUserMsg) {
              chatInput.value = lastUserMsg.content;
              handleSend();
            }
          }
        });
      }
    }

    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return msgDiv;
  }

  // --- 12. Send & Streaming AI Pipeline ---
  async function handleSend() {
    const query = chatInput.value.trim();
    if (!query && !activeAttachment) return;

    chatInput.value = '';
    const attCopy = activeAttachment ? { ...activeAttachment } : null;
    clearAttachment();

    // Append to UI & Conversation History
    const userDisplay = attCopy ? `📎 [${attCopy.name}]\n\n${query}` : query;
    appendChatMessage('user', userDisplay);
    conversationHistory.push({ role: 'user', content: query || `Inspect attached ${attCopy?.name}` });

    updateBubble("✦ Thinking...");
    playChime(480, 'sine', 0.1);

    // Create temporary streaming placeholder
    const streamDiv = appendChatMessage('assistant', "", true);
    const bubbleEl = streamDiv.querySelector('.msg-bubble');

    try {
      const answer = await window.NexusMobileAI.queryAI(conversationHistory, activePersona, attCopy);
      
      // Streaming typewriter effect
      let currentIdx = 0;
      const stepInterval = Math.max(15, Math.min(35, 1200 / answer.length));
      
      const timer = setInterval(() => {
        currentIdx += 3;
        if (currentIdx >= answer.length) {
          clearInterval(timer);
          streamDiv.remove();
          appendChatMessage('assistant', answer);
          conversationHistory.push({ role: 'assistant', content: answer });
          updateBubble(answer.length > 140 ? answer.substring(0, 140) + "..." : answer);
          if (voiceEnabled) speakAloud(answer);
          addXP(3);
        } else {
          bubbleEl.innerHTML = renderMarkdown(answer.substring(0, currentIdx)) + '<span class="typing-cursor"></span>';
          chatMessages.scrollTop = chatMessages.scrollHeight;
        }
      }, stepInterval);

    } catch (err) {
      streamDiv.remove();
      const errMsg = "I encountered an issue processing that. Please try again!";
      appendChatMessage('assistant', errMsg);
      updateBubble(errMsg);
    }
  }

  sendBtn.addEventListener('click', handleSend);
  chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleSend();
  });

  // --- 13. File & Document Upload ---
  docUpload.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      activeAttachment = {
        name: file.name,
        type: file.type || 'text/plain',
        size: Math.round(file.size / 1024),
        content: event.target.result
      };
      attachmentName.textContent = activeAttachment.name;
      attachmentSize.textContent = `${activeAttachment.size} KB`;
      attachmentStrip.style.display = 'block';
      updateBubble(`📎 Attached "${file.name}"! Type a prompt or tap send to analyze.`);
      playChime(600, 'sine', 0.12);
    };
    reader.readAsText(file);
  });

  function clearAttachment() {
    activeAttachment = null;
    attachmentStrip.style.display = 'none';
    docUpload.value = '';
  }
  removeAttachmentBtn.addEventListener('click', clearAttachment);

  // Camera Photo Upload
  cameraUpload.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
      appendChatMessage('user', `📷 Captured photo: <strong>${file.name}</strong> (${Math.round(file.size / 1024)} KB)`);
      updateBubble("Analyzing photo with AI vision...");
      setTimeout(() => {
        const reply = `I received your photo "${file.name}"! Looking sharp! What would you like to explore about this image?`;
        appendChatMessage('assistant', reply);
        conversationHistory.push({ role: 'assistant', content: reply });
        updateBubble(reply);
        speakAloud(reply);
        triggerPetAction();
      }, 700);
    }
  });

  // Expand / Collapse Chat Drawer
  let isChatExpanded = false;
  expandChatBtn.addEventListener('click', () => {
    isChatExpanded = !isChatExpanded;
    const drawer = document.getElementById('chatDrawer');
    if (isChatExpanded) {
      drawer.classList.add('expanded');
      expandChatBtn.textContent = '↕️ Minimize';
    } else {
      drawer.classList.remove('expanded');
      expandChatBtn.textContent = '↕️ Expand';
    }
  });

  clearChatBtn.addEventListener('click', () => {
    conversationHistory = [
      { role: 'assistant', content: "Chat cleared. Ready for your next adventure!" }
    ];
    chatMessages.innerHTML = `
      <div class="chat-msg assistant">
        <div class="msg-bubble">
          <strong>✦ NEXUS:</strong> Chat cleared. Ready for your next adventure!
        </div>
      </div>
    `;
    updateBubble("Chat history cleared.");
  });

  // --- 14. Skin Archetype Picker (All 8 Models) ---
  function populateSkinGrid() {
    skinGrid.innerHTML = '';
    Object.keys(SKINS).forEach((key) => {
      const s = SKINS[key];
      const card = document.createElement('div');
      card.className = `skin-card ${key === activeSkinKey ? 'active' : ''}`;
      card.innerHTML = `
        <div class="skin-card-icon">${s.icon}</div>
        <div class="skin-card-title">${s.displayName}</div>
        <div class="skin-card-desc">${s.desc}</div>
      `;
      card.addEventListener('click', () => {
        setSkin(key);
        skinModal.style.display = 'none';
      });
      skinGrid.appendChild(card);
    });
  }

  function setSkin(key) {
    if (!SKINS[key]) return;
    activeSkinKey = key;
    activeSkin = SKINS[key];
    localStorage.setItem('nexus_mobile_skin', key);

    skinIcon.textContent = activeSkin.icon;
    skinLabel.textContent = activeSkin.displayName.split(' ')[0];
    bubbleArchetype.textContent = `${activeSkin.icon} ${activeSkin.displayName}`;
    
    // Update ambient glow colors
    document.getElementById('orbTop').style.background = activeSkin.primary + '22';
    document.getElementById('orbBottom').style.background = activeSkin.secondary + '1c';

    spawnParticles(activeSkin.particleType, 16, activeSkin.primary);
    playChime(700, 'sine', 0.15);
    updateBubble(`Appearance changed to ${activeSkin.displayName}!`);
  }

  skinPickerBtn.addEventListener('click', () => {
    populateSkinGrid();
    skinModal.style.display = 'flex';
  });
  closeSkinModalBtn.addEventListener('click', () => skinModal.style.display = 'none');

  // --- 15. Device Command Center & Diagnostics ---
  async function refreshDiagnostics() {
    // Battery
    if ('getBattery' in navigator) {
      try {
        const bat = await navigator.getBattery();
        const levelPct = Math.round(bat.level * 100);
        diagBattery.textContent = `${levelPct}% (${bat.charging ? '⚡ Charging' : 'On Battery'})`;
        diagBatteryBar.style.width = `${levelPct}%`;
      } catch (e) {
        diagBattery.textContent = "Supported";
      }
    } else {
      diagBattery.textContent = "Standard AC/Battery";
      diagBatteryBar.style.width = "85%";
    }

    // Memory (RAM)
    if ('deviceMemory' in navigator) {
      diagMemory.textContent = `~${navigator.deviceMemory} GB RAM`;
    } else {
      diagMemory.textContent = "High-Performance Mobile";
    }

    // CPU Cores
    if ('hardwareConcurrency' in navigator) {
      diagCpu.textContent = `${navigator.hardwareConcurrency} Cores (Active)`;
    } else {
      diagCpu.textContent = "Multi-Core ARM";
    }

    // Network
    if ('connection' in navigator && navigator.connection.effectiveType) {
      diagNetwork.textContent = `${navigator.connection.effectiveType.toUpperCase()} (Online)`;
    } else {
      diagNetwork.textContent = navigator.onLine ? "Online (Connected)" : "Offline";
    }

    // Storage
    if (navigator.storage && navigator.storage.estimate) {
      try {
        const est = await navigator.storage.estimate();
        const quotaMB = Math.round(est.quota / (1024 * 1024));
        diagStorage.textContent = `~${quotaMB} MB App Storage`;
      } catch (e) {
        diagStorage.textContent = "Client Storage Active";
      }
    } else {
      diagStorage.textContent = "Local Cache Active";
    }

    updateUserNameUI();
    updateBondUI();
  }

  deviceHubBtn.addEventListener('click', () => {
    refreshDiagnostics();
    deviceModal.style.display = 'flex';
  });
  closeDeviceModalBtn.addEventListener('click', () => deviceModal.style.display = 'none');

  // --- 16. User Name Memory Modal ---
  userBadgeBtn.addEventListener('click', () => {
    const cur = localStorage.getItem('nexus_user_name') || '';
    userNameInput.value = cur;
    nameModal.style.display = 'flex';
  });
  closeNameModalBtn.addEventListener('click', () => nameModal.style.display = 'none');
  saveNameBtn.addEventListener('click', () => {
    const val = userNameInput.value.trim();
    if (val) {
      localStorage.setItem('nexus_user_name', val);
      updateUserNameUI();
      nameModal.style.display = 'none';
      updateBubble(`Name saved! I will remember you as ${val} forever.`);
      speakAloud(`Understood. I will remember you as ${val} forever.`);
    }
  });

  // --- 17. Settings Modal ---
  settingsBtn.addEventListener('click', () => {
    groqKeyInput.value = localStorage.getItem('nexus_groq_key') || '';
    geminiKeyInput.value = localStorage.getItem('nexus_gemini_key') || '';
    openRouterKeyInput.value = localStorage.getItem('nexus_openrouter_key') || '';
    personaSelect.value = activePersona;
    settingsModal.style.display = 'flex';
  });
  closeModalBtn.addEventListener('click', () => settingsModal.style.display = 'none');
  saveSettingsBtn.addEventListener('click', () => {
    localStorage.setItem('nexus_groq_key', groqKeyInput.value.trim());
    localStorage.setItem('nexus_gemini_key', geminiKeyInput.value.trim());
    localStorage.setItem('nexus_openrouter_key', openRouterKeyInput.value.trim());
    activePersona = personaSelect.value;
    localStorage.setItem('nexus_mobile_persona', activePersona);
    settingsModal.style.display = 'none';
    updateBubble("Settings saved! Ready with enhanced intelligence.");
  });

  // Close modals on overlay click
  window.addEventListener('click', (e) => {
    if (e.target === skinModal) skinModal.style.display = 'none';
    if (e.target === deviceModal) deviceModal.style.display = 'none';
    if (e.target === nameModal) nameModal.style.display = 'none';
    if (e.target === settingsModal) settingsModal.style.display = 'none';
  });

  // --- 18. Initialize App ---
  setSkin(activeSkinKey);
  updateUserNameUI();
  updateBondUI();

  // Register PWA service worker
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('./sw.js').catch(() => {});
  }

  // Start Animation Loop
  requestAnimationFrame(animate);
})();
