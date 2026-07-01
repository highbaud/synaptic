---
type: resource
status: reference
date: 2026-06-08
tags: [local-ai, ollama, tools]
source: Synaptic local-llm-setup skill
---

# Local AI Model Selection Guide

Model choice depends on two variables: available RAM and primary task. This is a working reference, not an exhaustive catalog.

## By RAM

| RAM | Best model | Use case |
|-----|-----------|----------|
| 8 GB | llama3.2:3b | Daily vault work, capture processing, idea development |
| 16 GB | llama3.1:8b | Better reasoning, longer context, writing tasks |
| 24 GB | gemma2:9b | Long document analysis, note synthesis across many notes |
| Any (fast) | llama3.2:1b or phi3:mini | Quick lookups on slower hardware |

## By task

- **Daily thinking, capture processing:** llama3.2:3b or llama3.1:8b
- **Summarizing and connecting long notes:** gemma2:9b
- **Creative writing, idea development:** mistral:7b
- **Technical work, code in notes:** codellama:7b or deepseek-coder:6.7b

## Pull command
```bash
ollama pull llama3.2:3b      # default recommendation
ollama pull llama3.1:8b      # if 16GB available
ollama pull nomic-embed-text # required for embeddings
```

## Key Tension
The temptation is to pull the most capable model available. The right instinct is the opposite: pull the smallest model that handles your actual daily tasks. The capability gap between 3B and 8B for "process this morning's captures" is smaller than the speed and memory difference. Use frontier models (via API) for work that genuinely needs them.

## Connections
- [[Privacy Is the Real Value of Local AI]] — model selection only matters after the privacy decision is made
- [[2026-06-08-project-local-llm-stack]] — current project applying this selection logic
