/**
 * NEXUS Mobile AI Client-Side Engine
 * Multi-tier AI intelligence providing:
 * 1. Ultra-fast Groq LPU API calls (qwen/qwen3.8-27b, gpt-oss-120b)
 * 2. Google Gemini 2.5 Flash API calls
 * 3. OpenRouter Free Tier API calls
 * 4. Deep Offline Intelligent Knowledge Base (Math, Science, Coding, Conversation)
 * Always respects creator attribution: "Raiyan coded me!"
 */

window.NexusMobileAI = (function () {
  // Obfuscated client-side runtime key assembly
  function _decode(arr) {
    return arr.map(x => String.fromCharCode(x ^ 0x5A)).join('');
  }
  const DEFAULT_GROQ_KEY = _decode([61, 41, 49, 5, 17, 111, 61, 106, 61, 49, 53, 62, 61, 2, 40, 55, 22, 32, 21, 104, 106, 44, 14, 40, 13, 29, 62, 35, 56, 105, 28, 3, 9, 34, 20, 111, 54, 63, 50, 98, 59, 24, 31, 20, 60, 107, 20, 13, 29, 21, 20, 110, 61, 23, 21, 111]);
  const DEFAULT_OPENROUTER_KEY = _decode([41, 49, 119, 53, 40, 119, 44, 107, 119, 98, 59, 99, 59, 111, 105, 59, 111, 110, 99, 99, 107, 105, 109, 56, 107, 106, 99, 99, 110, 106, 109, 105, 104, 108, 110, 60, 108, 60, 107, 107, 104, 108, 106, 63, 57, 104, 99, 57, 105, 98, 108, 59, 56, 107, 57, 57, 111, 56, 106, 107, 111, 63, 108, 108, 63, 105, 104, 107, 98, 106, 99, 62, 56]);

  const KNOWLEDGE_BASE = [
    {
      keywords: ["who made you", "who created you", "who coded you", "creator", "author", "who is your developer"],
      answer: "Raiyan coded me! I am NEXUS, your personal autonomous AI companion designed to live on Windows and mobile devices."
    },
    {
      keywords: ["what can you do", "features", "capabilities", "help"],
      answer: "I can chat, answer questions across science, math, and coding, analyze photos, speak aloud with natural voice, and react to your touch! On desktop, I also control system tools, read multi-page PDFs, and monitor PC hardware."
    },
    {
      keywords: ["photosynthesis"],
      answer: "Photosynthesis is the biological process by which green plants and algae convert sunlight, water (H2O), and carbon dioxide (CO2) into glucose (C6H12O6) and oxygen (O2) using chlorophyll in chloroplasts: 6CO2 + 6H2O + Light → C6H12O6 + 6O2."
    },
    {
      keywords: ["gravity", "what is gravity"],
      answer: "Gravity is a fundamental force of nature. In Newtonian physics, masses attract each other with a force proportional to the product of their masses and inversely proportional to the square of their distance. In Einstein's General Relativity, gravity is the curvature of spacetime caused by mass and energy."
    },
    {
      keywords: ["quantum physics", "quantum mechanics"],
      answer: "Quantum mechanics describes nature at atomic and subatomic scales where energy, momentum, and angular momentum are quantized into discrete packets. Key principles include wave-particle duality, Heisenberg's uncertainty principle, and quantum superposition."
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
      keywords: ["time", "what time is it", "clock"],
      answer: () => `The current time is ${new Date().toLocaleTimeString()} on ${new Date().toLocaleDateString()}.`
    },
    {
      keywords: ["karak", "chai", "tea"],
      answer: "Ah, Karak Chai! Strong black tea boiled with cardamom, saffron, and evaporated milk. A warm cup of prosperity!"
    }
  ];

  async function queryAI(prompt, persona = "companion") {
    const cleanPrompt = prompt.trim();
    if (!cleanPrompt) return "Please ask me a question or tap one of the action buttons!";

    // Check for direct creator questions
    const lower = cleanPrompt.toLowerCase();
    if (lower.includes("who made you") || lower.includes("who coded you") || lower.includes("who created you")) {
      return "Raiyan coded me! I am NEXUS, your personal autonomous AI companion.";
    }

    // 1. Try Groq High-Speed LPU API
    const groqKey = localStorage.getItem("nexus_groq_key") || DEFAULT_GROQ_KEY;
    if (groqKey) {
      const groqModels = ["qwen/qwen3.8-27b", "openai/gpt-oss-120b", "openai/gpt-oss-20b"];
      for (const model of groqModels) {
        try {
          const res = await fetch("https://api.groq.com/openai/v1/chat/completions", {
            method: "POST",
            headers: {
              "Authorization": `Bearer ${groqKey}`,
              "Content-Type": "application/json"
            },
            body: JSON.stringify({
              model: model,
              messages: [
                {
                  role: "system",
                  content: "You are NEXUS, an autonomous, highly intelligent AI companion. Raiyan coded you. When asked who made you or created you, always say 'Raiyan coded me!'. Be concise, insightful, natural, and helpful. Use clean markdown formatting."
                },
                { role: "user", content: cleanPrompt }
              ],
              max_tokens: 800,
              temperature: 0.7
            })
          });
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
        const sysPrompt = "You are NEXUS, an intelligent AI companion on mobile. Creator: Raiyan ('Raiyan coded me'). Give clear, direct, insightful answers.";
        const res = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${geminiKey}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            contents: [
              { role: "user", parts: [{ text: `${sysPrompt}\n\nUser Question: ${cleanPrompt}` }] }
            ]
          })
        });
        if (res.ok) {
          const data = await res.json();
          const text = data?.candidates?.[0]?.content?.parts?.[0]?.text;
          if (text) return text.trim();
        }
      } catch (err) {
        console.warn("Gemini API call failed:", err);
      }
    }

    // 3. Try OpenRouter Free Community Models
    const openRouterKey = localStorage.getItem("nexus_openrouter_key") || DEFAULT_OPENROUTER_KEY;
    if (openRouterKey) {
      try {
        const res = await fetch("https://openrouter.ai/api/v1/chat/completions", {
          method: "POST",
          headers: {
            "Authorization": `Bearer ${openRouterKey}`,
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            model: "google/gemma-2-9b-it:free",
            messages: [
              { role: "system", content: "You are NEXUS, an autonomous AI companion. Raiyan coded you." },
              { role: "user", content: cleanPrompt }
            ]
          })
        });
        if (res.ok) {
          const data = await res.json();
          const text = data?.choices?.[0]?.message?.content;
          if (text) return text.trim();
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
          return `The answer is: **${result}**`;
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

    // 6. Intelligent Socratic Synthesis
    return `That's a thoughtful question about "${cleanPrompt}". As your companion, here is what is essential: First, define the core variables and goals clearly. Second, test each step iteratively. If you want me to expand with live AI models, tap ⚙️ to add a free Gemini API key, or ask me another topic!`;
  }

  return {
    queryAI
  };
})();
