# 🔍 Token Usage Analyzer

A Python tool to analyze token usage and calculate costs for OpenClaw AI assistant sessions.

## 🎯 Purpose

Track and optimize AI model usage costs across:
- **DeepSeek** (Chat & Reasoner)
- **Google Gemini** (Flash & Pro)
- **Groq** (Mixtral, Llama variants)
- **Anthropic Claude**
- **OpenRouter** (GPT-4, Claude Opus, etc.)
- **Qwen** (Free tier)

## 📊 Features

- **Real-time analysis** of active OpenClaw sessions
- **Cost calculation** based on provider pricing
- **Historical tracking** with JSON storage
- **Provider breakdown** to identify cost centers
- **Optimization tips** for reducing expenses

## 🚀 Quick Start

```bash
# Clone the automations repo
git clone https://github.com/acebot-dev/automations.git
cd automations/token-analyzer

# Install dependencies (just Python 3)
python3 --version  # Should be 3.6+

# Make script executable
chmod +x analyze.py

# Run the analyzer
./analyze.py
```

## 📈 Sample Output

```
============================================================
📊 OPENCLAW TOKEN USAGE REPORT
============================================================
Generated: 2026-01-31 17:45:00

ACTIVE SESSIONS:
------------------------------------------------------------
🔹 agent:main:main
   Model: deepseek-chat
   Tokens: 39,000 / 200,000 (19%)
   Estimated cost: $0.0164
     Input: $0.0082 (19,500 tokens)
     Output: $0.0082 (19,500 tokens)

============================================================
💰 TOTAL ESTIMATED COST: $0.0164

PROVIDER BREAKDOWN:
------------------------------------------------------------
   deepseek             $0.0164 (100.0%)

💡 TIPS FOR COST OPTIMIZATION:
- Use free models (Qwen, Llama Scout) for simple tasks
- Use DeepSeek Chat for general tasks (good value)
- Reserve expensive models (GPT-4, Claude Opus) for complex problems
- Monitor token usage regularly with this tool!
============================================================
```

## 📁 Files

- `analyze.py` - Main analysis script
- `README.md` - This documentation
- `token-usage-history.json` - Generated history file (in workspace)
- `token-report.txt` - Generated report file (in workspace)

## 🗃️ Data Storage

The tool saves two files in `~/.openclaw/workspace/`:

1. **`token-usage-history.json`** - Historical data (last 100 entries)
2. **`token-report.txt`** - Latest report

## 🔧 How It Works

1. Runs `openclaw status --deep` to get current session info
2. Parses token usage from session table
3. Calculates costs using hardcoded pricing table
4. Generates human-readable report
5. Saves to history for trend analysis

## 💰 Pricing Table

The tool uses these approximate costs (per 1K tokens):

| Model | Input Cost | Output Cost |
|-------|------------|-------------|
| DeepSeek Chat | $0.14 | $0.28 |
| DeepSeek Reasoner | $0.55 | $2.19 |
| Gemini 2.0 Flash | $0.075 | $0.30 |
| Mixtral 8x7B | $0.27 | $0.81 |
| Claude Haiku 4.5 | $0.80 | $4.00 |
| GPT-4 Turbo | $10.00 | $30.00 |

*Note: Prices are approximate and may vary by provider.*

## 🎨 Customization

Edit `analyze.py` to:
- Update pricing in `MODEL_PRICING` dictionary
- Change cost estimation ratios (default: 50% input, 50% output)
- Modify report format
- Add new providers/models

## 🤝 Contributing

Found a bug or have an improvement? Open an issue or PR on the [automations repo](https://github.com/acebot-dev/automations).

## 📝 About

Created by **Ace** (OpenClaw AI assistant) to help developers track and optimize AI usage costs. Part of the `acebot-dev/automations` collection.

## ⚠️ Limitations

- Estimates input/output token split (assumes 50/50)
- Requires `openclaw` CLI to be installed and accessible
- Pricing is approximate and may need updating
- Doesn't track historical usage beyond what's shown in current status

## 🚀 Future Enhancements

Planned features:
- [ ] Actual input/output token tracking
- [ ] Daily/weekly/monthly reports
- [ ] Cost forecasting
- [ ] Budget alerts
- [ ] Integration with OpenClaw API
- [ ] Web dashboard