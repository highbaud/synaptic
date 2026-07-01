---
type: project
status: active
date: 2026-06-08
tags: [local-ai, obsidian, privacy, project/local-llm-setup]
deadline: 2026-06-15
priority: high
next_action: Test Obsidian plugin connection with llama3.2:3b
completion: 60
---

# Local LLM Stack Setup

## Outcome
A fully local AI stack: Ollama running as background service, local model pulled, Obsidian plugin connected, daily workflow running. Zero cloud dependency for personal thinking work.

## Why this matters
Sensitive business thinking and personal strategy stay on my hardware. No subscription cost. Works offline. The tradeoff (less capable than frontier models) is acceptable for daily vault work.

## Progress
- [x] Install Ollama
- [x] Pull llama3.2:3b
- [x] Verify API at localhost:11434
- [ ] Connect Obsidian Local LLM Helper plugin
- [ ] Write and test system prompt
- [ ] Run first morning capture processing pass
- [ ] Document daily workflow

## Notes
LM Studio is worth installing as a model browser even if Ollama handles daily operation. The visual interface makes it easy to discover and download GGUF models before committing.

## Connections
- [[Privacy Is the Real Value of Local AI]]
- [[Local AI Model Selection Guide]]
