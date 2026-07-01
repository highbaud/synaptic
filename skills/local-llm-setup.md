---
name: local-llm-setup
description: Install and configure a local AI stack for private Obsidian vault intelligence — Ollama for running models, LM Studio for model discovery, Obsidian plugin connection, system prompt configuration, and model selection by task. Use when the user wants to set up local AI, asks how to connect Obsidian to a local model, or wants to run vault intelligence without a cloud dependency.
version: 0.1
---

# Local LLM Setup Skill

This skill covers the complete setup of a local AI stack for Obsidian vault intelligence. Total setup time: 30–45 minutes. Total cost: $0.

The privacy case first, because setup takes effort and the effort needs a clear motivation: when you use cloud AI for thinking work, your half-formed business decisions, your assessment of people, your private strategy exists on infrastructure you cannot audit. Local AI runs entirely on your machine. Your prompts stay in your RAM. Nothing is logged. Nothing trains a model. Your thinking is yours.

The tradeoff is honest: local models are less capable than frontier models. For complex multi-step reasoning or polished long-form writing, use the cloud. For daily vault work — morning capture processing, idea development, connection finding, decision support — local models are more than sufficient.

---

## Hardware Requirements

- **8 GB RAM minimum** — works, but model selection matters. Use llama3.2:3b only.
- **16 GB RAM** — comfortable daily use with llama3.1:8b.
- **24 GB RAM** — can run gemma2:9b for long document synthesis.
- **Apple Silicon (M1–M4)** — handles this exceptionally well. Metal GPU acceleration is automatic.
- **Windows/Linux with dedicated GPU** — excellent performance. Ollama uses CUDA automatically.
- **Older Intel-only machines with 8 GB** — work but are noticeably slower. Use phi3:mini or llama3.2:1b.

---

## Part 1: Install Ollama

Ollama runs large language models locally as a background service. It exposes a simple API at `http://localhost:11434` that Obsidian plugins and Synaptic connect to.

