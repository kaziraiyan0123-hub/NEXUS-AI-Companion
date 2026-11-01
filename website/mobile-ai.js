/**
 * NEXUS Mobile AI Client-Side Engine
 * Multi-tier AI intelligence providing:
 * 1. Direct Google Gemini 2.5 Flash API calls (if key configured)
 * 2. Direct Groq Llama 3.3 70B API calls (if key configured)
 * 3. Deep Offline Intelligent Knowledge Base (Math, Science, Coding, Conversation)
 * Always respects creator attribution: "Raiyan coded me!"
 */

window.NexusMobileAI = (function () {
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

    // 1. Try Google Gemini API if user saved a key
    const geminiKey = localStorage.getItem("nexus_gemini_key");
    if (geminiKey) {
      try {
        const sysPrompt = `You are NEXUS, an intelligent AI companion on mobile. Creator: Raiyan ('Raiyan coded me'). Mode: ${persona}. Give clear, direct, insightful answers.`;
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
          if (text) return text;
        }
      } catch (err) {
        console.warn("Gemini API call failed, falling back to local brain:", err);
      }
    }

    // 2. Try Groq API if user saved a key
    const groqKey = localStorage.getItem("nexus_groq_key");
    if (groqKey) {
      try {
        const res = await fetch("https://api.groq.com/openai/v1/chat/completions", {
          method: "POST",
          headers: {
            "Authorization": `Bearer ${groqKey}`,
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            model: "llama-3.3-70b-versatile",
            messages: [
              { role: "system", content: "You are NEXUS, an autonomous AI companion. Raiyan coded you. Be insightful, concise, and helpful." },
              { role: "user", content: cleanPrompt }
            ]
          })
        });
        if (res.ok) {
          const data = await res.json();
          const text = data?.choices?.[0]?.message?.content;
          if (text) return text;
        }
      } catch (err) {
        console.warn("Groq API call failed, falling back to local brain:", err);
      }
    }

    // 3. Math Expression Evaluator
    const mathMatch = cleanPrompt.match(/^(\d+[\s\+\-\*\/\^\%\.]+\d+[\s\+\-\*\/\^\%\d\.]*)$/);
    if (mathMatch) {
      try {
        const sanitized = mathMatch[1].replace(/\^/g, "**");
        // Safe numeric evaluation
        if (/^[0-9\+\-\*\/\.\s\(\)]+$/.test(sanitized)) {
          const result = Function(`'use strict'; return (${sanitized})`)();
          return `The answer is: **${result}**`;
        }
      } catch (e) {}
    }

    // 4. Offline Knowledge Base Matching
    for (const item of KNOWLEDGE_BASE) {
      for (const kw of item.keywords) {
        if (lower.includes(kw)) {
          return typeof item.answer === "function" ? item.answer() : item.answer;
        }
      }
    }

    // 5. Intelligent Socratic Synthesis
    return `That's a thoughtful question about "${cleanPrompt}". As your companion, here is what is essential: First, define the core variables and goals clearly. Second, test each step iteratively. If you want me to expand with live AI models, tap ⚙️ to add a free Gemini API key, or ask me another topic!`;
  }

  return {
    queryAI
  };
})();
