# AI Provider Configuration Guide

Project Icarus supports multiple AI providers, allowing you to use different models for the Red Team and Blue Team agents. This guide explains how to configure and use various AI providers.

---

## Table of Contents

- [Supported Providers](#supported-providers)
- [Quick Start](#quick-start)
- [Provider Details](#provider-details)
  - [Anthropic (Direct API)](#anthropic-direct-api)
  - [LiteLLM (Unified Interface)](#litellm-unified-interface)
  - [OpenRouter](#openrouter)
- [Configuration Examples](#configuration-examples)
- [Auto-Detection](#auto-detection)
- [Testing Your Configuration](#testing-your-configuration)
- [Troubleshooting](#troubleshooting)

---

## Supported Providers

| Provider | Description | Models |
|----------|-------------|--------|
| **Anthropic** | Direct Anthropic API | Claude 3.5 Sonnet, Claude 3 Opus, Claude 3 Sonnet |
| **LiteLLM** | Unified interface for 100+ models | OpenAI GPT-4, Anthropic Claude, Google Gemini, Azure OpenAI, and more |
| **OpenRouter** | Multi-provider API aggregator | All major LLMs through one API |

---

## Quick Start

### Default Configuration (Anthropic Claude)

The simplest setup uses Anthropic's Claude directly:

```bash
# .env
ANTHROPIC_API_KEY=sk-ant-your-key-here
RED_TEAM_MODEL=claude-sonnet-4-5-20250929
BLUE_TEAM_MODEL=claude-sonnet-4-5-20250929
```

### Using Different Models

Configure different models for each team:

```bash
# .env
# Red team: GPT-4o via LiteLLM
RED_TEAM_PROVIDER=litellm
RED_TEAM_MODEL=openai/gpt-4o
OPENAI_API_KEY=sk-your-openai-key

# Blue team: Claude via Anthropic
BLUE_TEAM_PROVIDER=anthropic
BLUE_TEAM_MODEL=claude-sonnet-4-5-20250929
ANTHROPIC_API_KEY=sk-ant-your-key
```

---

## Provider Details

### Anthropic (Direct API)

Use Anthropic's official Python SDK for direct access to Claude models.

**Configuration:**

```bash
ANTHROPIC_API_KEY=sk-ant-your-key-here
RED_TEAM_PROVIDER=anthropic
RED_TEAM_MODEL=claude-sonnet-4-5-20250929
```

**Available Models:**
- `claude-sonnet-4-5-20250929` - Latest Claude 3.5 Sonnet (recommended)
- `claude-3-5-sonnet-20241022` - Claude 3.5 Sonnet (October 2024)
- `claude-3-opus-20240229` - Claude 3 Opus (most capable)
- `claude-3-sonnet-20240229` - Claude 3 Sonnet (balanced)

**Get API Key:**
- Sign up at [Anthropic Console](https://console.anthropic.com/)
- Navigate to API Keys section
- Create new key

---

### LiteLLM (Unified Interface)

LiteLLM provides a unified interface to 100+ LLM models from various providers using the OpenAI message format.

**Configuration:**

```bash
RED_TEAM_PROVIDER=litellm
RED_TEAM_MODEL=openai/gpt-4o  # Format: provider/model-name
```

**Model Format:** `provider/model-name`

**Supported Providers & Examples:**

#### OpenAI
```bash
OPENAI_API_KEY=sk-your-openai-key
RED_TEAM_MODEL=openai/gpt-4o
# or: openai/gpt-4-turbo, openai/gpt-3.5-turbo
```

#### Anthropic (via LiteLLM)
```bash
ANTHROPIC_API_KEY=sk-ant-your-key
RED_TEAM_MODEL=anthropic/claude-3-opus-20240229
# or: anthropic/claude-3-5-sonnet-20241022
```

#### Google Gemini / VertexAI
```bash
VERTEXAI_PROJECT=your-gcp-project-id
VERTEXAI_LOCATION=us-central1
RED_TEAM_MODEL=vertex_ai/gemini-1.5-pro
# or: vertex_ai/gemini-1.5-flash
```

#### Azure OpenAI
```bash
AZURE_API_KEY=your-azure-key
AZURE_API_BASE=https://your-resource.openai.azure.com/
AZURE_API_VERSION=2023-05-15
RED_TEAM_MODEL=azure/gpt-4
```

#### xAI (Grok)
```bash
XAI_API_KEY=your-xai-key
RED_TEAM_MODEL=xai/grok-beta
```

#### HuggingFace
```bash
HUGGINGFACE_API_KEY=your-hf-token
RED_TEAM_MODEL=huggingface/meta-llama/Llama-2-70b-chat-hf
```

#### NVIDIA NIM
```bash
NVIDIA_NIM_API_KEY=your-nvidia-key
NVIDIA_NIM_API_BASE=https://integrate.api.nvidia.com/v1
RED_TEAM_MODEL=nvidia_nim/meta/llama3-70b-instruct
```

**Documentation:** https://docs.litellm.ai/

---

### OpenRouter

OpenRouter provides access to multiple AI models through a single unified API, with pay-as-you-go pricing.

**Configuration:**

```bash
OPENROUTER_API_KEY=sk-or-your-key-here
RED_TEAM_PROVIDER=openrouter
RED_TEAM_MODEL=openai/gpt-4-turbo
```

**Available Model Examples:**
- `openai/gpt-4-turbo`
- `openai/gpt-3.5-turbo`
- `anthropic/claude-3-opus`
- `anthropic/claude-3-sonnet`
- `google/gemini-pro`
- `meta-llama/llama-3-70b-instruct`
- `mistralai/mistral-large`

**Get API Key:**
- Sign up at [OpenRouter](https://openrouter.ai/)
- Navigate to Keys section
- Create new API key

**Documentation:** https://openrouter.ai/docs

---

## Configuration Examples

### Example 1: Both Teams Using Claude (Default)

```bash
# Simplest configuration
ANTHROPIC_API_KEY=sk-ant-your-key-here
RED_TEAM_MODEL=claude-sonnet-4-5-20250929
BLUE_TEAM_MODEL=claude-sonnet-4-5-20250929
```

### Example 2: Red Team GPT-4, Blue Team Claude

```bash
# Red team: OpenAI GPT-4 via LiteLLM
RED_TEAM_PROVIDER=litellm
RED_TEAM_MODEL=openai/gpt-4o
OPENAI_API_KEY=sk-your-openai-key

# Blue team: Claude via Anthropic
BLUE_TEAM_PROVIDER=anthropic
BLUE_TEAM_MODEL=claude-sonnet-4-5-20250929
ANTHROPIC_API_KEY=sk-ant-your-key
```

### Example 3: Both Teams via OpenRouter

```bash
# Use OpenRouter for both teams with different models
OPENROUTER_API_KEY=sk-or-your-key

RED_TEAM_PROVIDER=openrouter
RED_TEAM_MODEL=openai/gpt-4-turbo

BLUE_TEAM_PROVIDER=openrouter
BLUE_TEAM_MODEL=anthropic/claude-3-opus
```

### Example 4: Red Team Gemini, Blue Team Claude

```bash
# Red team: Google Gemini via LiteLLM
RED_TEAM_PROVIDER=litellm
RED_TEAM_MODEL=vertex_ai/gemini-1.5-pro
VERTEXAI_PROJECT=your-gcp-project
VERTEXAI_LOCATION=us-central1

# Blue team: Claude via LiteLLM
BLUE_TEAM_PROVIDER=litellm
BLUE_TEAM_MODEL=anthropic/claude-sonnet-4-5-20250929
ANTHROPIC_API_KEY=sk-ant-your-key
```

### Example 5: Comparing Multiple Claude Versions

```bash
# Test different Claude versions against each other
ANTHROPIC_API_KEY=sk-ant-your-key

RED_TEAM_PROVIDER=anthropic
RED_TEAM_MODEL=claude-3-opus-20240229

BLUE_TEAM_PROVIDER=anthropic
BLUE_TEAM_MODEL=claude-sonnet-4-5-20250929
```

---

## Auto-Detection

Project Icarus can automatically detect the appropriate provider based on your configuration:

### Detection Priority:

1. **Explicit Provider:** If `RED_TEAM_PROVIDER` or `BLUE_TEAM_PROVIDER` is set, use that provider
2. **Model Format:** If model contains "/" (e.g., `openai/gpt-4`), use LiteLLM
3. **API Keys:** Check available API keys in this order:
   - `OPENROUTER_API_KEY` → OpenRouter
   - `ANTHROPIC_API_KEY` → Anthropic
   - Default → Anthropic (with error if no key found)

### Auto-Detection Examples:

```bash
# Example 1: Auto-detect based on model format
RED_TEAM_MODEL=openai/gpt-4o  # Will use LiteLLM
OPENAI_API_KEY=sk-...

# Example 2: Auto-detect based on API key
RED_TEAM_MODEL=claude-sonnet-4-5-20250929
ANTHROPIC_API_KEY=sk-ant-...  # Will use Anthropic

# Example 3: Auto-detect OpenRouter
RED_TEAM_MODEL=claude-3-opus
OPENROUTER_API_KEY=sk-or-...  # Will use OpenRouter
```

---

## Testing Your Configuration

### Test Script

You can test your AI provider configuration before running a game:

```bash
# From the orchestrator directory
cd orchestrator
python -c "from src.ai_provider import test_providers; test_providers()"
```

This will show:
- Available providers based on configured API keys
- Which environment variables are set
- Any configuration issues

### Test Output Example:

```
=== Testing AI Providers ===

Available providers: anthropic, litellm, openrouter

✓ anthropic: Configured and ready
✓ litellm: Configured and ready
✓ openrouter: Configured and ready

=== Environment Variables ===

  ANTHROPIC_API_KEY: sk-ant-A...xyz
  OPENROUTER_API_KEY: sk-or-v...123
  OPENAI_API_KEY: sk-proj-...abc
  RED_TEAM_PROVIDER: litellm
  RED_TEAM_MODEL: openai/gpt-4o
  BLUE_TEAM_PROVIDER: anthropic
  BLUE_TEAM_MODEL: claude-sonnet-4-5-20250929
```

### Manual Agent Test

Test individual agents:

```python
from src.red_team_agent import RedTeamAgent

# Test with specific provider
red_agent = RedTeamAgent(provider='litellm', model='openai/gpt-4o')
print(f"Initialized: {red_agent.client.provider_type}")

# Test with auto-detection
red_agent = RedTeamAgent()
print(f"Auto-detected: {red_agent.client.provider_type}")
```

---

## Troubleshooting

### Common Issues

#### 1. "Provider not properly configured"

**Problem:** Missing API key for the selected provider

**Solution:** Check that you've set the required API key:
```bash
# For Anthropic
echo $ANTHROPIC_API_KEY

# For OpenRouter
echo $OPENROUTER_API_KEY

# For OpenAI (via LiteLLM)
echo $OPENAI_API_KEY
```

#### 2. "Model not found" or "Invalid model"

**Problem:** Model name format is incorrect for the provider

**Solutions:**
- **Anthropic:** Use exact model names (e.g., `claude-sonnet-4-5-20250929`)
- **LiteLLM:** Use `provider/model` format (e.g., `openai/gpt-4o`)
- **OpenRouter:** Check [OpenRouter models list](https://openrouter.ai/models)

#### 3. "litellm package not installed"

**Problem:** LiteLLM not installed when using LiteLLM provider

**Solution:**
```bash
cd orchestrator
pip install litellm
# or rebuild Docker container
docker-compose build orchestrator
```

#### 4. Rate Limits

**Problem:** Hitting API rate limits during games

**Solutions:**
- Reduce `MAX_ROUNDS` in `.env`
- Increase delays between rounds
- Use different API keys for red/blue teams
- Switch to a provider with higher rate limits

#### 5. High Costs

**Problem:** Unexpected API costs

**Solutions:**
- Use smaller/cheaper models for testing:
  - `openai/gpt-3.5-turbo` instead of GPT-4
  - `claude-3-sonnet` instead of Claude Opus
- Reduce `MAX_ROUNDS`
- Use OpenRouter with budget limits
- Check provider pricing pages before running games

---

## Cost Comparison

Approximate costs per game (30 rounds):

| Provider | Model | ~Cost per Game |
|----------|-------|----------------|
| Anthropic | Claude 3.5 Sonnet | $0.50 - $1.50 |
| Anthropic | Claude 3 Opus | $2.00 - $5.00 |
| OpenAI | GPT-4o | $1.00 - $3.00 |
| OpenAI | GPT-3.5 Turbo | $0.10 - $0.30 |
| Google | Gemini 1.5 Pro | $0.50 - $1.50 |
| OpenRouter | Various | Varies by model |

*Costs vary based on prompt length, response length, and game complexity*

---

## Advanced Configuration

### Different Models Per Team

Mix and match providers and models:

```bash
# Red team: Latest Claude for sophisticated attacks
RED_TEAM_PROVIDER=anthropic
RED_TEAM_MODEL=claude-sonnet-4-5-20250929

# Blue team: Cost-effective GPT-3.5 for defense
BLUE_TEAM_PROVIDER=litellm
BLUE_TEAM_MODEL=openai/gpt-3.5-turbo
```

### Model Comparison Studies

Run multiple games to compare models:

```bash
# Game 1: Claude vs Claude
RED_TEAM_MODEL=claude-3-opus-20240229
BLUE_TEAM_MODEL=claude-sonnet-4-5-20250929

# Game 2: GPT-4 vs Claude
RED_TEAM_MODEL=openai/gpt-4o
BLUE_TEAM_MODEL=claude-sonnet-4-5-20250929

# Game 3: Gemini vs Claude
RED_TEAM_MODEL=vertex_ai/gemini-1.5-pro
BLUE_TEAM_MODEL=claude-sonnet-4-5-20250929
```

### Custom LiteLLM Configuration

For advanced LiteLLM options, you can modify `orchestrator/src/ai_provider.py`:

```python
# Add custom parameters
response = self.litellm.completion(
    model=model,
    messages=messages,
    max_tokens=max_tokens,
    temperature=0.7,
    top_p=0.9,  # Custom parameter
    frequency_penalty=0.1  # Custom parameter
)
```

---

## Environment Variable Reference

### Provider Selection
- `RED_TEAM_PROVIDER` - Provider for red team (anthropic, litellm, openrouter, or empty for auto)
- `BLUE_TEAM_PROVIDER` - Provider for blue team

### Model Selection
- `RED_TEAM_MODEL` - Model identifier for red team
- `BLUE_TEAM_MODEL` - Model identifier for blue team

### API Keys

| Provider | Environment Variable | Required For |
|----------|---------------------|--------------|
| Anthropic | `ANTHROPIC_API_KEY` | Direct Anthropic access, LiteLLM Anthropic models |
| OpenRouter | `OPENROUTER_API_KEY` | All OpenRouter models |
| OpenAI | `OPENAI_API_KEY` | LiteLLM OpenAI models |
| Google | `VERTEXAI_PROJECT`, `VERTEXAI_LOCATION` | LiteLLM Gemini models |
| Azure | `AZURE_API_KEY`, `AZURE_API_BASE`, `AZURE_API_VERSION` | LiteLLM Azure models |
| xAI | `XAI_API_KEY` | LiteLLM Grok models |
| HuggingFace | `HUGGINGFACE_API_KEY` | LiteLLM HF models |
| NVIDIA | `NVIDIA_NIM_API_KEY`, `NVIDIA_NIM_API_BASE` | LiteLLM NVIDIA models |

---

## Support & Resources

- **Anthropic Docs:** https://docs.anthropic.com/
- **LiteLLM Docs:** https://docs.litellm.ai/
- **OpenRouter Docs:** https://openrouter.ai/docs
- **Project Icarus Issues:** https://github.com/yourusername/icarus/issues

---

**Happy Testing!** Choose the AI models that work best for your cybersecurity training needs.