**Install:**
- Mac: [ollama.com](https://ollama.com) → download → drag to Applications → launch. A llama icon appears in the menu bar.
- Windows: `winget install Ollama.Ollama` or download the .exe installer. Runs as a background service.
- Linux: `curl -fsSL https://ollama.com/install.sh | sh`

**Pull a model:**
```bash
ollama pull llama3.2:3b        # 8 GB RAM: start here
ollama pull llama3.1:8b        # 16 GB RAM: noticeably better reasoning
ollama pull nomic-embed-text   # embeddings (required for Synaptic)
```

**Verify:**
```bash
ollama run llama3.2:3b
# Type: "Hello, are you running locally?"
# You should get a response. Press Ctrl+D to exit.
```

Open `http://localhost:11434` in a browser — you should see `Ollama is running`. That URL is what every tool uses.

**Ollama auto-starts** on login after the first launch. You do not manage it manually.

---

## Part 2: LM Studio (Optional Visual Interface)

LM Studio provides a visual model browser and runs an OpenAI-compatible server at `http://localhost:1234/v1`. Most people use it to discover and test models, then switch to Ollama for daily operation.

- Install from [lmstudio.ai](https://lmstudio.ai)
- Open → Discover tab → search for a model → select a GGUF format (Q4_K_M or Q5_K_M)
- Download, then Developer tab → Start Server → server goes green

**LM Studio vs. Ollama:**
Use LM Studio to browse and download models. Use Ollama as the daily background service. LM Studio's server stops when you close the app; Ollama persists.

To use LM Studio with Synaptic: uncomment the `lm_studio` provider block in `config.yaml`.

---

## Part 3: Model Selection

Pick the right model for your RAM and primary task. Changing models is a single command.

### By RAM

| RAM | Recommended model | Why |
|-----|------------------|-----|
| 8 GB | `llama3.2:3b` | Fast, handles daily vault work well |
| 16 GB | `llama3.1:8b` | Better reasoning, longer context |
| 24 GB | `gemma2:9b` | Long document synthesis across many notes |
| Slow hardware | `llama3.2:1b` or `phi3:mini` | Speed over capability |

### By task

| Task | Best model |
|------|-----------|
| Daily capture processing, inbox | llama3.2:3b |
| Decision briefs, complex reasoning | llama3.1:8b |
| Long document analysis, synthesis | gemma2:9b |
| Creative writing, idea development | mistral:7b |
| Technical notes, code | codellama:7b or deepseek-coder:6.7b |
| Fastest possible response | llama3.2:1b or phi3:mini |

```bash
# Pull additional models
ollama pull gemma2:9b
ollama pull mistral:7b
ollama pull phi3:mini

# List installed models
ollama list
```

The temptation is to pull the most capable model. The better instinct: pull the smallest model that handles your actual daily tasks, and use frontier cloud models only for work that genuinely needs them.

---

## Part 4: Connect Obsidian

### Plugin options

Search Community Plugins in Obsidian for any of these — they all work on the same principle:
- **Local LLM Helper** — recommended
- **BMO Chatbot** — supports local Ollama models, more features
- **Ollama plugin for Obsidian** — lightweight

Install: Settings → Community plugins → turn off Restricted mode → Browse → search → Install → Enable.

### Plugin configuration

In the plugin settings:

**API URL:**
- Ollama: `http://localhost:11434`
- LM Studio: `http://localhost:1234/v1`

**Model name:**
The exact model name from `ollama list`. For example: `llama3.2:3b` (not `llama3.2` — include the size tag).

**System prompt (copy this):**
```
You are a thinking partner helping me work through ideas in my Obsidian vault. 
You are direct, specific, and concise. You help me find non-obvious connections 
between ideas, surface the tensions in my thinking, and develop half-formed 
captures into ideas worth keeping. You do not pad responses with affirmations 
or restate what I just said. When I share a note or ask a question, respond 
in a way that genuinely advances my thinking. If an idea is weak, say so and 
explain why. If a note is not worth keeping, say that.
```

**Test:** Open any note. Ask the plugin: "Can you see this note and tell me what the main idea is?" A response means the connection is working.

---

## Obsidian Community Plugins Reference

The AI plugins in Part 4 connect your vault to a local model. The table below covers the broader community plugin ecosystem — useful to know when building out a full Obsidian setup. Start with 3 at most; add more only when you feel a specific gap.

| Category | Plugin | What it does |
|----------|--------|-------------|
| **Writing & Notes** | Templater | Powerful note templates with dynamic content, date variables, custom functions |
| | Longform | Project-level writing: manage scenes, chapters, word counts |
| | Smart Composer | AI-assisted writing inside the editor (works with local Ollama) |
| **Productivity** | Dataview | Query your vault like a database — build live tables, lists, and task views from frontmatter |
| | Tasks | Inline task management with due dates, priorities, and filters |
| | Calendar | Daily note calendar sidebar with contribution heatmap |
| **Visualization** | Excalidraw | Whiteboard and freehand diagrams embedded in notes |
| | Kanban | Project boards from Markdown lists |
| | Mind Map | Auto-generated mind maps from note heading structure |
| **AI & Publishing** | Smart Connections | Semantic note similarity surface (works with Ollama for local embeddings) |
| | Copilot | In-vault AI chat with vault context (supports local LLM endpoints) |
| | Obsidian Publish | Official publish-to-web for public-facing note sites |

**Recommended starting set (3 plugins):** Templater + Dataview + whichever AI plugin matches your setup. Add others only after 4 weeks of regular vault use — by then you will know exactly what friction each plugin addresses.

---

## Part 5: Synaptic Configuration

In `config.yaml`, the Ollama provider is pre-configured:

```yaml
providers:
  ollama:
    type: local
    base_url: http://localhost:11434
    chat_model: llama3.2:3b      # change to match your pulled model
    embedding_model: nomic-embed-text
```

Run `synaptic doctor` to verify Ollama is reachable and the model is available.

---

## Troubleshooting

**"Connection refused" in Obsidian plugin:**
Ollama is not running. Mac: check for the llama icon in the menu bar. Windows: check system tray. If missing, open Ollama from Applications. Terminal fallback: `ollama serve`.

**Very slow responses:**
Model is too large for available RAM and is swapping to disk. Switch to a smaller model: `llama3.2:3b` instead of `8b`, or `phi3:mini` on constrained hardware.

**Generic, unhelpful responses:**
System prompt is empty or too vague. Copy the system prompt from Part 4 into plugin settings. A specific system prompt is the single biggest quality improvement available without changing models.

**Plugin cannot find model:**
Run `ollama list` in terminal. Copy the exact model name including the size tag (e.g. `llama3.2:3b`, not `llama3.2`). Capitalization and the colon matter.

**LM Studio server keeps stopping:**
Expected — LM Studio stops when you close the app. Use Ollama for persistent background operation.

---

## Rules

- Start with `llama3.2:3b`. Upgrade to `llama3.1:8b` only if the smaller model is genuinely a bottleneck for your actual tasks.
- Use the system prompt. The difference between a well-crafted system prompt and a default one is larger than the difference between most model sizes.
- Verify the API is running (`localhost:11434` shows `Ollama is running`) before debugging plugin issues.
- The privacy boundary is the whole point. Keep `local_only: true` in Synaptic unless you have a specific reason to route a task externally.
- Ollama auto-starts after first launch. You do not need to manage it manually unless `synaptic doctor` reports it unreachable.
