# Westminster Parliamentary AI - Model Configuration Guide

This guide explains how to configure the Westminster Parliamentary AI System to work with any AI model provider, making the system completely model-agnostic for organizations and end users.

## Overview

The Westminster Parliamentary AI System supports multiple AI providers through a comprehensive model-agnostic architecture that allows:

- **Multi-Provider Support**: OpenAI, Anthropic, Gemini, Groq, Mistral, and many more
- **Automatic Fallback**: If one provider fails, automatically switch to backup providers
- **Custom Endpoints**: Support for organization proxies and custom model deployments
- **Role-Specific Configuration**: Different model settings for each constitutional role
- **Environment-Based Configuration**: Easy setup through environment variables

## Supported Providers

### Primary Providers
- **OpenAI**: GPT-4o, GPT-4 Turbo, GPT-3.5 Turbo
- **Anthropic**: Claude 3.5 Sonnet, Claude 3.5 Haiku, Claude 3 Opus
- **Google Gemini**: Gemini 2.0 Flash, Gemini 1.5 Pro
- **Groq**: Llama 3.1, Mixtral (ultra-fast inference)
- **Mistral**: Mistral Large, Mistral Small

### OpenAI-Compatible Providers
- **DeepSeek**: Code-focused models
- **Grok (xAI)**: Latest xAI models
- **Ollama**: Local/self-hosted models
- **OpenRouter**: Multi-model proxy service
- **Perplexity**: Research-focused models
- **Fireworks AI**: Fast inference
- **Together AI**: Open source models

### Enterprise Providers
- **Azure OpenAI**: Enterprise OpenAI deployment
- **AWS Bedrock**: Amazon's managed AI service
- **Custom Proxies**: Organization-specific endpoints

## Quick Start

1. **Copy the environment template**:
   ```bash
   cp .env.example .env
   ```

2. **Configure your preferred providers** in `.env`:
   ```bash
   # Enable OpenAI
   OPENAI_API_KEY=sk-your-openai-key
   OPENAI_ENABLED=true
   
   # Enable Anthropic as fallback
   ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
   ANTHROPIC_ENABLED=true
   ```

3. **Test the configuration**:
   ```python
   from triad.models.model_config import get_model_config
   
   config = get_model_config()
   print(config.get_model_status())
   ```

## Configuration Examples

### Basic Multi-Provider Setup

```bash
# Primary provider
OPENAI_API_KEY=sk-your-openai-key
OPENAI_ENABLED=true

# Fallback providers
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
ANTHROPIC_ENABLED=true

GEMINI_API_KEY=your-gemini-key
GEMINI_ENABLED=true

# Fallback order
PRIMARY_PROVIDER=openai
SECONDARY_PROVIDER=anthropic
TERTIARY_PROVIDER=gemini
```

### Organization Proxy Setup

```bash
# Custom organization proxy using OpenAI format
OPENAI_API_KEY=your-org-proxy-key
OPENAI_ENABLED=true
OPENAI_BASE_URL=https://ai-proxy.yourcompany.com/v1
OPENAI_ORG_ID=your-org-id

# Backup to external provider
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
ANTHROPIC_ENABLED=true
```

### Local/Self-Hosted Setup

```bash
# Local Ollama deployment
OLLAMA_API_KEY=ollama
OLLAMA_ENABLED=true
OLLAMA_BASE_URL=http://localhost:11434/v1

# Cloud fallback
GROQ_API_KEY=gsk-your-groq-key
GROQ_ENABLED=true
```

### Cost-Optimized Setup

```bash
# Fast, cheap models for routine tasks
GROQ_API_KEY=gsk-your-groq-key
GROQ_ENABLED=true

MISTRAL_API_KEY=your-mistral-key
MISTRAL_ENABLED=true

# Premium models for complex analysis
OPENAI_API_KEY=sk-your-openai-key
OPENAI_ENABLED=true
```

## Parliamentary Role Configuration

Each constitutional agent can be configured with role-specific model settings:

### Planner Agent (Legislative Authority)
```bash
PLANNER_TEMPERATURE=0.2    # More deterministic for policy planning
PLANNER_MAX_TOKENS=6144    # Longer context for legislation
```

### Executor Agent (Executive Authority)
```bash
EXECUTOR_TEMPERATURE=0.3   # Balanced for implementation decisions
EXECUTOR_MAX_TOKENS=4096   # Standard context
```

### Evaluator Agent (Judicial Authority)
```bash
EVALUATOR_TEMPERATURE=0.1  # Most deterministic for legal analysis
EVALUATOR_MAX_TOKENS=8192  # Longest context for complex legal reasoning
```

### Overwatch Agent (Crown Authority)
```bash
OVERWATCH_TEMPERATURE=0.15 # Conservative for constitutional oversight
OVERWATCH_MAX_TOKENS=4096  # Standard context
```

## Advanced Configuration

### Custom Model Implementation

For unsupported providers, implement a custom model:

```python
from triad.models.model_config import WestminsterModelConfig
from pydantic_ai.models.base import Model
from pydantic_ai.providers.openai import OpenAIProvider

# Custom provider configuration
config = WestminsterModelConfig()
config.providers["custom"] = ProviderConfig(
    name="custom",
    api_key="your-custom-key",
    base_url="https://custom-api.yourorg.com/v1",
    enabled=True,
    models=["custom-model-v1"]
)

# Create custom model instance
custom_model = config.create_model_instance("custom", "custom-model-v1")
```

