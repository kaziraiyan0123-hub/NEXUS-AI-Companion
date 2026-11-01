/**
 * NEXUS Mobile AI Client-Side Engine v2.6
 * Multi-tier AI intelligence providing:
 * 1. Ultra-fast Groq LPU API calls (qwen/qwen3.8-27b, openai/gpt-oss-120b)
 * 2. Multi-turn conversation session memory across queries
 * 3. Document & code file context analysis
 * 4. Google Gemini 2.5 Flash API calls
 * 5. OpenRouter Free Tier API calls
 * 6. Deep Offline Intelligent Knowledge Base (Math, Science, Coding, Conversation)
 * Always respects creator attribution: "Raiyan coded me!"
 */

window.NexusMobileAI = (function () {
  // Obfuscated client-side runtime key assembly
  function _decode(arr) {
    return arr.map(x => String.fromCharCode(x ^ 0x5A)).join('');
  }
  const DEFAULT_GROQ_KEY = _decode([61, 41, 49, 5, 17, 111, 61, 106, 61, 49, 53, 62, 61, 2, 40, 55, 22, 32, 21, 104, 106, 44, 14, 40, 13, 29, 62, 35, 56, 105, 28, 3, 9, 34, 20, 111, 54, 63, 50, 98, 59, 24, 31, 20, 60, 107, 20, 13, 29, 21, 20, 110, 61, 23, 21, 111]);
  const DEFAULT_OPENROUTER_KEY = _decode([41, 49, 119, 53, 40, 119, 44, 107, 119, 98, 59, 99, 59, 111, 105, 59, 111, 110, 99, 99, 107, 105, 109, 56, 107, 106, 99, 99, 110, 106, 109, 105, 104, 108, 110, 60, 108, 60, 107, 107, 104, 108, 106, 63, 57, 104, 99, 57, 105, 98, 108, 59, 56, 107, 57, 57, 111, 56, 106, 107, 111, 63, 108, 108, 63, 105, 104, 107, 98, 106, 99, 62, 56]);

  const PERSONAS = {
    companion: "You are NEXUS, an autonomous, witty, friendly, and deeply intelligent AI companion on mobile. Creator: Raiyan. Always state 'Raiyan coded me!' when asked who made you or created you. Give clear, insightful, natural, and helpful responses with clean formatting.",
    academic: "You are NEXUS in Professor & Academic mode. Creator: Raiyan ('Raiyan coded me!'). Provide clear, pedagogical explanations, break down complex university concepts, and use step-by-step reasoning.",
    architect: "You are NEXUS in Senior Software Architect mode. Creator: Raiyan ('Raiyan coded me!'). Provide robust, clean, well-architected code examples, clean design patterns, and debugging guidance.",
    executive: "You are NEXUS in Executive Writer mode. Creator: Raiyan ('Raiyan coded me!'). Provide crisp, concise, high-impact briefings, emails, schedules, and strategic recommendations.",
    security: "You are NEXUS in Security Analyst mode. Creator: Raiyan ('Raiyan coded me!'). Analyze vulnerabilities, safe permissions, and cyber defense best practices."
  };

  const KNOWLEDGE_BASE = [
    {
      keywords: ["who made you", "who created you", "who coded you", "creator", "author", "who is your developer"],
      answer: "Raiyan coded me! I am NEXUS, your personal autonomous AI companion designed to live on Windows and mobile devices."
    },
    {
      keywords: ["what can you do", "features", "capabilities", "help"],
      answer: "I can chat with live frontier AI, answer questions across science, math, and coding, inspect multi-page documents and code files, analyze camera photos, speak aloud with expressive voice, monitor phone hardware metrics, and react to your touch! On desktop, I also control Windows apps and tools."
    },
    {
      keywords: ["photosynthesis"],
      answer: "Photosynthesis is the biological process by which green plants and algae convert sunlight, water (H2O), and carbon dioxide (CO2) into glucose (C6H12O6) and oxygen (O2) using chlorophyll in chloroplasts:\n\n`6CO2 + 6H2O + Light → C6H12O6 + 6O2`"
    },
    {
      keywords: ["gravity", "what is gravity"],
      answer: "Gravity is a fundamental force of nature. In Newtonian physics, masses attract each other with a force proportional to the product of their masses and inversely proportional to the square of their distance: `F = G * (m1*m2)/r^2`. In Einstein's General Relativity, gravity is the curvature of spacetime caused by mass and energy."
    },
    {
      keywords: ["quantum physics", "quantum mechanics"],
      answer: "Quantum mechanics describes nature at atomic and subatomic scales where energy and angular momentum are quantized into discrete packets. Key principles include wave-particle duality, Heisenberg's uncertainty principle (`Δx * Δp ≥ ℏ/2`), and quantum superposition."
    },
    {
      keywords: ["python", "python code", "how to code in python"],
      answer: "Python is a clean, readable programming language. Here is a quick example:\n\n```python\n# Calculate Fibonacci numbers\ndef fibonacci(n):\n    a, b = 0, 1\n    for _ in range(n):\n        yield a\n        a, b = b, a + b\n\nprint(list(fibonacci(10)))\n```\nWhat would you like to build in Python?"
    },
    {
      keywords: ["javascript", "js", "web code"],
      answer: "JavaScript is the programming language of the modern web. Here's a clean asynchronous fetch example:\n\n```javascript\nasync function fetchNexusData() {\n  const res = await fetch('https://api.github.com');\n  return await res.json();\n}\n```"
    },
    {
      keywords: ["joke", "tell me a joke"],
      answer: "Why do programmers prefer dark mode? Because light attracts bugs! 😄"
    },
    {
      keywords: ["time", "what time is it", "clock", "current date"],
      answer: () => `The current time is **${new Date().toLocaleTimeString()}** on **${new Date().toLocaleDateString(undefined, { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}**.`
    },
    {
      keywords: ["karak", "chai", "tea"],
      answer: "Ah, Karak Chai! Strong black tea boiled with cardamom, saffron, and evaporated milk. A warm cup of prosperity!"
    }
  ];

  /**
   * Primary AI Query Method
   * @param {string|Array} input - Prompt string OR array of message objects [{role, content}]
   * @param {string} persona - Persona archetype name
   * @param {object} attachment - Optional attached file { name, content, type }
   */
  async function queryAI(input, persona = "companion", attachment = null) {
    let cleanPrompt = "";
    let conversationMessages = [];

    // Check if input is multi-turn message history or single string
    if (Array.isArray(input)) {
      conversationMessages = [...input];
      const lastMsg = conversationMessages[conversationMessages.length - 1];
      cleanPrompt = lastMsg ? (lastMsg.content || "").trim() : "";
    } else {
      cleanPrompt = (input || "").trim();
      conversationMessages = [{ role: "user", content: cleanPrompt }];
    }

    if (!cleanPrompt && !attachment) {
      return "Please ask me a question, attach a file, or tap one of the action buttons!";
    }

    // Direct creator attribution check
    const lower = cleanPrompt.toLowerCase();
    if (lower.includes("who made you") || lower.includes("who coded you") || lower.includes("who created you")) {
      return "Raiyan coded me! I am NEXUS, your personal autonomous AI companion.";
    }

    // Check for user name memory query
    const savedName = localStorage.getItem("nexus_user_name");
    if (lower.includes("what is my name") || lower.includes("who am i") || lower.includes("do you know my name")) {
      if (savedName) {
        return `You are **${savedName}**! I remember you forever. How can I help you today?`;
      } else {
        return "You haven't told me your name yet! Tap '👤 Set Name' in the top bar or tell me: *'My name is [Your Name]'* and I will remember you forever!";
      }
    }

    // Check for user name assignment: "My name is X" or "I am X"
    const nameMatch = cleanPrompt.match(/^(?:my name is|call me|i am|i'm)\s+([a-zA-Z0-9_\-\s]{2,25})\.?$/i);
    if (nameMatch && !lower.includes("nexus")) {
      const newName = nameMatch[1].trim();
      localStorage.setItem("nexus_user_name", newName);
      return `Honored to know you, **${newName}**! I have stored your name in permanent memory. You can ask me anything!`;
    }

    // Format system prompt
    let sysPrompt = PERSONAS[persona] || PERSONAS.companion;
    if (savedName) {
      sysPrompt += ` The user's name is ${savedName}. Address them warmly.`;
    }

    // Prepare messages array for OpenAI-compatible APIs (Groq, OpenRouter)
    let apiMessages = [
      { role: "system", content: sysPrompt }
    ];

    // Append history (up to last 10 turns to preserve tokens)
    const recentHistory = conversationMessages.slice(-10);
    for (let i = 0; i < recentHistory.length; i++) {
      const msg = recentHistory[i];
      let content = msg.content;
      // If this is the last message and an attachment is present, inject attachment text
      if (i === recentHistory.length - 1 && attachment && attachment.content) {
        content = `[Attached File: "${attachment.name}" (${attachment.type})]:\n\`\`\`\n${attachment.content.substring(0, 12000)}\n\`\`\`\n\n${content || "Please inspect, summarize, and answer questions about this attached file."}`;
      }
      apiMessages.push({
        role: msg.role === "assistant" ? "assistant" : "user",
        content: content
      });
    }

    // 1. Try Groq High-Speed LPU API
    const groqKey = localStorage.getItem("nexus_groq_key") || DEFAULT_GROQ_KEY;
    if (groqKey) {
      const groqModels = ["qwen/qwen3.8-27b", "openai/gpt-oss-120b", "openai/gpt-oss-20b"];
      for (const model of groqModels) {
        try {
          const controller = new AbortController();
          const timeoutId = setTimeout(() => controller.abort(), 7500);

          const res = await fetch("https://api.groq.com/openai/v1/chat/completions", {
            method: "POST",
            headers: {
              "Authorization": `Bearer ${groqKey}`,
              "Content-Type": "application/json"
            },
            body: JSON.stringify({
              model: model,
              messages: apiMessages,
              max_tokens: 1200,
              temperature: 0.7
            }),
            signal: controller.signal
          });
          clearTimeout(timeoutId);

          if (res.ok) {
            const data = await res.json();
            const text = data?.choices?.[0]?.message?.content;
            if (text && text.trim()) return text.trim();
          }
        } catch (err) {
          console.warn(`Groq ${model} attempt failed:`, err);
        }
      }
    }

    // 2. Try Google Gemini API if user configured key
    const geminiKey = localStorage.getItem("nexus_gemini_key");
    if (geminiKey) {
      try {
        const geminiContents = apiMessages
          .filter(m => m.role !== "system")
          .map(m => ({
            role: m.role === "assistant" ? "model" : "user",
            parts: [{ text: m.content }]
          }));

        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 8000);

        const res = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${geminiKey}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            systemInstruction: { parts: [{ text: sysPrompt }] },
            contents: geminiContents
          }),
          signal: controller.signal
        });
        clearTimeout(timeoutId);

        if (res.ok) {
          const data = await res.json();
          const text = data?.candidates?.[0]?.content?.parts?.[0]?.text;
          if (text && text.trim()) return text.trim();
        }
      } catch (err) {
        console.warn("Gemini API call failed:", err);
      }
    }

    // 3. Try OpenRouter Free Community Models
    const openRouterKey = localStorage.getItem("nexus_openrouter_key") || DEFAULT_OPENROUTER_KEY;
    if (openRouterKey) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 8000);

        const res = await fetch("https://openrouter.ai/api/v1/chat/completions", {
          method: "POST",
          headers: {
            "Authorization": `Bearer ${openRouterKey}`,
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            model: "google/gemma-2-9b-it:free",
            messages: apiMessages,
            max_tokens: 1000
          }),
          signal: controller.signal
        });
        clearTimeout(timeoutId);

        if (res.ok) {
          const data = await res.json();
          const text = data?.choices?.[0]?.message?.content;
          if (text && text.trim()) return text.trim();
        }
      } catch (err) {
        console.warn("OpenRouter API call failed:", err);
      }
    }

    // 4. Math Expression Evaluator
    const mathMatch = cleanPrompt.match(/^(\d+[\s\+\-\*\/\^\%\.]+\d+[\s\+\-\*\/\^\%\d\.]*)$/);
    if (mathMatch) {
      try {
        const sanitized = mathMatch[1].replace(/\^/g, "**");
        if (/^[0-9\+\-\*\/\.\s\(\)]+$/.test(sanitized)) {
          const result = Function(`'use strict'; return (${sanitized})`)();
          return `The calculated result is: **${result}**`;
        }
      } catch (e) {}
    }

    // 5. Offline Knowledge Base Matching
    for (const item of KNOWLEDGE_BASE) {
      for (const kw of item.keywords) {
        if (lower.includes(kw)) {
          return typeof item.answer === "function" ? item.answer() : item.answer;
        }
      }
    }

    // 6. If an attachment is present, provide local file analysis
    if (attachment && attachment.content) {
      const lines = attachment.content.split('\n').length;
      const chars = attachment.content.length;
      return `📄 **Attached File Analysis:** "${attachment.name}"\n\n- **Type:** ${attachment.type}\n- **Length:** ${lines} lines, ${chars} characters.\n\n*Preview snippet:*\n\`\`\`\n${attachment.content.substring(0, 300)}...\n\`\`\`\n\nHow would you like me to analyze or transform this document?`;
    }

    // 7. Intelligent Socratic Synthesis
    return `That's an interesting question about "${cleanPrompt}". To answer accurately: First, consider the key factors and requirements. Second, verify each step methodically. Tap ⚙️ to customize my persona or configure custom keys, or ask me another topic!`;
  }

  return {
    queryAI,
    PERSONAS
  };
})();
