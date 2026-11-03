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
  const restBtn = document.getElementById('restBtn');

  // Pet vitals DOM
  const vitalEnergy = document.getElementById('vitalEnergy');
  const vitalMood = document.getElementById('vitalMood');
  const vitalMoodText = document.getElementById('vitalMoodText');
  const petAuraGlow = document.getElementById('petAuraGlow');

  // Games DOM
  const gameTabTtt = document.getElementById('gameTabTtt');
  const gameTabMem = document.getElementById('gameTabMem');
  const gameTabTrivia = document.getElementById('gameTabTrivia');
  const gameTttSection = document.getElementById('gameTttSection');
  const gameMemSection = document.getElementById('gameMemSection');
  const gameTriviaSection = document.getElementById('gameTriviaSection');
  const botSelfPlayToggle = document.getElementById('botSelfPlayToggle');

  // Tic-Tac-Toe Scoreboard & Difficulty DOM
  const scorePlayerEl = document.getElementById('scorePlayer');
  const scoreBotEl = document.getElementById('scoreBot');
  const scoreDrawEl = document.getElementById('scoreDraw');
  const diffPills = document.querySelectorAll('.diff-pill');

  // Trivia Streaks & Categories DOM
  const triviaStreakEl = document.getElementById('triviaStreak');
  const triviaCategoryEl = document.getElementById('triviaCategory');

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

  // Active state & Vitals
  let totalXP = parseInt(localStorage.getItem('nexus_bond_xp') || '0', 10);
  let petEnergy = 100;
  let petMood = "Happy";
  let activeAttachment = null;
  let botSelfPlayActive = false;
  let tttDifficulty = 'grandmaster';
  let tttScore = { player: 0, bot: 0, draw: 0 };
  let triviaStreak = 0;
  let conversationHistory = [
    { role: 'assistant', content: "Raiyan coded me! I am NEXUS, your personal autonomous AI companion. Ask me anything, attach multi-page PDFs, Word docs, PowerPoint presentations, spreadsheets, or code, snap photos with your camera, or play games!" }
  ];

  function updateVitals() {
    if (vitalEnergy) vitalEnergy.style.width = `${Math.max(5, Math.min(100, petEnergy))}%`;
    if (vitalMood) {
      const moodVal = petEnergy > 60 ? 95 : (petEnergy > 30 ? 65 : 40);
      vitalMood.style.width = `${moodVal}%`;
    }
    if (vitalMoodText) vitalMoodText.textContent = petMood;
  }


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

  // Canvas Pet Animation Engine (Desktop Vector Fidelity)
  const canvas = document.getElementById('mobilePetCanvas');
  const ctx = canvas.getContext('2d');
  let petAnimTime = 0;
  let petSquish = 1.0;
  let cursorX = 180, cursorY = 145;
  let targetLookX = 0, targetLookY = 0;
  let currentLookX = 0, currentLookY = 0;
  let particles = [];

  // Track pointer for smooth gaze tracking
  window.addEventListener('pointermove', (e) => {
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    cursorX = e.clientX - rect.left;
    cursorY = e.clientY - rect.top;
  });

  canvas.addEventListener('touchmove', (e) => {
    if (e.touches && e.touches[0]) {
      const rect = canvas.getBoundingClientRect();
      cursorX = e.touches[0].clientX - rect.left;
      cursorY = e.touches[0].clientY - rect.top;
    }
  }, { passive: true });

  function updateAuraGlow() {
    if (!petAuraGlow) return;
    const p = currentSkin.primary;
    const s = currentSkin.secondary || '#38bdf8';
    petAuraGlow.style.background = `radial-gradient(circle, ${p}33 0%, ${s}18 50%, transparent 75%)`;
  }

  function drawPet() {
    petAnimTime += 0.045;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const cx = canvas.width / 2;
    const cy = canvas.height / 2 + Math.sin(petAnimTime * 2.2) * 6;
    
    // Gaze tracking physics (smooth dampening)
    targetLookX = Math.max(-1, Math.min(1, (cursorX - cx) / 100));
    targetLookY = Math.max(-1, Math.min(1, (cursorY - cy) / 80));
    currentLookX += (targetLookX - currentLookX) * 0.12;
    currentLookY += (targetLookY - currentLookY) * 0.12;

    const lookOx = currentLookX * 8.0;
    const lookOy = currentLookY * 6.0;

    const isHabibi = (currentSkin.archetype === 'habibi' || currentSkin.name === 'habibi_dubai');

    // 1. Aerodynamic Cyber Side Fins (Behind body)
    const finFlap = Math.sin(petAnimTime * 3.8) * 3.5;
    ctx.save();
    // Left fin
    ctx.save();
    ctx.translate(cx - 52, cy - 6 + finFlap);
    ctx.rotate((-15 + finFlap) * Math.PI / 180);
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.lineTo(-22, -16);
    ctx.quadraticCurveTo(-28, 2, -14, 18);
    ctx.closePath();
    ctx.fillStyle = currentSkin.bodyBottom;
    ctx.strokeStyle = currentSkin.bodyRim;
    ctx.lineWidth = 2;
    ctx.fill();
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(-4, -2);
    ctx.lineTo(-16, -10);
    ctx.strokeStyle = currentSkin.primary;
    ctx.lineWidth = 1.5;
    ctx.stroke();
    ctx.restore();

    // Right fin
    ctx.save();
    ctx.translate(cx + 52, cy - 6 - finFlap);
    ctx.rotate((15 - finFlap) * Math.PI / 180);
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.lineTo(22, -16);
    ctx.quadraticCurveTo(28, 2, 14, 18);
    ctx.closePath();
    ctx.fillStyle = currentSkin.bodyBottom;
    ctx.strokeStyle = currentSkin.bodyRim;
    ctx.lineWidth = 2;
    ctx.fill();
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(4, -2);
    ctx.lineTo(16, -10);
    ctx.strokeStyle = currentSkin.primary;
    ctx.lineWidth = 1.5;
    ctx.stroke();
    ctx.restore();
    ctx.restore();

    // 2. White Flowing Ghutra Drapes (Shoulders) for Habibi
    if (isHabibi) {
      const sway = Math.sin(petAnimTime * 2.8) * 3.8;
      ctx.save();
      ctx.strokeStyle = 'rgba(212, 175, 55, 0.85)'; // Gold trim edge
      ctx.lineWidth = 1.8;

      // Left drape
      ctx.beginPath();
      ctx.moveTo(cx - 38, cy - 36);
      ctx.bezierCurveTo(cx - 62, cy - 10, cx - 68 + sway, cy + 24, cx - 48 + sway, cy + 54);
      ctx.bezierCurveTo(cx - 40, cy + 44, cx - 35, cy + 10, cx - 36, cy - 20);
      ctx.closePath();
      const gradL = ctx.createLinearGradient(cx - 65, cy, cx - 35, cy);
      gradL.addColorStop(0, 'rgba(240, 244, 250, 0.95)');
      gradL.addColorStop(1, '#ffffff');
      ctx.fillStyle = gradL;
      ctx.fill();
      ctx.stroke();

      // Right drape
      ctx.beginPath();
      ctx.moveTo(cx + 38, cy - 36);
      ctx.bezierCurveTo(cx + 62, cy - 10, cx + 68 - sway, cy + 24, cx + 48 - sway, cy + 54);
      ctx.bezierCurveTo(cx + 40, cy + 44, cx + 35, cy + 10, cx + 36, cy - 20);
      ctx.closePath();
      const gradR = ctx.createLinearGradient(cx + 35, cy, cx + 65, cy);
      gradR.addColorStop(0, '#ffffff');
      gradR.addColorStop(1, 'rgba(240, 244, 250, 0.95)');
      ctx.fillStyle = gradR;
      ctx.fill();
      ctx.stroke();
      ctx.restore();
    }

    // 3. Main Body Chassis (Titanium / Ceramic Orb)
    const bw = 110 * petSquish;
    const bh = 100 * (2.0 - petSquish);
    const bx = cx - bw / 2;
    const by = cy - bh / 2;

    ctx.save();
    ctx.beginPath();
    // Rounded rect
    const radius = 45;
    ctx.moveTo(bx + radius, by);
    ctx.lineTo(bx + bw - radius, by);
    ctx.quadraticCurveTo(bx + bw, by, bx + bw, by + radius);
    ctx.lineTo(bx + bw, by + bh - radius);
    ctx.quadraticCurveTo(bx + bw, by + bh, bx + bw - radius, by + bh);
    ctx.lineTo(bx + radius, by + bh);
    ctx.quadraticCurveTo(bx, by + bh, bx, by + bh - radius);
    ctx.lineTo(bx, by + radius);
    ctx.quadraticCurveTo(bx, by, bx + radius, by);
    ctx.closePath();

    const bodyGrad = ctx.createRadialGradient(cx, cy - 20, 15, cx, cy, 65);
    bodyGrad.addColorStop(0, currentSkin.bodyBottom);
    bodyGrad.addColorStop(0.7, currentSkin.bodyTop);
    bodyGrad.addColorStop(1, currentSkin.bodyRim);
    ctx.fillStyle = bodyGrad;
    ctx.shadowColor = currentSkin.primary;
    ctx.shadowBlur = 18;
    ctx.fill();
    ctx.shadowBlur = 0;
    ctx.strokeStyle = currentSkin.bodyRim;
    ctx.lineWidth = 2.5;
    ctx.stroke();
    ctx.restore();

    // Archetype ears / horns
    if (currentSkin.archetype === 'fox') {
      // Kitsune Fox Cyber Ears
      ctx.save();
      ctx.fillStyle = currentSkin.primary;
      ctx.beginPath();
      ctx.moveTo(cx - 36, cy - 38);
      ctx.lineTo(cx - 62, cy - 82);
      ctx.lineTo(cx - 18, cy - 54);
      ctx.closePath();
      ctx.fill();
      ctx.fillStyle = '#ffffff';
      ctx.beginPath();
      ctx.moveTo(cx - 38, cy - 42);
      ctx.lineTo(cx - 54, cy - 74);
      ctx.lineTo(cx - 24, cy - 52);
      ctx.closePath();
      ctx.fill();

      ctx.fillStyle = currentSkin.primary;
      ctx.beginPath();
      ctx.moveTo(cx + 36, cy - 38);
      ctx.lineTo(cx + 62, cy - 82);
      ctx.lineTo(cx + 18, cy - 54);
      ctx.closePath();
      ctx.fill();
      ctx.fillStyle = '#ffffff';
      ctx.beginPath();
      ctx.moveTo(cx + 38, cy - 42);
      ctx.lineTo(cx + 54, cy - 74);
      ctx.lineTo(cx + 24, cy - 52);
      ctx.closePath();
      ctx.fill();
      ctx.restore();
    } else if (currentSkin.archetype === 'cat') {
      ctx.fillStyle = currentSkin.primary;
      ctx.beginPath();
      ctx.moveTo(cx - 32, cy - 42);
      ctx.lineTo(cx - 48, cy - 76);
      ctx.lineTo(cx - 14, cy - 56);
      ctx.fill();
      ctx.beginPath();
      ctx.moveTo(cx + 32, cy - 42);
      ctx.lineTo(cx + 48, cy - 76);
      ctx.lineTo(cx + 14, cy - 56);
      ctx.fill();
    }

    // 4. Curved High-Gloss OLED Visor
    const vw = 86;
    const vh = 66;
    const vx = cx - vw / 2;
    const vy = cy - 34;

    ctx.save();
    ctx.beginPath();
    const vRad = 22;
    ctx.moveTo(vx + vRad, vy);
    ctx.lineTo(vx + vw - vRad, vy);
    ctx.quadraticCurveTo(vx + vw, vy, vx + vw, vy + vRad);
    ctx.lineTo(vx + vw, vy + vh - vRad);
    ctx.quadraticCurveTo(vx + vw, vy + vh, vx + vw - vRad, vy + vh);
    ctx.lineTo(vx + vRad, vy + vh);
    ctx.quadraticCurveTo(vx, vy + vh, vx, vy + vh - vRad);
    ctx.lineTo(vx, vy + vRad);
    ctx.quadraticCurveTo(vx, vy, vx + vRad, vy);
    ctx.closePath();

    const visorGrad = ctx.createLinearGradient(cx, vy, cx, vy + vh);
    visorGrad.addColorStop(0, '#10141f');
    visorGrad.addColorStop(0.7, '#070a12');
    visorGrad.addColorStop(1, '#020408');
    ctx.fillStyle = visorGrad;
    ctx.fill();
    ctx.strokeStyle = isHabibi ? '#fbbf24' : currentSkin.primary;
    ctx.lineWidth = 1.8;
    ctx.stroke();

    // Gloss sheen reflection
    ctx.beginPath();
    ctx.moveTo(cx - 34, vy + 6);
    ctx.quadraticCurveTo(cx, vy + 2, cx + 34, vy + 6);
    ctx.quadraticCurveTo(cx, vy + 9, cx - 34, vy + 6);
    ctx.fillStyle = isHabibi ? 'rgba(255, 235, 160, 0.25)' : 'rgba(255, 255, 255, 0.25)';
    ctx.fill();
    ctx.restore();

    // 5. Habibi Ghutra Canopy & Double Black Agal Cord
    if (isHabibi) {
      ctx.save();
      // White canopy wrapping crown
      ctx.beginPath();
      ctx.moveTo(cx - 48, cy - 34);
      ctx.bezierCurveTo(cx - 50, cy - 58, cx - 25, cy - 65, cx, cy - 66);
      ctx.bezierCurveTo(cx + 25, cy - 65, cx + 50, cy - 58, cx + 48, cy - 34);
      ctx.quadraticCurveTo(cx, cy - 40, cx - 48, cy - 34);
      ctx.closePath();
      const gGrad = ctx.createLinearGradient(cx, cy - 66, cx, cy - 34);
      gGrad.addColorStop(0, '#ffffff');
      gGrad.addColorStop(1, '#f1f5f9');
      ctx.fillStyle = gGrad;
      ctx.fill();
      ctx.strokeStyle = 'rgba(212, 175, 55, 0.85)';
      ctx.lineWidth = 1.2;
      ctx.stroke();

      // Double black Agal cord rings
      ctx.lineCap = 'round';
      ctx.strokeStyle = '#12141a';
      ctx.lineWidth = 5.5;
      ctx.beginPath();
      ctx.moveTo(cx - 40, cy - 52);
      ctx.quadraticCurveTo(cx, cy - 57, cx + 40, cy - 52);
      ctx.stroke();

      ctx.strokeStyle = '#1a1d26';
      ctx.lineWidth = 5.0;
      ctx.beginPath();
      ctx.moveTo(cx - 42, cy - 46);
      ctx.quadraticCurveTo(cx, cy - 51, cx + 42, cy - 46);
      ctx.stroke();

      // Gold clasp bands on Agal
      ctx.strokeStyle = '#fbbf24';
      ctx.lineWidth = 2.5;
      ctx.beginPath();
      ctx.moveTo(cx - 22, cy - 55);
      ctx.lineTo(cx - 22, cy - 44);
      ctx.moveTo(cx + 22, cy - 55);
      ctx.lineTo(cx + 22, cy - 44);
      ctx.stroke();

      // Royal Gold Diamond Crest
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

    // 6. Eyes / Face with Dynamic Gaze Tracking
    const eyeY = cy - 4 + lookOy;
    const leftEyeX = cx - 18 + lookOx;
    const rightEyeX = cx + 18 + lookOx;
    const isBlinking = (Math.sin(petAnimTime * 0.7) > 0.96);

    if (isHabibi) {
      // Luxury Gold Aviator Sunglasses
      const aw = 20, ah = 17;
      ctx.save();
      // Gold top brow bar connecting lenses
      ctx.strokeStyle = '#fbbf24';
      ctx.lineWidth = 2.2;
      ctx.beginPath();
      ctx.moveTo(leftEyeX + 4, eyeY - 8);
      ctx.lineTo(rightEyeX - 4, eyeY - 8);
      ctx.stroke();

      // Lenses
      for (const lx of [leftEyeX, rightEyeX]) {
        ctx.beginPath();
        ctx.moveTo(lx - aw / 2, eyeY - ah / 2);
        ctx.lineTo(lx + aw / 2, eyeY - ah / 2);
        ctx.bezierCurveTo(lx + aw / 2, eyeY + ah / 2, lx + aw / 4, eyeY + ah / 2 + 2, lx, eyeY + ah / 2 + 2);
        ctx.bezierCurveTo(lx - aw / 4, eyeY + ah / 2 + 2, lx - aw / 2, eyeY + ah / 2, lx - aw / 2, eyeY - ah / 2);
        ctx.closePath();

        const lensGrad = ctx.createLinearGradient(lx, eyeY - ah, lx, eyeY + ah);
        lensGrad.addColorStop(0, 'rgba(28, 22, 14, 0.95)');
        lensGrad.addColorStop(0.6, 'rgba(10, 8, 4, 0.98)');
        lensGrad.addColorStop(1, 'rgba(32, 25, 16, 0.95)');
        ctx.fillStyle = lensGrad;
        ctx.fill();
        ctx.strokeStyle = '#fbbf24';
        ctx.lineWidth = 1.8;
        ctx.stroke();

        // Diagonal gold mirror reflection glint
        ctx.beginPath();
        ctx.moveTo(lx - aw / 3, eyeY - ah / 2 + 2);
        ctx.lineTo(lx - aw / 4, eyeY - ah / 2 + 2);
        ctx.lineTo(lx + aw / 3, eyeY + ah / 2 - 2);
        ctx.lineTo(lx + aw / 4, eyeY + ah / 2 - 2);
        ctx.closePath();
        ctx.fillStyle = 'rgba(255, 235, 160, 0.45)';
        ctx.fill();
      }

      // Glowing amber pupils visible through shades
      if (!isBlinking) {
        ctx.fillStyle = 'rgba(251, 191, 36, 0.88)';
        ctx.shadowColor = '#fbbf24';
        ctx.shadowBlur = 8;
        ctx.beginPath();
        ctx.arc(leftEyeX, eyeY, 4.2, 0, Math.PI * 2);
        ctx.arc(rightEyeX, eyeY, 4.2, 0, Math.PI * 2);
        ctx.fill();
        ctx.shadowBlur = 0;
      }

      // Corner glint star on frames
      ctx.fillStyle = '#ffffff';
      const gx = rightEyeX + aw / 2;
      const gy = eyeY - ah / 2;
      ctx.beginPath();
      ctx.arc(gx, gy, 1.8, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();
    } else {
      // Standard Expressive Eyes
      ctx.save();
      if (isBlinking) {
        ctx.strokeStyle = currentSkin.primary;
        ctx.lineWidth = 3.2;
        ctx.lineCap = 'round';
        ctx.beginPath();
        ctx.moveTo(leftEyeX - 8, eyeY);
        ctx.lineTo(leftEyeX + 8, eyeY);
        ctx.moveTo(rightEyeX - 8, eyeY);
        ctx.lineTo(rightEyeX + 8, eyeY);
        ctx.stroke();
      } else {
        ctx.fillStyle = currentSkin.primary;
        ctx.shadowColor = currentSkin.primary;
        ctx.shadowBlur = 10;
        ctx.beginPath();
        ctx.ellipse(leftEyeX, eyeY, 7.5, 10.5, 0, 0, Math.PI * 2);
        ctx.ellipse(rightEyeX, eyeY, 7.5, 10.5, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.shadowBlur = 0;
        // Specular eye shine
        ctx.fillStyle = '#ffffff';
        ctx.beginPath();
        ctx.arc(leftEyeX - 2.5, eyeY - 3.5, 2.4, 0, Math.PI * 2);
        ctx.arc(rightEyeX - 2.5, eyeY - 3.5, 2.4, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.restore();
    }

    // 7. Rosy Cheeks Blush
    ctx.save();
    ctx.fillStyle = 'rgba(255, 110, 150, 0.45)';
    ctx.beginPath();
    ctx.ellipse(cx - 27 + lookOx * 0.5, cy + 11 + lookOy * 0.5, 6.8, 4.0, 0, 0, Math.PI * 2);
    ctx.ellipse(cx + 27 + lookOx * 0.5, cy + 11 + lookOy * 0.5, 6.8, 4.0, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();

    // 8. Dynamic Equalizer Mouth / Smile
    const isSpeaking = (window.speechSynthesis && window.speechSynthesis.speaking);
    ctx.save();
    if (isSpeaking) {
      // 5 jumping audio equalizer bars
      const barY = cy + 17;
      ctx.fillStyle = isHabibi ? '#fbbf24' : currentSkin.primary;
      for (let i = 0; i < 5; i++) {
        const bx = cx - 14 + i * 7;
        const bh = 3.0 + Math.abs(Math.sin(petAnimTime * 8.0 + i * 1.3)) * 11.0;
        ctx.beginPath();
        ctx.roundRect ? ctx.roundRect(bx - 1.5, barY - bh / 2, 3.5, bh, 2) : ctx.rect(bx - 1.5, barY - bh / 2, 3.5, bh);
        ctx.fill();
      }
    } else {
      // Warm smile arc
      ctx.strokeStyle = isHabibi ? '#fbbf24' : currentSkin.primary;
      ctx.lineWidth = 2.4;
      ctx.lineCap = 'round';
      ctx.beginPath();
      ctx.arc(cx, cy + 13, 8.5, 0.15 * Math.PI, 0.85 * Math.PI);
      ctx.stroke();
    }
    ctx.restore();

    // 9. Floating Burst Particles
    for (let i = particles.length - 1; i >= 0; i--) {
      const p = particles[i];
      p.x += p.vx;
      p.y += p.vy;
      p.life -= 0.025;
      if (p.life <= 0) {
        particles.splice(i, 1);
        continue;
      }
      ctx.save();
      ctx.fillStyle = p.color;
      ctx.globalAlpha = p.life;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();
    }

    if (petSquish < 1.0) petSquish += 0.035;
    requestAnimationFrame(drawPet);
  }
  requestAnimationFrame(drawPet);
  updateAuraGlow();

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
    petEnergy = Math.max(10, petEnergy - 2);
    petMood = "Loving";
    updateVitals();
    spawnBurst('heart', 14);
    playTone(650, 'sine', 0.12);
    addXP(5, "Petting Companion");
    updateBubble("Hehehe, that tickles! 💖 Affection acknowledged!");
  });

  // Pet Action Bar Buttons
  petBtn.addEventListener('click', () => {
    petSquish = 0.84;
    petEnergy = Math.max(10, petEnergy - 3);
    petMood = "Happy";
    updateVitals();
    spawnBurst('heart', 16);
    addXP(5, "Petting");
    updateBubble("I feel loved and happy! 💖 (+5 XP)");
  });

  highFiveBtn.addEventListener('click', () => {
    spawnBurst('sparkle', 20);
    petEnergy = Math.max(10, petEnergy - 4);
    petMood = "Excited";
    updateVitals();
    playTone(800, 'triangle', 0.15);
    addXP(10, "High-Five");
    updateBubble("High five! ✋ Unstoppable teamwork! (+10 XP)");
  });

  cheerBtn.addEventListener('click', () => {
    spawnBurst('star', 22);
    petEnergy = Math.max(10, petEnergy - 2);
    petMood = "Inspired";
    updateVitals();
    addXP(5, "Cheer");
    updateBubble("You've got this! Reaching for the stars! ⭐ (+5 XP)");
  });

  karakBtn.addEventListener('click', () => {
    spawnBurst('sparkle', 24);
    petEnergy = Math.min(100, petEnergy + 20);
    petMood = "Energized";
    updateVitals();
    addXP(15, "Karak Chai");
    updateBubble("Ah, a steaming royal cup of Karak Chai! ☕ Pure energy! (+15 XP)");
  });

  danceBtn.addEventListener('click', () => {
    petSquish = 0.75;
    petEnergy = Math.max(10, petEnergy - 8);
    petMood = "Playful";
    updateVitals();
    spawnBurst('star', 25);
    addXP(10, "Dance");
    updateBubble("Look at those autonomous moves! 💃 (+10 XP)");
  });

  if (restBtn) {
    restBtn.addEventListener('click', () => {
      petEnergy = Math.min(100, petEnergy + 30);
      petMood = "Refueled & Fresh";
      updateVitals();
      playTone(440, 'triangle', 0.2);
      spawnBurst('sparkle', 15);
      addXP(10, "Rest");
      updateBubble("💤 NEXUS took a power rest! Core battery recharged! (+10 XP)");
    });
  }

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
        updateAuraGlow();
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


  // --- 7. Multi-Format Document, Slide & Spreadsheet Extractors ---
  async function parseDocx(file) {
    if (typeof JSZip === 'undefined') throw new Error("JSZip not available");
    const zip = await JSZip.loadAsync(file);
    const docFile = zip.file("word/document.xml");
    if (!docFile) throw new Error("word/document.xml not found in DOCX");
    const docXml = await docFile.async("string");
    const parser = new DOMParser();
    const xmlDoc = parser.parseFromString(docXml, "text/xml");
    const paragraphs = xmlDoc.getElementsByTagName("w:p");
    let textOut = [];
    for (let i = 0; i < paragraphs.length; i++) {
      const p = paragraphs[i];
      let pText = "";
      const textNodes = p.getElementsByTagName("w:t");
      for (let j = 0; j < textNodes.length; j++) {
        pText += textNodes[j].textContent;
      }
      if (pText.trim()) textOut.push(pText.trim());
    }
    return textOut.join("\n\n");
  }

  async function parsePptx(file) {
    if (typeof JSZip === 'undefined') throw new Error("JSZip not available");
    const zip = await JSZip.loadAsync(file);
    const parser = new DOMParser();
    let slidesText = [];
    let slideIdx = 1;
    while (true) {
      const slideFile = zip.file(`ppt/slides/slide${slideIdx}.xml`);
      if (!slideFile) break;
      const slideXml = await slideFile.async("string");
      const xmlDoc = parser.parseFromString(slideXml, "text/xml");
      const paragraphs = xmlDoc.getElementsByTagName("a:p");
      let slideText = [];
      for (let i = 0; i < paragraphs.length; i++) {
        const p = paragraphs[i];
        let pText = "";
        const textNodes = p.getElementsByTagName("a:t");
        for (let j = 0; j < textNodes.length; j++) {
          pText += textNodes[j].textContent;
        }
        if (pText.trim()) slideText.push(pText.trim());
      }
      if (slideText.length > 0) {
        slidesText.push(`--- Slide ${slideIdx} ---\n${slideText.join("\n")}`);
      }
      slideIdx++;
    }
    if (slidesText.length === 0) throw new Error("No slide content extracted");
    return slidesText.join("\n\n");
  }

  async function parseXlsx(file) {
    if (typeof JSZip === 'undefined') throw new Error("JSZip not available");
    const zip = await JSZip.loadAsync(file);
    const parser = new DOMParser();
    let sharedStrings = [];
    const ssFile = zip.file("xl/sharedStrings.xml");
    if (ssFile) {
      const ssXml = await ssFile.async("string");
      const xmlDoc = parser.parseFromString(ssXml, "text/xml");
      const siNodes = xmlDoc.getElementsByTagName("si");
      for (let i = 0; i < siNodes.length; i++) {
        let str = "";
        const tNodes = siNodes[i].getElementsByTagName("t");
        for (let j = 0; j < tNodes.length; j++) str += tNodes[j].textContent;
        sharedStrings.push(str);
      }
    }
    const sheetFile = zip.file("xl/worksheets/sheet1.xml");
    if (!sheetFile) return "Excel file attached (Empty sheet).";
    const sheetXml = await sheetFile.async("string");
    const xmlDoc = parser.parseFromString(sheetXml, "text/xml");
    const rowNodes = xmlDoc.getElementsByTagName("row");
    let rowsOut = [];
    for (let i = 0; i < Math.min(rowNodes.length, 100); i++) {
      const r = rowNodes[i];
      let cells = [];
      const cNodes = r.getElementsByTagName("c");
      for (let j = 0; j < cNodes.length; j++) {
        const c = cNodes[j];
        const type = c.getAttribute("t");
        const vNode = c.getElementsByTagName("v")[0];
        let val = vNode ? vNode.textContent : "";
        if (type === "s" && sharedStrings[parseInt(val, 10)]) {
          val = sharedStrings[parseInt(val, 10)];
        }
        cells.push(val);
      }
      if (cells.some(x => x.trim())) rowsOut.push(cells.join(" | "));
    }
    return rowsOut.join("\n");
  }

  function extractPrintableStrings(buffer) {
    const bytes = new Uint8Array(buffer);
    let str = "";
    for (let i = 0; i < bytes.length; i++) {
      const b = bytes[i];
      if (b >= 32 && b <= 126) str += String.fromCharCode(b);
      else if (b === 10 || b === 13 || b === 9) str += " ";
      else str += "\x00";
    }
    const chunks = str.split("\x00").map(s => s.trim()).filter(s => s.length >= 4);
    return chunks.slice(0, 500).join(" ");
  }

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
    // 2. Word Document (.docx / .doc)
    else if (ext === 'docx' || ext === 'doc') {
      attIcon.textContent = '📄';
      attachmentStrip.style.display = 'block';
      updateBubble(`Unpacking Word document "${file.name}"...`);
      try {
        let content = "";
        if (ext === 'docx') {
          content = await parseDocx(file);
        } else {
          const buf = await file.arrayBuffer();
          content = extractPrintableStrings(buf);
        }
        activeAttachment = {
          name: file.name,
          type: `Word Document (.${ext})`,
          size: Math.round(file.size / 1024),
          content: content || `[Empty Word Document: ${file.name}]`
        };
        updateBubble(`✅ Read Word document "${file.name}"! Ready to inspect.`);
      } catch (err) {
        console.warn("Word extract fallback:", err);
        const buf = await file.arrayBuffer();
        const content = extractPrintableStrings(buf);
        activeAttachment = {
          name: file.name,
          type: `Word Document (.${ext})`,
          size: Math.round(file.size / 1024),
          content: content
        };
        updateBubble(`Attached "${file.name}". Ready to ask questions!`);
      }
    }
    // 3. PowerPoint Presentations (.pptx / .ppt)
    else if (ext === 'pptx' || ext === 'ppt') {
      attIcon.textContent = '📊';
      attachmentStrip.style.display = 'block';
      updateBubble(`Extracting slides from "${file.name}"...`);
      try {
        let content = "";
        if (ext === 'pptx') {
          content = await parsePptx(file);
        } else {
          const buf = await file.arrayBuffer();
          content = extractPrintableStrings(buf);
        }
        activeAttachment = {
          name: file.name,
          type: `PowerPoint Slides (.${ext})`,
          size: Math.round(file.size / 1024),
          content: content
        };
        updateBubble(`✅ Extracted presentation slides from "${file.name}"!`);
      } catch (err) {
        console.warn("PPT extract fallback:", err);
        const buf = await file.arrayBuffer();
        activeAttachment = {
          name: file.name,
          type: `PowerPoint Slides (.${ext})`,
          size: Math.round(file.size / 1024),
          content: extractPrintableStrings(buf)
        };
        updateBubble(`Attached presentation "${file.name}". Ready to analyze!`);
      }
    }
    // 4. Excel Spreadsheets (.xlsx / .xls)
    else if (ext === 'xlsx' || ext === 'xls') {
      attIcon.textContent = '📈';
      attachmentStrip.style.display = 'block';
      updateBubble(`Parsing spreadsheet tables from "${file.name}"...`);
      try {
        let content = "";
        if (ext === 'xlsx') {
          content = await parseXlsx(file);
        } else {
          const buf = await file.arrayBuffer();
          content = extractPrintableStrings(buf);
        }
        activeAttachment = {
          name: file.name,
          type: `Spreadsheet (.${ext})`,
          size: Math.round(file.size / 1024),
          content: content
        };
        updateBubble(`✅ Loaded spreadsheet tables from "${file.name}"!`);
      } catch (err) {
        console.warn("Excel extract fallback:", err);
        const buf = await file.arrayBuffer();
        activeAttachment = {
          name: file.name,
          type: `Spreadsheet (.${ext})`,
          size: Math.round(file.size / 1024),
          content: extractPrintableStrings(buf)
        };
        updateBubble(`Attached spreadsheet "${file.name}".`);
      }
    }
    // 5. Code, Markdown, JSON, Text, CSV Documents
    else {
      attIcon.textContent = (ext === 'csv') ? '📊' : (['py', 'js', 'html', 'css', 'ts', 'sql', 'json'].includes(ext) ? '💻' : '📄');
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

    let promptText = query;
    if (attCopy && attCopy.content) {
      promptText = `[Attached File: "${attCopy.name}" (${attCopy.type})]:\n${attCopy.content.substring(0, 16000)}\n\n${query || "Please analyze, explain, and summarize this attached document in detail."}`;
    } else if (attCopy && attCopy.isImage) {
      promptText = query || "Please analyze this attached photo in detail and describe what you see.";
    }
    conversationHistory.push({ role: 'user', content: promptText });

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

  // Quick Prompt Suggestion Chips
  document.querySelectorAll('.chat-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      const prompt = chip.getAttribute('data-prompt');
      if (prompt) {
        chatInput.value = prompt;
        handleSend();
      }
    });
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

  // Difficulty pills selector
  diffPills.forEach(pill => {
    pill.addEventListener('click', () => {
      diffPills.forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      tttDifficulty = pill.dataset.diff;
      playTone(550, 'sine', 0.08);
      updateBubble(`AI Difficulty set to ${pill.textContent}!`);
    });
  });

  // 1. Tic-Tac-Toe Game with Minimax AI & Self-Play
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

  function getBestTttMove(board, player, diff) {
    const emptyCells = board.map((v, i) => v === '' ? i : null).filter(v => v !== null);
    if (emptyCells.length === 0) return null;

    if (diff === 'casual' && Math.random() < 0.5) {
      return emptyCells[Math.floor(Math.random() * emptyCells.length)];
    }
    if (diff === 'tactical' && Math.random() < 0.25) {
      return emptyCells[Math.floor(Math.random() * emptyCells.length)];
    }

    const opponent = (player === 'O') ? 'X' : 'O';

    function minimax(b, depth, isMax) {
      const winner = checkTttWinner(b);
      if (winner === player) return 10 - depth;
      if (winner === opponent) return depth - 10;
      if (winner === 'Tie') return 0;
      if (depth >= 6) return 0;

      const avail = b.map((v, i) => v === '' ? i : null).filter(v => v !== null);

      if (isMax) {
        let best = -Infinity;
        for (const idx of avail) {
          b[idx] = player;
          best = Math.max(best, minimax(b, depth + 1, false));
          b[idx] = '';
        }
        return best;
      } else {
        let best = Infinity;
        for (const idx of avail) {
          b[idx] = opponent;
          best = Math.min(best, minimax(b, depth + 1, true));
          b[idx] = '';
        }
        return best;
      }
    }

    let bestMove = emptyCells[0];
    let bestVal = -Infinity;
    for (const idx of emptyCells) {
      board[idx] = player;
      const moveVal = minimax(board, 0, false);
      board[idx] = '';
      if (moveVal > bestVal) {
        bestVal = moveVal;
        bestMove = idx;
      }
    }
    return bestMove;
  }

  // Autonomous Bot Self-Play Toggle
  botSelfPlayToggle.addEventListener('change', (e) => {
    botSelfPlayActive = e.target.checked;
    if (botSelfPlayActive) {
      playTone(750, 'triangle', 0.2);
      updateBubble("🤖 Bot Self-Play activated! NEXUS-Alpha & Omega will battle autonomously!");
      runBotSelfPlayStep();
    } else {
      updateBubble("Bot Self-Play paused.");
    }
  });

  function runBotSelfPlayStep() {
    if (!botSelfPlayActive) return;

    if (gameTttSection.style.display !== 'none') {
      if (tttGameOver) {
        setTimeout(() => {
          if (botSelfPlayActive) {
            resetTtt();
            setTimeout(runBotSelfPlayStep, 700);
          }
        }, 1600);
        return;
      } else {
        const move = getBestTttMove(tttBoard, tttCurrentPlayer, 'tactical');
        if (move !== null) {
          if (tttCurrentPlayer === 'X') {
            tttDialogue.textContent = `NEXUS-Alpha 🤖: "Executing tactical grid flank at position ${move + 1}!"`;
          } else {
            tttDialogue.textContent = `NEXUS-Omega ⚡: "Calculating counter-defense at position ${move + 1}!"`;
          }
          makeTttMove(move, tttCurrentPlayer);
        }
      }
    }

    setTimeout(runBotSelfPlayStep, 950);
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
        tttScore.draw++;
        if (scoreDrawEl) scoreDrawEl.textContent = tttScore.draw;
        addXP(10, "Tic-Tac-Toe Tie");
      } else if (winner === 'X') {
        const title = botSelfPlayActive ? "NEXUS-Alpha 🤖 Wins!" : "🏆 Player X Wins!";
        tttStatus.textContent = title;
        tttDialogue.textContent = botSelfPlayActive
          ? 'NEXUS-Alpha: "Neural victory! Grid dominance achieved."'
          : 'NEXUS: "Incredible flank! You pierced my Minimax heuristics!"';
        spawnBurst('star', 20);
        tttScore.player++;
        if (scorePlayerEl) scorePlayerEl.textContent = tttScore.player;
        addXP(25, "Tic-Tac-Toe Win");
      } else {
        const title = botSelfPlayActive ? "NEXUS-Omega ⚡ Wins!" : "🤖 NEXUS (O) Wins!";
        tttStatus.textContent = title;
        tttDialogue.textContent = botSelfPlayActive
          ? 'NEXUS-Omega: "Flank blocked, counter-offensive executed!"'
          : 'NEXUS: "Three in a row! Tactical victory."';
        tttScore.bot++;
        if (scoreBotEl) scoreBotEl.textContent = tttScore.bot;
        addXP(15, "Tic-Tac-Toe Match");
      }
      return;
    }

    tttCurrentPlayer = (player === 'X') ? 'O' : 'X';
    tttStatus.textContent = `Turn: Player ${tttCurrentPlayer}`;

    // Pet AI counter-move if playing human vs pet
    if (!botSelfPlayActive && tttCurrentPlayer === 'O' && !tttGameOver) {
      setTimeout(() => {
        const petMove = getBestTttMove(tttBoard, 'O', tttDifficulty);
        if (petMove !== null) {
          makeTttMove(petMove, 'O');
        }
      }, 450);
    }
  }

  tttCells.forEach(cell => {
    cell.addEventListener('click', () => {
      if (botSelfPlayActive) return;
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
    tttDialogue.textContent = 'NEXUS: "Minimax game tree loaded. Let\'s see your best move!"';
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

  // 3. AI Brain Trivia Quiz Suite
  const TRIVIA = [
    // Science & Biology
    {
      cat: "Science & Nature",
      q: "Which gas is released by green plants during photosynthesis?",
      opts: ["Oxygen (O2)", "Carbon Dioxide", "Helium", "Methane"],
      ans: 0,
      exp: "Plants convert CO2 and water into glucose and Oxygen!"
    },
    {
      cat: "Science & Nature",
      q: "What is the powerhouse organelle of eukaryotic cells responsible for producing ATP?",
      opts: ["Ribosome", "Mitochondria", "Endoplasmic Reticulum", "Golgi"],
      ans: 1,
      exp: "Mitochondria generate most cellular ATP via oxidative phosphorylation."
    },
    {
      cat: "Science & Nature",
      q: "What is the chemical symbol and atomic number of Gold?",
      opts: ["Ag (47)", "Fe (26)", "Au (79)", "Pt (78)"],
      ans: 2,
      exp: "Gold is Au (from Latin 'aurum') with atomic number 79."
    },
    // Space & Cosmos
    {
      cat: "Space & Universe",
      q: "What is the universal gravitational constant symbolized by?",
      opts: ["g", "G", "C", "h"],
      ans: 1,
      exp: "Capital G represents the universal gravitational constant in Newton's law: F = G*(m1*m2)/r^2."
    },
    {
      cat: "Space & Universe",
      q: "Which planet in our solar system has the shortest orbital period around the Sun?",
      opts: ["Mercury (88 days)", "Venus", "Mars", "Jupiter"],
      ans: 0,
      exp: "Mercury completes one orbit in approximately 88 Earth days."
    },
    {
      cat: "Space & Universe",
      q: "What is the point of no return surrounding a black hole where light cannot escape?",
      opts: ["Photon Sphere", "Ergosphere", "Event Horizon", "Accretion Disk"],
      ans: 2,
      exp: "The event horizon is the boundary beyond which escape velocity exceeds the speed of light."
    },
    // Computer Science & AI
    {
      cat: "Computer Science & AI",
      q: "Who coded the NEXUS AI Companion architecture?",
      opts: ["Raiyan", "Anonymous", "OpenAI", "NASA"],
      ans: 0,
      exp: "Raiyan coded me! I am NEXUS, your personal autonomous AI companion."
    },
    {
      cat: "Computer Science & AI",
      q: "In Python, which built-in function returns the number of items in a sequence?",
      opts: ["count()", "size()", "len()", "length()"],
      ans: 2,
      exp: "len() is the standard Python built-in to return length in O(1) time."
    },
    {
      cat: "Computer Science & AI",
      q: "Which architecture introduced self-attention mechanisms in modern LLMs?",
      opts: ["Transformer", "RNN", "Markov Chain", "Perceptron"],
      ans: 0,
      exp: "The Transformer architecture (Vaswani et al., 2017) revolutionized AI with parallelized self-attention."
    },
    {
      cat: "Computer Science & AI",
      q: "What is the average time complexity of QuickSort on randomized input arrays?",
      opts: ["O(n)", "O(n log n)", "O(n²)", "O(log n)"],
      ans: 1,
      exp: "QuickSort and MergeSort run in O(n log n) average time complexity."
    },
    // World History
    {
      cat: "World History",
      q: "In which ancient civilization was the Great Pyramid of Giza constructed?",
      opts: ["Mesopotamia", "Ancient Egypt", "Ancient Greece", "Indus Valley"],
      ans: 1,
      exp: "Built during Egypt's Fourth Dynasty for Pharaoh Khufu circa 2560 BCE."
    },
    {
      cat: "World History",
      q: "Which invention by Johannes Gutenberg revolutionized book publishing in 1440?",
      opts: ["Steam Engine", "Movable Type Press", "The Astrolabe", "Compass"],
      ans: 1,
      exp: "Gutenberg's movable type printing press democratized literacy across the globe."
    },
    // World Geography
    {
      cat: "World Geography",
      q: "What is the deepest known oceanic trench on planet Earth?",
      opts: ["Java Trench", "Puerto Rico Trench", "Mariana Trench", "Tonga Trench"],
      ans: 2,
      exp: "Challenger Deep in the Mariana Trench reaches approximately 10,994 meters."
    },
    {
      cat: "World Geography",
      q: "Which is the longest river in the world by traditional geographic consensus?",
      opts: ["The Amazon", "The Nile", "The Yangtze", "The Mississippi"],
      ans: 1,
      exp: "The Nile River spans approximately 6,650 km across northeastern Africa."
    },
    // Mathematics & Logic
    {
      cat: "Mathematics & Logic",
      q: "What is the evaluated result of Euler's identity: e^(i*pi) + 1?",
      opts: ["0", "1", "-1", "pi"],
      ans: 0,
      exp: "Euler's identity beautifully links e, i, pi, 1, and 0: e^(i*pi) + 1 = 0."
    },
    {
      cat: "Mathematics & Logic",
      q: "How many degrees are in the sum of all interior angles of a pentagon?",
      opts: ["360°", "540°", "720°", "180°"],
      ans: 1,
      exp: "(n - 2) * 180° = (5 - 2) * 180° = 540°."
    },
    // Pop Culture & Gaming
    {
      cat: "Pop Culture & Gaming",
      q: "Which video game character debuted in 1981 under the name 'Jumpman'?",
      opts: ["Sonic", "Mario", "Mega Man", "Pac-Man"],
      ans: 1,
      exp: "Mario was originally named 'Jumpman' in Donkey Kong before his legendary series began."
    }
  ];

  let currentTriviaIdx = 0;
  const triviaQuestion = document.getElementById('triviaQuestion');
  const triviaOptions = document.getElementById('triviaOptions');
  const triviaExplanation = document.getElementById('triviaExplanation');
  const triviaNextBtn = document.getElementById('triviaNextBtn');
  const triviaCategorySelect = document.getElementById('triviaCategorySelect');
  const triviaAiGenBtn = document.getElementById('triviaAiGenBtn');

  function getFilteredTrivia() {
    if (!triviaCategorySelect || triviaCategorySelect.value === 'all') {
      return TRIVIA;
    }
    const sel = triviaCategorySelect.value;
    const filtered = TRIVIA.filter(t => t.cat === sel);
    return filtered.length > 0 ? filtered : TRIVIA;
  }

  function loadTrivia(idx) {
    const pool = getFilteredTrivia();
    currentTriviaIdx = idx % pool.length;
    const item = pool[currentTriviaIdx];
    if (triviaCategoryEl) triviaCategoryEl.textContent = item.cat || "Science & Tech";
    if (triviaStreakEl) triviaStreakEl.textContent = `🔥 Streak: ${triviaStreak}`;

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
          triviaStreak++;
          if (triviaStreakEl) triviaStreakEl.textContent = `🔥 Streak: ${triviaStreak}`;
          const streakBonus = Math.min(25, triviaStreak * 5);
          triviaExplanation.textContent = `✅ Correct! (+${20 + streakBonus} XP with Streak bonus) ${item.exp}`;
          addXP(20 + streakBonus, "Trivia Correct");
          spawnBurst('star', 18);
          playTone(880, 'triangle', 0.2);
        } else {
          btn.classList.add('wrong');
          triviaStreak = 0;
          if (triviaStreakEl) triviaStreakEl.textContent = `🔥 Streak: 0`;
          triviaExplanation.textContent = `❌ Not quite. ${item.exp}`;
          playTone(280, 'sine', 0.2);
        }
      });
      triviaOptions.appendChild(btn);
    });
  }

  if (triviaCategorySelect) {
    triviaCategorySelect.addEventListener('change', () => {
      loadTrivia(0);
    });
  }

  if (triviaAiGenBtn) {
    triviaAiGenBtn.addEventListener('click', async () => {
      triviaAiGenBtn.disabled = true;
      triviaAiGenBtn.textContent = '✨ Generating...';
      const cat = triviaCategorySelect ? triviaCategorySelect.value : 'General Knowledge';
      const prompt = `Generate 1 unique multiple choice trivia question on topic '${cat === 'all' ? 'Science and Technology' : cat}'. Respond ONLY with a valid raw JSON object with keys: {"cat": "${cat === 'all' ? 'Science' : cat}", "q": "question text", "opts": ["Option 1", "Option 2", "Option 3", "Option 4"], "ans": 0, "exp": "explanation"}. No markdown backticks.`;

      try {
        const reply = await window.NexusMobileAI.queryAI(prompt, 'academic');
        const match = reply.match(/\{[\s\S]*\}/);
        if (match) {
          const newQ = JSON.parse(match[0]);
          if (newQ.q && Array.isArray(newQ.opts) && newQ.opts.length === 4 && typeof newQ.ans === 'number') {
            TRIVIA.push(newQ);
            loadTrivia(TRIVIA.length - 1);
            addXP(10, "AI Trivia Discovery");
            triviaExplanation.textContent = "✨ Fresh AI-generated question loaded! (+10 Discovery XP)";
            playTone(800, 'sine', 0.15);
          } else {
            loadTrivia(currentTriviaIdx + 1);
          }
        } else {
          loadTrivia(currentTriviaIdx + 1);
        }
      } catch (e) {
        console.warn("AI Trivia Gen Error:", e);
        loadTrivia(currentTriviaIdx + 1);
      } finally {
        triviaAiGenBtn.disabled = false;
        triviaAiGenBtn.textContent = '✨ AI Question';
      }
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
  if (settingProviderSelect) {
    const savedProv = localStorage.getItem('nexus_active_provider');
    if (savedProv) settingProviderSelect.value = savedProv;
    settingProviderSelect.addEventListener('change', () => {
      localStorage.setItem('nexus_active_provider', settingProviderSelect.value);
      updateBubble(`Active AI provider set to ${settingProviderSelect.value.toUpperCase()}!`);
    });
  }

  saveKeysBtn.addEventListener('click', () => {
    if (settingProviderSelect) {
      localStorage.setItem('nexus_active_provider', settingProviderSelect.value);
    }
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
  updateVitals();
  bubbleArchetype.textContent = `${currentSkin.icon} ${currentSkin.displayName}`;
  skinIcon.textContent = currentSkin.icon;
  skinLabel.textContent = currentSkin.displayName;
  auraBadge.textContent = `✨ ${currentSkin.displayName} Aura`;
})();