### Fallback Strategies

Configure different fallback behaviors:

```python
from triad.models.model_config import get_model_config
from pydantic_ai.models.fallback import FallbackModel

config = get_model_config()

# Speed-first fallback (fast → accurate)
speed_fallback = config.create_fallback_model(["groq", "openai", "anthropic"])

# Accuracy-first fallback (accurate → fast)
accuracy_fallback = config.create_fallback_model(["anthropic", "openai", "groq"])

# Cost-optimized fallback (cheap → expensive)
cost_fallback = config.create_fallback_model(["groq", "mistral", "openai"])
```

### Environment Variable Priority

The system loads configuration in this order:
1. Direct environment variables
2. `.env` file in project root
3. Configuration file (if specified)
4. Default values

## API Keys and Security

### Getting API Keys

- **OpenAI**: https://platform.openai.com/api-keys
- **Anthropic**: https://console.anthropic.com/settings/keys
- **Google Gemini**: https://aistudio.google.com/app/apikey
- **Groq**: https://console.groq.com/keys
- **Mistral**: https://console.mistral.ai/api-keys/

### Security Best Practices

1. **Never commit API keys to version control**
2. **Use environment variables or secure key management**
3. **Rotate keys regularly**
4. **Set up monitoring for unusual usage**
5. **Use organization-specific keys for team deployments**

## Usage Examples

### Creating Constitutional Agents

```python
from triad.models.model_config import create_constitutional_agents
from triad.models.model_config import ParliamentaryRole, get_model_config

# Create all four constitutional agents
agents = create_constitutional_agents()

planner = agents[ParliamentaryRole.PLANNER]
executor = agents[ParliamentaryRole.EXECUTOR] 
evaluator = agents[ParliamentaryRole.EVALUATOR]
overwatch = agents[ParliamentaryRole.OVERWATCH]

# Use in parliamentary session
async with planner.run_stream("Analyze the proposed healthcare bill") as response:
    async for message in response:
        print(message.content)
```

### Custom Agent Configuration

```python
from triad.models.model_config import get_model_config, ParliamentaryRole
from pydantic_ai.settings import ModelSettings

config = get_model_config()

# Create custom settings for specific use case
custom_settings = ModelSettings(
    temperature=0.1,
    max_tokens=2048,
    top_p=0.95
)

# Create agent with specific providers and settings
evaluator = config.create_parliamentary_agent(
    role=ParliamentaryRole.EVALUATOR,
    providers=["anthropic", "openai"],  # Only use these providers
    custom_settings=custom_settings
)
```

### Configuration Validation

```python
from triad.models.model_config import get_model_config

config = get_model_config()

# Check configuration status
status = config.get_model_status()
print(f"Enabled providers: {status['enabled_providers']}")

# Validate configuration
issues = config.validate_configuration()
if issues:
    print("Configuration issues found:")
    for issue in issues:
        print(f"  - {issue}")
else:
    print("Configuration is valid!")
```

## Troubleshooting

### Common Issues

1. **No providers enabled**
   ```
   ValueError: No enabled providers available for fallback model
   ```
   **Solution**: Enable at least one provider with a valid API key

2. **Invalid API key**
   ```
   AuthenticationError: Incorrect API key provided
   ```
   **Solution**: Check API key format and validity

3. **Rate limits**
   ```
   RateLimitError: Rate limit exceeded
   ```
   **Solution**: Configure multiple providers for automatic fallback

4. **Network connectivity**
   ```
   ConnectionError: Unable to connect to provider
   ```
   **Solution**: Check network connectivity and firewall settings

### Debug Configuration

Enable debug logging to troubleshoot configuration issues:

```python
import logging
from triad.models.model_config import get_model_config

# Enable debug logging
logging.getLogger('pydantic_ai').setLevel(logging.DEBUG)
logging.getLogger('triad').setLevel(logging.DEBUG)

# Test configuration
config = get_model_config()
try:
    agents = create_constitutional_agents()
    print("✅ All agents created successfully")
except Exception as e:
    print(f"❌ Configuration error: {e}")
```

## Performance Optimization

### Provider Selection Guidelines

- **Groq**: Fastest inference, use for real-time interactions
- **OpenAI**: Best general performance, good for all roles
- **Anthropic**: Superior reasoning, excellent for Evaluator role
- **Gemini**: Good balance of speed and quality
- **Local models**: Best privacy, higher latency

### Cost Optimization

1. **Use cheaper models for routine tasks**
2. **Configure higher-cost models as fallbacks only**
3. **Set appropriate max_tokens limits**
4. **Monitor usage with Logfire integration**

## Integration with Parliamentary System

The model-agnostic configuration integrates seamlessly with the Westminster Parliamentary system:

- **Constitutional Oversight**: All model interactions are logged with constitutional context
- **Parliamentary Accountability**: Agent decisions are traceable through Logfire
- **Role-Based Access**: Different models can be assigned to different constitutional roles
- **Democratic Process**: Multiple models ensure no single point of failure

This flexibility allows organizations to:
- Use preferred AI providers
- Maintain regulatory compliance
- Optimize for cost and performance
- Ensure system reliability through redundancy
- Adapt to changing AI landscape

The Westminster Parliamentary AI System's model-agnostic design ensures that democratic principles and constitutional governance remain consistent regardless of the underlying AI technology.