/**
 * NEXUS Mobile Companion Application Logic v3.0
 * Comprehensive Native Mobile Experience:
 * - 5-Tab Dynamic Navigation (Pet, Chat, Games Arcade, EXP Unlocks, Settings)
 * - Mozilla PDF.js Multi-Page Document Reader & Multimodal Vision
 * - 8 Animated Vector Pet Archetypes with Touch & Affection
 * - Arcade & Brain Games (Tic-Tac-Toe, Memory Matrix, AI Trivia)
 * - Autonomous Bot Self-Play Idle Mode (bot plays & earns XP automatically)
 * - Permanent User Name & Bond Progression Engine
 * - Creator Attribution: "Raiyan coded me!"
 */

(function () {
  'use strict';

  // --- 1. Sound FX Synthesis (Web Audio API) ---
  const AudioContext = window.AudioContext || window.webkitAudioContext;
  let audioCtx = null;
  let voiceEnabled = true;

  function initAudio() {
    if (!audioCtx) {
      try { audioCtx = new AudioContext(); } catch (e) { console.warn("Web Audio unavailable", e); }
    }
  }

  function playTone(freq, type = 'sine', duration = 0.1, gainVal = 0.15) {
    if (!voiceEnabled) return;
    try {
      initAudio();
      if (!audioCtx) return;
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.type = type;
      osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
      gain.gain.setValueAtTime(gainVal, audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + duration);
      osc.connect(gain);
      gain.connect(audioCtx.destination);
      osc.start();
      osc.stop(audioCtx.currentTime + duration);
    } catch (e) {}
  }

  function playLevelUpChime() {
    playTone(523.25, 'triangle', 0.12);
    setTimeout(() => playTone(659.25, 'triangle', 0.12), 110);
    setTimeout(() => playTone(783.99, 'triangle', 0.15), 220);
    setTimeout(() => playTone(1046.50, 'triangle', 0.25), 330);
  }

  // --- 2. Character Archetypes (All 8 Models) ---
  const SKINS = {
    habibi_dubai: {
      name: "habibi_dubai",
      icon: "👑",
      displayName: "Royal Habibi",
      desc: "Golden Ghutra, Regal Keffiyeh & Warm Amber Aura",
      archetype: "habibi",
      primary: "#fbbf24",
      secondary: "#f59e0b",
      bodyTop: "#1c1409",
      bodyBottom: "#2d1f0f",
      bodyRim: "#fbbf24",
      particleType: "sparkle",
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
      desc: "Stealth Matt-Black Chassis & Violet Eyes",
      archetype: "phantom",
      primary: "#a855f7",
      secondary: "#7e22ce",
      bodyTop: "#08060c",
      bodyBottom: "#120e1a",
      bodyRim: "#a855f7",
      particleType: "star",
      particleColor: "#a855f7"
    },
    celestial_dragon: {
      name: "celestial_dragon",
      icon: "🐉",
      displayName: "Celestial Dragon",
      desc: "Emerald Dragon Horns & Jade Cosmic Flames",
      archetype: "dragon",
      primary: "#34d399",
      secondary: "#059669",
      bodyTop: "#081b14",
      bodyBottom: "#0f2e22",
      bodyRim: "#34d399",
      particleType: "sparkle",
      particleColor: "#34d399"
    }
  };

  let currentSkinKey = localStorage.getItem('nexus_skin') || 'habibi_dubai';
  let currentSkin = SKINS[currentSkinKey] || SKINS.habibi_dubai;

  // --- 3. DOM Elements ---
  const navItems = document.querySelectorAll('.nav-item');
  const tabViews = document.querySelectorAll('.tab-view');

  const bondFill = document.getElementById('bondFill');
  const bondLevelText = document.getElementById('bondLevelText');
  const bondXpText = document.getElementById('bondXpText');
  const miniBondText = document.getElementById('miniBondText');
  const userBadgeBtn = document.getElementById('userBadgeBtn');
  const userBadgeText = document.getElementById('userBadgeText');
  const voiceToggleBtn = document.getElementById('voiceToggleBtn');
  const voiceStatusIcon = document.getElementById('voiceStatusIcon');

  const speechBubble = document.getElementById('speechBubble');
  const bubbleArchetype = document.getElementById('bubbleArchetype');
  const bubbleText = document.getElementById('bubbleText');
  const speechWave = document.getElementById('speechWave');
  const repeatSpeechBtn = document.getElementById('repeatSpeechBtn');
  const auraBadge = document.getElementById('auraBadge');

  const skinPickerBtn = document.getElementById('skinPickerBtn');
  const skinIcon = document.getElementById('skinIcon');
  const skinLabel = document.getElementById('skinLabel');
  const skinModal = document.getElementById('skinModal');
  const closeSkinModalBtn = document.getElementById('closeSkinModalBtn');
  const skinGrid = document.getElementById('skinGrid');

  const nameModal = document.getElementById('nameModal');
  const userNameInput = document.getElementById('userNameInput');
  const saveNameModalBtn = document.getElementById('saveNameModalBtn');
  const closeNameModalBtn = document.getElementById('closeNameModalBtn');

  const chatMessages = document.getElementById('chatMessages');
  const chatInput = document.getElementById('chatInput');
  const sendBtn = document.getElementById('sendBtn');
  const docUpload = document.getElementById('docUpload');
  const cameraUpload = document.getElementById('cameraUpload');
  const micBtn = document.getElementById('micBtn');
  const clearChatBtn = document.getElementById('clearChatBtn');
  const chatPersonaSelect = document.getElementById('chatPersonaSelect');

  const attachmentStrip = document.getElementById('attachmentStrip');
  const attachmentName = document.getElementById('attachmentName');
  const attachmentSize = document.getElementById('attachmentSize');
  const attachmentThumbWrap = document.getElementById('attachmentThumbWrap');
  const attachmentThumb = document.getElementById('attachmentThumb');
  const attIcon = document.getElementById('attIcon');
  const removeAttachmentBtn = document.getElementById('removeAttachmentBtn');

  // Pet action buttons
  const petBtn = document.getElementById('petBtn');
  const highFiveBtn = document.getElementById('highFiveBtn');
  const cheerBtn = document.getElementById('cheerBtn');
  const karakBtn = document.getElementById('karakBtn');
  const danceBtn = document.getElementById('danceBtn');

  // Games DOM
  const gameTabTtt = document.getElementById('gameTabTtt');
  const gameTabMem = document.getElementById('gameTabMem');
  const gameTabTrivia = document.getElementById('gameTabTrivia');
  const gameTttSection = document.getElementById('gameTttSection');
  const gameMemSection = document.getElementById('gameMemSection');
  const gameTriviaSection = document.getElementById('gameTriviaSection');
  const botSelfPlayToggle = document.getElementById('botSelfPlayToggle');

  // Unlocks DOM
  const heroRankTitle = document.getElementById('heroRankTitle');
  const heroXpText = document.getElementById('heroXpText');
  const heroXpFill = document.getElementById('heroXpFill');

  // Settings DOM
  const diagBattery = document.getElementById('diagBattery');
  const diagBatteryBar = document.getElementById('diagBatteryBar');
  const diagMemory = document.getElementById('diagMemory');
  const diagCpu = document.getElementById('diagCpu');
  const diagNetwork = document.getElementById('diagNetwork');
  const diagStorage = document.getElementById('diagStorage');
  const settingProviderSelect = document.getElementById('settingProviderSelect');
  const geminiKeyInput = document.getElementById('geminiKeyInput');
  const groqKeyInput = document.getElementById('groqKeyInput');
  const openRouterKeyInput = document.getElementById('openRouterKeyInput');
  const saveKeysBtn = document.getElementById('saveKeysBtn');
  const settingUserNameInput = document.getElementById('settingUserNameInput');
  const saveUserNameBtn = document.getElementById('saveUserNameBtn');

  // Active state
  let totalXP = parseInt(localStorage.getItem('nexus_bond_xp') || '0', 10);
  let activeAttachment = null;
  let botSelfPlayActive = false;
  let conversationHistory = [
    { role: 'assistant', content: "Raiyan coded me! I am NEXUS, your personal autonomous AI companion. Ask me anything, attach multi-page PDFs or code, snap photos with your camera, or play games!" }
  ];

  // --- 4. Tab Navigation Engine ---
  function switchTab(viewId) {
    tabViews.forEach(v => v.classList.remove('active'));
    navItems.forEach(n => n.classList.remove('active'));

    const targetView = document.getElementById(viewId);
    if (targetView) targetView.classList.add('active');

    const targetNav = Array.from(navItems).find(n => n.dataset.view === viewId);
    if (targetNav) targetNav.classList.add('active');

    playTone(500, 'sine', 0.08);
  }

  navItems.forEach(item => {
    item.addEventListener('click', () => {
      switchTab(item.dataset.view);
    });
  });

  // --- 5. Bond & EXP Unlocks Engine ---
  const LEVEL_THRESHOLDS = [
    { level: 1, title: "Novice Companion", minXp: 0, maxXp: 25 },
    { level: 2, title: "Arcade Master", minXp: 25, maxXp: 60 },
    { level: 3, title: "Cyber Sage", minXp: 60, maxXp: 120 },
    { level: 4, title: "Karak Monarch", minXp: 120, maxXp: 200 },
    { level: 5, title: "Omnipresent Deity", minXp: 200, maxXp: 350 }
  ];

  function getLevelInfo(xp) {
    for (let i = LEVEL_THRESHOLDS.length - 1; i >= 0; i--) {
      if (xp >= LEVEL_THRESHOLDS[i].minXp) {
        return LEVEL_THRESHOLDS[i];
      }
    }
    return LEVEL_THRESHOLDS[0];
  }

  function updateBondUI() {
    const lvlInfo = getLevelInfo(totalXP);
    const range = lvlInfo.maxXp - lvlInfo.minXp;
    const progress = Math.min(Math.max(totalXP - lvlInfo.minXp, 0), range);
    const pct = Math.round((progress / range) * 100);

    bondLevelText.textContent = `💖 Level ${lvlInfo.level} • ${lvlInfo.title}`;
    bondXpText.textContent = `${totalXP} / ${lvlInfo.maxXp} XP`;
    bondFill.style.width = `${pct}%`;
    miniBondText.textContent = `💖 Lv.${lvlInfo.level} (${totalXP} XP)`;

    if (heroRankTitle) {
      heroRankTitle.textContent = `👑 Level ${lvlInfo.level}: ${lvlInfo.title}`;
      heroXpText.textContent = `${totalXP} / ${lvlInfo.maxXp} Total XP`;
      heroXpFill.style.width = `${pct}%`;
    }

    // Update Unlock tags
    for (let i = 2; i <= 5; i++) {
      const tag = document.getElementById(`tagLvl${i}`);
      const item = document.getElementById(`unlockLvl${i}`);
      const req = LEVEL_THRESHOLDS[i - 1].minXp;
      if (totalXP >= req) {
        if (tag) {
          tag.className = 'unlock-tag';
          tag.textContent = 'UNLOCKED';
        }
        if (item) item.classList.add('unlocked');
      } else {
        if (tag) {
          tag.className = 'unlock-tag locked';
          tag.textContent = `LOCKED (${req} XP)`;
        }
        if (item) item.classList.remove('unlocked');
      }
    }

    localStorage.setItem('nexus_bond_xp', totalXP.toString());
  }

  function addXP(amount, reason = "") {
    const prevLvl = getLevelInfo(totalXP).level;
    totalXP += amount;
    const newLvl = getLevelInfo(totalXP).level;

    updateBondUI();

    if (newLvl > prevLvl) {
      playLevelUpChime();
      spawnConfetti();
      updateBubble(`⭐ LEVEL UP! We are now Level ${newLvl}: ${getLevelInfo(totalXP).title}! New perks unlocked! 🎉`);
    } else {
      playTone(600, 'sine', 0.1);
    }
  }

  // --- 6. Speech Bubble & Living Pet Canvas Engine ---
  let bubbleTimeout = null;
  function updateBubble(text, durationMs = 5000) {
    bubbleText.textContent = text;
    speechBubble.style.display = 'block';
    if (bubbleTimeout) clearTimeout(bubbleTimeout);
    if (durationMs > 0) {
      bubbleTimeout = setTimeout(() => {}, durationMs);
    }
  }

  function speakText(text) {
    if (!voiceEnabled || !window.speechSynthesis) return;
    window.speechSynthesis.cancel();

    const clean = text.replace(/[*_#`[\]()]/g, '').trim();
    if (!clean) return;

    const utter = new SpeechSynthesisUtterance(clean);
    utter.rate = 1.05;
    utter.pitch = 1.0;

    speechWave.style.display = 'flex';
    utter.onend = () => { speechWave.style.display = 'none'; };
    utter.onerror = () => { speechWave.style.display = 'none'; };

    window.speechSynthesis.speak(utter);
  }

  repeatSpeechBtn.addEventListener('click', () => {
    speakText(bubbleText.textContent);
  });

  // Canvas Pet Animation
  const canvas = document.getElementById('mobilePetCanvas');
  const ctx = canvas.getContext('2d');
  let petAnimTime = 0;
  let petSquish = 1.0;
  let petEmotion = 'idle';
  let cursorX = 180, cursorY = 140;
  let particles = [];

  function drawPet() {
    petAnimTime += 0.04;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const cx = canvas.width / 2;
    const cy = canvas.height / 2 + Math.sin(petAnimTime * 2) * 6;
    const r = 68 * petSquish;

    // Body radial glow
    const grad = ctx.createRadialGradient(cx, cy, r * 0.2, cx, cy, r);
    grad.addColorStop(0, currentSkin.bodyBottom);
    grad.addColorStop(0.8, currentSkin.bodyTop);
    grad.addColorStop(1, currentSkin.bodyRim);

    ctx.save();
    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.fillStyle = grad;
    ctx.shadowColor = currentSkin.primary;
    ctx.shadowBlur = 18;
    ctx.fill();
    ctx.restore();

    // Archetype decorative features
    if (currentSkin.archetype === 'habibi') {
      // Golden Ghutra Headband & Regal Keffiyeh
      ctx.save();
      ctx.beginPath();
      ctx.ellipse(cx, cy - r * 0.72, r * 0.88, 14, 0, 0, Math.PI * 2);
      ctx.fillStyle = '#1c1917';
      ctx.fill();
      ctx.lineWidth = 3.5;
      ctx.strokeStyle = '#fbbf24';
      ctx.stroke();
      ctx.restore();
    } else if (currentSkin.archetype === 'fox') {
      // Fox cyber ears
      ctx.fillStyle = currentSkin.primary;
      ctx.beginPath();
      ctx.moveTo(cx - 45, cy - 40);
      ctx.lineTo(cx - 65, cy - 85);
      ctx.lineTo(cx - 20, cy - 60);
      ctx.fill();
      ctx.beginPath();
      ctx.moveTo(cx + 45, cy - 40);
      ctx.lineTo(cx + 65, cy - 85);
      ctx.lineTo(cx + 20, cy - 60);
      ctx.fill();
    } else if (currentSkin.archetype === 'cat') {
      // Cat ears
      ctx.fillStyle = currentSkin.primary;
      ctx.beginPath();
      ctx.moveTo(cx - 35, cy - 45);
      ctx.lineTo(cx - 50, cy - 80);
      ctx.lineTo(cx - 15, cy - 60);
      ctx.fill();
      ctx.beginPath();
      ctx.moveTo(cx + 35, cy - 45);
      ctx.lineTo(cx + 50, cy - 80);
      ctx.lineTo(cx + 15, cy - 60);
      ctx.fill();
    }

    // Expressive Eyes
    const eyeOffsetX = (cursorX - cx) * 0.05;
    const eyeOffsetY = (cursorY - cy) * 0.04;
    const blink = Math.sin(petAnimTime * 0.7) > 0.96;

    if (blink) {
      ctx.strokeStyle = currentSkin.primary;
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.moveTo(cx - 28, cy - 4);
      ctx.lineTo(cx - 12, cy - 4);
      ctx.moveTo(cx + 12, cy - 4);
      ctx.lineTo(cx + 28, cy - 4);
      ctx.stroke();
    } else {
      ctx.fillStyle = currentSkin.primary;
      ctx.shadowColor = currentSkin.primary;
      ctx.shadowBlur = 10;
      ctx.beginPath();
      ctx.ellipse(cx - 20 + eyeOffsetX, cy - 6 + eyeOffsetY, 7, 10, 0, 0, Math.PI * 2);
      ctx.ellipse(cx + 20 + eyeOffsetX, cy - 6 + eyeOffsetY, 7, 10, 0, 0, Math.PI * 2);
      ctx.fill();
    }

    // Mouth / smile
    ctx.strokeStyle = currentSkin.primary;
    ctx.lineWidth = 2.5;
    ctx.beginPath();
    ctx.arc(cx, cy + 12, 10, 0.15 * Math.PI, 0.85 * Math.PI);
    ctx.stroke();

    // Floating burst particles
    for (let i = particles.length - 1; i >= 0; i--) {
      const p = particles[i];
      p.x += p.vx;
      p.y += p.vy;
      p.life -= 0.025;
      if (p.life <= 0) {
        particles.splice(i, 1);
        continue;
      }
      ctx.fillStyle = p.color;
      ctx.globalAlpha = p.life;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
      ctx.fill();
      ctx.globalAlpha = 1.0;
    }

    if (petSquish < 1.0) petSquish += 0.03;
    requestAnimationFrame(drawPet);
  }
  requestAnimationFrame(drawPet);

  function spawnBurst(type = 'heart', count = 12) {
    const cx = canvas.width / 2;
    const cy = canvas.height / 2;
    for (let i = 0; i < count; i++) {
      const angle = (Math.PI * 2 * i) / count + Math.random() * 0.5;
      const speed = 2 + Math.random() * 3.5;
      particles.push({
        x: cx,
        y: cy,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed,
        life: 1.0,
        size: 3 + Math.random() * 4,
        color: currentSkin.primary
      });
    }
  }

  function spawnConfetti() {
    spawnBurst('star', 30);
  }

  // Pet Canvas Interaction (Petting)
  canvas.addEventListener('pointerdown', (e) => {
    const rect = canvas.getBoundingClientRect();
    cursorX = e.clientX - rect.left;
    cursorY = e.clientY - rect.top;
    petSquish = 0.82;
    spawnBurst('heart', 14);
    playTone(650, 'sine', 0.12);
    addXP(5, "Petting Companion");
    updateBubble("Hehehe, that tickles! 💖 Affection acknowledged!");
  });

  // Pet Action Bar Buttons
  petBtn.addEventListener('click', () => {
    petSquish = 0.84;
    spawnBurst('heart', 16);
    addXP(5, "Petting");
    updateBubble("I feel loved and happy! 💖 (+5 XP)");
  });

  highFiveBtn.addEventListener('click', () => {
    spawnBurst('sparkle', 20);
    playTone(800, 'triangle', 0.15);
    addXP(10, "High-Five");
    updateBubble("High five! ✋ Unstoppable teamwork! (+10 XP)");
  });

  cheerBtn.addEventListener('click', () => {
    spawnBurst('star', 22);
    addXP(5, "Cheer");
    updateBubble("You've got this! Reaching for the stars! ⭐ (+5 XP)");
  });

  karakBtn.addEventListener('click', () => {
    spawnBurst('sparkle', 24);
    addXP(15, "Karak Chai");
    updateBubble("Ah, a steaming royal cup of Karak Chai! ☕ Pure energy! (+15 XP)");
  });

  danceBtn.addEventListener('click', () => {
    petSquish = 0.75;
    spawnBurst('star', 25);
    addXP(10, "Dance");
    updateBubble("Look at those autonomous moves! 💃 (+10 XP)");
  });

  // Archetype Skin Switcher
  function renderSkinGrid() {
    skinGrid.innerHTML = '';
    Object.values(SKINS).forEach(s => {
      const card = document.createElement('div');
      card.className = `skin-card ${s.name === currentSkinKey ? 'active' : ''}`;
      card.innerHTML = `
        <div class="skin-card-header">
          <span>${s.icon}</span>
          <span style="color:${s.primary};">${s.displayName}</span>
        </div>
        <div class="skin-card-desc">${s.desc}</div>
      `;
      card.addEventListener('click', () => {
        currentSkinKey = s.name;
        currentSkin = s;
        localStorage.setItem('nexus_skin', s.name);
        skinIcon.textContent = s.icon;
        skinLabel.textContent = s.displayName;
        bubbleArchetype.textContent = `${s.icon} ${s.displayName}`;
        auraBadge.textContent = `✨ ${s.displayName} Aura`;
        skinModal.style.display = 'none';
        spawnBurst('sparkle', 20);
        updateBubble(`Switched archetype to ${s.displayName}!`);
        renderSkinGrid();
      });
      skinGrid.appendChild(card);
    });
  }

  skinPickerBtn.addEventListener('click', () => {
    renderSkinGrid();
    skinModal.style.display = 'flex';
  });
  closeSkinModalBtn.addEventListener('click', () => { skinModal.style.display = 'none'; });

  // --- 7. Multi-Format Document & PDF Reader ---
  docUpload.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const ext = file.name.split('.').pop().toLowerCase();
    attachmentName.textContent = file.name;
    attachmentSize.textContent = `${Math.round(file.size / 1024)} KB`;
    attachmentThumbWrap.style.display = 'none';

    // 1. PDF File Extraction using Mozilla PDF.js
    if (ext === 'pdf' || file.type === 'application/pdf') {
      attIcon.textContent = '📑';
      attachmentStrip.style.display = 'block';
      updateBubble(`Analyzing multi-page PDF "${file.name}"...`);

      try {
        const arrayBuffer = await file.arrayBuffer();
        if (typeof pdfjsLib !== 'undefined') {
          const loadingTask = pdfjsLib.getDocument({ data: arrayBuffer });
          const pdf = await loadingTask.promise;
          let fullText = `[PDF Document: "${file.name}" - ${pdf.numPages} Pages]\n`;

          for (let pageNum = 1; pageNum <= Math.min(pdf.numPages, 30); pageNum++) {
            const page = await pdf.getPage(pageNum);
            const textContent = await page.getTextContent();
            const pageString = textContent.items.map(item => item.str).join(' ');
            fullText += `\n--- Page ${pageNum} ---\n${pageString}\n`;
          }

          activeAttachment = {
            name: file.name,
            type: 'PDF Document',
            size: Math.round(file.size / 1024),
            pageCount: pdf.numPages,
            content: fullText
          };
          updateBubble(`✅ Extracted ${pdf.numPages} pages from "${file.name}"! Ready to inspect.`);
        } else {
          throw new Error("PDF.js library not loaded");
        }
      } catch (err) {
        console.warn("PDF extraction fallback:", err);
        const text = await file.text();
        activeAttachment = {
          name: file.name,
          type: 'PDF Document (Raw)',
          size: Math.round(file.size / 1024),
          content: text
        };
        updateBubble(`Attached "${file.name}". Ready to analyze.`);
      }
    }
    // 2. Code, Text, CSV Documents
    else {
      attIcon.textContent = (ext === 'csv') ? '📊' : '📄';
      attachmentStrip.style.display = 'block';
      const text = await file.text();
      activeAttachment = {
        name: file.name,
        type: `Document (.${ext})`,
        size: Math.round(file.size / 1024),
        content: text
      };
      updateBubble(`📎 Attached "${file.name}"! Type a prompt or tap send.`);
    }

    playTone(700, 'sine', 0.12);
  });

  // Camera & Image Upload with Multimodal Preview
  cameraUpload.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
      const dataUrl = event.target.result;
      const base64 = dataUrl.split(',')[1];

      activeAttachment = {
        name: file.name,
        type: 'Image (Multimodal Vision)',
        isImage: true,
        mimeType: file.type || 'image/jpeg',
        size: Math.round(file.size / 1024),
        base64: base64,
        dataUrl: dataUrl
      };

      attachmentName.textContent = file.name;
      attachmentSize.textContent = `${activeAttachment.size} KB (Vision)`;
      attachmentThumb.src = dataUrl;
      attachmentThumbWrap.style.display = 'block';
      attIcon.textContent = '📷';
      attachmentStrip.style.display = 'block';

      updateBubble(`📷 Captured photo "${file.name}"! Ask NEXUS anything about this image.`);
      playTone(750, 'sine', 0.12);
    };
    reader.readAsDataURL(file);
  });

  removeAttachmentBtn.addEventListener('click', () => {
    activeAttachment = null;
    attachmentStrip.style.display = 'none';
    docUpload.value = '';
    cameraUpload.value = '';
  });

  // --- 8. AI Chat Stream Engine ---
  function appendChatMessage(role, text) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `chat-msg ${role}`;
    
    // Markdown-like code formatting
    let formatted = text
      .replace(/```([a-z]*)\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>')
      .replace(/`([^`]+)`/g, '<code>$1</code>')
      .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
      .replace(/\*([^*]+)\*/g, '<em>$1</em>')
      .replace(/\n/g, '<br>');

    msgDiv.innerHTML = `
      <div class="msg-bubble">
        ${role === 'assistant' ? '<strong>✦ NEXUS:</strong> ' : ''}${formatted}
      </div>
    `;
    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  async function handleSend() {
    const query = chatInput.value.trim();
    if (!query && !activeAttachment) return;

    chatInput.value = '';
    const attCopy = activeAttachment ? { ...activeAttachment } : null;

    // Reset attachment bar
    activeAttachment = null;
    attachmentStrip.style.display = 'none';
    docUpload.value = '';
    cameraUpload.value = '';

    // Render user message in chat
    let userMsgText = query;
    if (attCopy) {
      userMsgText += (userMsgText ? '<br>' : '') + `<em>[Attached: ${attCopy.name} (${attCopy.type})]</em>`;
    }
    appendChatMessage('user', userMsgText);

    conversationHistory.push({ role: 'user', content: query || `Inspect attached ${attCopy?.name}` });

    updateBubble("Thinking with Frontier AI...");
    playTone(550, 'sine', 0.08);

    try {
      const persona = chatPersonaSelect.value;
      const reply = await window.NexusMobileAI.queryAI(conversationHistory, persona, attCopy);

      appendChatMessage('assistant', reply);
      conversationHistory.push({ role: 'assistant', content: reply });

      updateBubble(reply.substring(0, 140));
      speakText(reply);
      addXP(5, "AI Query");
    } catch (err) {
      console.error("AI Query Error:", err);
      appendChatMessage('assistant', "I encountered an error querying the model. Please check your network connection.");
    }
  }

  sendBtn.addEventListener('click', handleSend);
  chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleSend();
  });

  clearChatBtn.addEventListener('click', () => {
    chatMessages.innerHTML = '';
    conversationHistory = [
      { role: 'assistant', content: "Raiyan coded me! I am NEXUS, your personal autonomous AI companion." }
    ];
    appendChatMessage('assistant', conversationHistory[0].content);
  });

  // Speech Recognition (Microphone STT)
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (SpeechRecognition) {
    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      chatInput.value = transcript;
      handleSend();
    };

    micBtn.addEventListener('click', () => {
      playTone(600, 'sine', 0.1);
      updateBubble("Listening... speak now! 🎙️");
      recognition.start();
    });
  } else {
    micBtn.addEventListener('click', () => {
      updateBubble("Microphone STT not supported on this browser.");
    });
  }

  // --- 9. Arcade & Brain Games Suite ---
  // Subtab switching
  gameTabTtt.addEventListener('click', () => {
    gameTabTtt.classList.add('active');
    gameTabMem.classList.remove('active');
    gameTabTrivia.classList.remove('active');
    gameTttSection.style.display = 'flex';
    gameMemSection.style.display = 'none';
    gameTriviaSection.style.display = 'none';
  });
  gameTabMem.addEventListener('click', () => {
    gameTabMem.classList.add('active');
    gameTabTtt.classList.remove('active');
    gameTabTrivia.classList.remove('active');
    gameMemSection.style.display = 'flex';
    gameTttSection.style.display = 'none';
    gameTriviaSection.style.display = 'none';
  });
  gameTabTrivia.addEventListener('click', () => {
    gameTabTrivia.classList.add('active');
    gameTabTtt.classList.remove('active');
    gameTabMem.classList.remove('active');
    gameTriviaSection.style.display = 'flex';
    gameTttSection.style.display = 'none';
    gameMemSection.style.display = 'none';
  });

  // Autonomous Bot Self-Play Toggle
  botSelfPlayToggle.addEventListener('change', (e) => {
    botSelfPlayActive = e.target.checked;
    if (botSelfPlayActive) {
      playTone(750, 'triangle', 0.2);
      updateBubble("🤖 Bot Self-Play activated! I will now play and gain idle XP!");
      runBotSelfPlayStep();
    } else {
      updateBubble("Bot Self-Play paused.");
    }
  });

  function runBotSelfPlayStep() {
    if (!botSelfPlayActive) return;

    if (gameTttSection.style.display !== 'none') {
      // Step in Tic-Tac-Toe
      if (tttGameOver) {
        resetTtt();
      } else {
        const emptyCells = tttBoard.map((val, idx) => val === '' ? idx : null).filter(v => v !== null);
        if (emptyCells.length > 0) {
          const move = emptyCells[Math.floor(Math.random() * emptyCells.length)];
          makeTttMove(move, tttCurrentPlayer);
        }
      }
    }

    setTimeout(runBotSelfPlayStep, 1100);
  }

  // 1. Tic-Tac-Toe Game
  const tttStatus = document.getElementById('tttStatus');
  const tttDialogue = document.getElementById('tttDialogue');
  const tttResetBtn = document.getElementById('tttResetBtn');
  const tttCells = document.querySelectorAll('.ttt-cell');

  let tttBoard = ['', '', '', '', '', '', '', '', ''];
  let tttCurrentPlayer = 'X';
  let tttGameOver = false;

  function checkTttWinner(board) {
    const lines = [
      [0, 1, 2], [3, 4, 5], [6, 7, 8],
      [0, 3, 6], [1, 4, 7], [2, 5, 8],
      [0, 4, 8], [2, 4, 6]
    ];
    for (const [a, b, c] of lines) {
      if (board[a] && board[a] === board[b] && board[a] === board[c]) {
        return board[a];
      }
    }
    if (board.every(cell => cell !== '')) return 'Tie';
    return null;
  }

  function makeTttMove(idx, player) {
    if (tttBoard[idx] !== '' || tttGameOver) return;
    tttBoard[idx] = player;
    const cell = tttCells[idx];
    cell.textContent = player;
    cell.style.color = (player === 'X') ? '#38bdf8' : '#fbbf24';
    playTone(player === 'X' ? 600 : 750, 'sine', 0.1);

    const winner = checkTttWinner(tttBoard);
    if (winner) {
      tttGameOver = true;
      if (winner === 'Tie') {
        tttStatus.textContent = "🤝 Draw game! Well played!";
        tttDialogue.textContent = 'NEXUS: "Stalemate! Our logic grids collided equally."';
        addXP(10, "Tic-Tac-Toe Tie");
      } else if (winner === 'X') {
        tttStatus.textContent = "🏆 Player X Wins!";
        tttDialogue.textContent = 'NEXUS: "Incredible flank! You pierced my defense!"';
        spawnBurst('star', 20);
        addXP(25, "Tic-Tac-Toe Win");
      } else {
        tttStatus.textContent = "🤖 NEXUS (O) Wins!";
        tttDialogue.textContent = 'NEXUS: "Three in a row! Tactical victory."';
        addXP(15, "Tic-Tac-Toe Match");
      }
      return;
    }

    tttCurrentPlayer = (player === 'X') ? 'O' : 'X';
    tttStatus.textContent = `Turn: Player ${tttCurrentPlayer}`;

    // Pet AI counter-move if playing human vs pet
    if (!botSelfPlayActive && tttCurrentPlayer === 'O' && !tttGameOver) {
      setTimeout(() => {
        const empty = tttBoard.map((v, i) => v === '' ? i : null).filter(v => v !== null);
        if (empty.length > 0) {
          const petMove = empty[Math.floor(Math.random() * empty.length)];
          makeTttMove(petMove, 'O');
        }
      }, 500);
    }
  }

  tttCells.forEach(cell => {
    cell.addEventListener('click', () => {
      const idx = parseInt(cell.dataset.idx, 10);
      makeTttMove(idx, tttCurrentPlayer);
    });
  });

  function resetTtt() {
    tttBoard = ['', '', '', '', '', '', '', '', ''];
    tttCurrentPlayer = 'X';
    tttGameOver = false;
    tttCells.forEach(c => {
      c.textContent = '';
      c.style.color = '#38bdf8';
    });
    tttStatus.textContent = "Your turn! Place X.";
    tttDialogue.textContent = 'NEXUS: "New grid calibrated. Show me your best move!"';
  }
  tttResetBtn.addEventListener('click', resetTtt);

  // 2. Memory Matrix Game
  const memStatus = document.getElementById('memStatus');
  const memDialogue = document.getElementById('memDialogue');
  const memStartBtn = document.getElementById('memStartBtn');
  const memPads = document.querySelectorAll('.mem-pad');

  let memSequence = [];
  let memPlayerStep = 0;
  let memAcceptingInput = false;

  function flashPad(idx) {
    const pad = memPads[idx];
    if (!pad) return;
    pad.classList.add('flash');
    playTone(400 + idx * 120, 'triangle', 0.18);
    setTimeout(() => { pad.classList.remove('flash'); }, 300);
  }

  function startMemoryRound() {
    memAcceptingInput = false;
    if (memSequence.length === 0) {
      memSequence = [Math.floor(Math.random() * 4), Math.floor(Math.random() * 4)];
    } else {
      memSequence.push(Math.floor(Math.random() * 4));
    }
    memPlayerStep = 0;
    memStatus.textContent = `Level ${memSequence.length}: Memorize the pattern!`;

    // Playback sequence
    let i = 0;
    const timer = setInterval(() => {
      if (i < memSequence.length) {
        flashPad(memSequence[i]);
        i++;
      } else {
        clearInterval(timer);
        memAcceptingInput = true;
        memStatus.textContent = "Your turn! Repeat the pattern.";
      }
    }, 600);
  }

  memPads.forEach(pad => {
    pad.addEventListener('click', () => {
      if (!memAcceptingInput) return;
      const idx = parseInt(pad.dataset.idx, 10);
      flashPad(idx);

      if (idx === memSequence[memPlayerStep]) {
        memPlayerStep++;
        if (memPlayerStep === memSequence.length) {
          memAcceptingInput = false;
          memStatus.textContent = `🎉 Level ${memSequence.length} Cleared!`;
          addXP(20, `Memory Level ${memSequence.length}`);
          setTimeout(startMemoryRound, 1200);
        }
      } else {
        memAcceptingInput = false;
        memStatus.textContent = "❌ Pattern missed! Tap Start to retry.";
        memSequence = [];
      }
    });
  });

  memStartBtn.addEventListener('click', startMemoryRound);

  // 3. AI Brain Trivia Quiz
  const TRIVIA = [
    {
      q: "Who coded the NEXUS AI Companion architecture?",
      opts: ["Raiyan", "Anonymous", "OpenAI", "NASA"],
      ans: 0,
      exp: "Raiyan coded me! I am NEXUS, your personal autonomous AI companion."
    },
    {
      q: "Which gas is released by green plants during photosynthesis?",
      opts: ["Oxygen (O2)", "Carbon Dioxide", "Helium", "Methane"],
      ans: 0,
      exp: "Plants convert CO2 and water into glucose and Oxygen!"
    },
    {
      q: "In Python, which function returns the number of items in a collection?",
      opts: ["count()", "size()", "len()", "length()"],
      ans: 2,
      exp: "len() is the standard Python built-in to return length."
    },
    {
      q: "What is the universal gravitational constant symbolized by?",
      opts: ["g", "G", "C", "h"],
      ans: 1,
      exp: "Capital G represents the universal gravitational constant in Newton's law."
    }
  ];

  let currentTriviaIdx = 0;
  const triviaQuestion = document.getElementById('triviaQuestion');
  const triviaOptions = document.getElementById('triviaOptions');
  const triviaExplanation = document.getElementById('triviaExplanation');
  const triviaNextBtn = document.getElementById('triviaNextBtn');

  function loadTrivia(idx) {
    currentTriviaIdx = idx % TRIVIA.length;
    const item = TRIVIA[currentTriviaIdx];
    triviaQuestion.textContent = `Q${currentTriviaIdx + 1}. ${item.q}`;
    triviaExplanation.textContent = '';
    triviaOptions.innerHTML = '';

    item.opts.forEach((opt, oIdx) => {
      const btn = document.createElement('button');
      btn.className = 'trivia-opt-btn';
      btn.textContent = `${String.fromCharCode(65 + oIdx)}) ${opt}`;
      btn.addEventListener('click', () => {
        if (btn.disabled) return;
        triviaOptions.querySelectorAll('button').forEach(b => b.disabled = true);
        if (oIdx === item.ans) {
          btn.classList.add('correct');
          triviaExplanation.textContent = `✅ Correct! ${item.exp}`;
          addXP(20, "Trivia Correct");
          spawnBurst('star', 16);
        } else {
          btn.classList.add('wrong');
          triviaExplanation.textContent = `❌ Not quite. ${item.exp}`;
        }
      });
      triviaOptions.appendChild(btn);
    });
  }

  triviaNextBtn.addEventListener('click', () => {
    loadTrivia(currentTriviaIdx + 1);
  });
  loadTrivia(0);

  // --- 10. Hardware Telemetry & Diagnostics ---
  function updateTelemetry() {
    // Battery
    if (navigator.getBattery) {
      navigator.getBattery().then(bat => {
        const lvl = Math.round(bat.level * 100);
        diagBattery.textContent = `${lvl}% ${bat.charging ? '(Charging ⚡)' : ''}`;
        diagBatteryBar.style.width = `${lvl}%`;
      });
    } else {
      diagBattery.textContent = "100% (AC Supply)";
      diagBatteryBar.style.width = "100%";
    }

    // Memory
    if (performance.memory) {
      const mb = Math.round(performance.memory.usedJSHeapSize / (1024 * 1024));
      diagMemory.textContent = `${mb} MB (Heap Active)`;
    } else {
      diagMemory.textContent = "Optimal (Native)";
    }

    // CPU
    diagCpu.textContent = `${navigator.hardwareConcurrency || 8} Logical Cores`;

    // Network
    diagNetwork.textContent = navigator.onLine ? "Online (Active)" : "Offline (Local KB)";

    // Storage
    if (navigator.storage && navigator.storage.estimate) {
      navigator.storage.estimate().then(est => {
        const usedMb = Math.round((est.usage || 0) / (1024 * 1024));
        diagStorage.textContent = `${usedMb} MB indexed`;
      });
    } else {
      diagStorage.textContent = "Persistent Store OK";
    }
  }
  updateTelemetry();
  setInterval(updateTelemetry, 15000);

  // --- 11. User Name & Identity Memory ---
  function syncUserName() {
    const saved = localStorage.getItem('nexus_user_name');
    if (saved) {
      userBadgeText.textContent = `👤 ${saved}`;
      settingUserNameInput.value = saved;
      userNameInput.value = saved;
    } else {
      userBadgeText.textContent = '👤 Set Name';
    }
  }
  syncUserName();

  userBadgeBtn.addEventListener('click', () => { nameModal.style.display = 'flex'; });
  closeNameModalBtn.addEventListener('click', () => { nameModal.style.display = 'none'; });

  function saveName(name) {
    if (!name || !name.trim()) return;
    const clean = name.trim();
    localStorage.setItem('nexus_user_name', clean);
    syncUserName();
    nameModal.style.display = 'none';
    updateBubble(`Honored to know you, ${clean}! I remember you forever.`);
    playTone(700, 'sine', 0.15);
  }

  saveNameModalBtn.addEventListener('click', () => saveName(userNameInput.value));
  saveUserNameBtn.addEventListener('click', () => saveName(settingUserNameInput.value));

  // --- 12. Settings Configuration ---
  saveKeysBtn.addEventListener('click', () => {
    if (geminiKeyInput.value.trim()) {
      localStorage.setItem('nexus_gemini_key', geminiKeyInput.value.trim());
    }
    if (groqKeyInput.value.trim()) {
      localStorage.setItem('nexus_groq_key', groqKeyInput.value.trim());
    }
    if (openRouterKeyInput.value.trim()) {
      localStorage.setItem('nexus_openrouter_key', openRouterKeyInput.value.trim());
    }
    playTone(650, 'sine', 0.15);
    updateBubble("AI Configuration updated successfully!");
  });

  voiceToggleBtn.addEventListener('click', () => {
    voiceEnabled = !voiceEnabled;
    voiceStatusIcon.textContent = voiceEnabled ? '🔊' : '🔇';
    playTone(500, 'sine', 0.08);
  });

  // Initial setup
  updateBondUI();
  bubbleArchetype.textContent = `${currentSkin.icon} ${currentSkin.displayName}`;
  skinIcon.textContent = currentSkin.icon;
  skinLabel.textContent = currentSkin.displayName;
  auraBadge.textContent = `✨ ${currentSkin.displayName} Aura`;
})();
