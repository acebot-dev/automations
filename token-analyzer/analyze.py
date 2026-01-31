#!/usr/bin/env python3
"""
Token Usage Analyzer for OpenClaw
Analyzes token usage and calculates costs across different AI models.
"""

import json
import subprocess
import re
from datetime import datetime
from pathlib import Path
import sys

# Model pricing (cost per 1K tokens)
MODEL_PRICING = {
    "deepseek-chat": {"input": 0.14, "output": 0.28},
    "deepseek-reasoner": {"input": 0.55, "output": 2.19},
    "gemini-2.0-flash": {"input": 0.075, "output": 0.30},
    "gemini-2.0-pro": {"input": 7.5, "output": 30.0},
    "mixtral-8x7b-32768": {"input": 0.27, "output": 0.81},
    "llama-3.1-8b-instant": {"input": 0.05, "output": 0.08},
    "llama-3.3-70b-versatile": {"input": 0.05, "output": 0.08},
    "llama-4-scout-17b-16e-instruct": {"input": 0.0, "output": 0.0},
    "claude-haiku-4-5": {"input": 0.8, "output": 4.0},
    "coder-model": {"input": 0.0, "output": 0.0},
    "vision-model": {"input": 0.0, "output": 0.0},
    "gpt-4-turbo": {"input": 10.0, "output": 30.0},
    "o1": {"input": 15.0, "output": 60.0},
    "claude-opus-4-1": {"input": 15.0, "output": 75.0},
    "llama-3.1-405b-instruct": {"input": 2.7, "output": 8.1},
    "mistral-large": {"input": 8.0, "output": 24.0},
}

def run_openclaw_status():
    """Run openclaw status --deep and parse output"""
    try:
        result = subprocess.run(
            ["openclaw", "status", "--deep"],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout
    except Exception as e:
        print(f"⚠️  Error running openclaw status: {e}")
        return ""

def parse_session_tokens(status_output):
    """Parse session token usage from status output"""
    sessions = []
    
    lines = status_output.split('\n')
    in_sessions = False
    
    for line in lines:
        if "Key" in line and "Kind" in line and "Age" in line and "Model" in line and "Tokens" in line:
            in_sessions = True
            continue
        
        if in_sessions:
            if line.startswith('└') or line.startswith('Health') or line.startswith('FAQ'):
                break
            
            # Parse session line - FIXED REGEX
            # Format: │ agent:main:main │ direct │ 1m ago │ deepseek-chat │ 39k/200k (19%) │
            # The "k" in "39k" is NOT a thousands separator, it's part of the number format
            match = re.search(r'│\s+([^│]+)\s+│\s+([^│]+)\s+│\s+([^│]+)\s+│\s+([^│]+)\s+│\s+([^│]+)\s+│', line)
            if match:
                key, kind, age, model, tokens = match.groups()
                key = key.strip()
                model = model.strip()
                tokens = tokens.strip()
                
                # Parse token usage (e.g., "39k/200k (19%)")
                # The "k" here is LITERAL, not a multiplier
                token_match = re.match(r'(\d+)([kKmM]?)\/(\d+)([kKmM]?)\s*\((\d+)%\)', tokens)
                if token_match:
                    used_num, used_suffix, limit_num, limit_suffix, percent = token_match.groups()
                    
                    # The "k" is part of the number format, NOT a thousands multiplier
                    # "39k" means 39 (with 'k' as suffix), not 39,000
                    used_tokens = float(used_num)  # Just the number part
                    limit_tokens = float(limit_num)  # Just the number part
                    
                    sessions.append({
                        'key': key,
                        'kind': kind.strip(),
                        'age': age.strip(),
                        'model': model,
                        'used_tokens': used_tokens,
                        'limit_tokens': limit_tokens,
                        'percent_used': int(percent)
                    })
    
    return sessions

def calculate_costs(sessions):
    """Calculate costs for each session based on model pricing"""
    total_cost = 0
    
    for session in sessions:
        model = session['model']
        
        pricing = None
        for model_key, price in MODEL_PRICING.items():
            if model_key in model or model in model_key:
                pricing = price
                break
        
        if pricing:
            # Estimate: assume 1:1 input:output ratio
            estimated_input_tokens = session['used_tokens'] * 0.5
            estimated_output_tokens = session['used_tokens'] * 0.5
            
            # Convert to thousands of tokens for cost calculation
            input_cost = (estimated_input_tokens / 1000) * pricing['input']
            output_cost = (estimated_output_tokens / 1000) * pricing['output']
            session_cost = input_cost + output_cost
            
            session['cost'] = session_cost
            session['input_tokens'] = estimated_input_tokens
            session['output_tokens'] = estimated_output_tokens
            session['input_cost'] = input_cost
            session['output_cost'] = output_cost
            session['pricing_model'] = model_key
            
            total_cost += session_cost
        else:
            session['cost'] = 0
            session['pricing_model'] = 'unknown'
            print(f"⚠️  No pricing found for model: {model}")
    
    return sessions, total_cost

def generate_report(sessions, total_cost):
    """Generate a human-readable report"""
    report = []
    report.append("=" * 60)
    report.append("📊 OPENCLAW TOKEN USAGE REPORT")
    report.append("=" * 60)
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    if not sessions:
        report.append("❌ No active sessions found")
        return "\n".join(report)
    
    report.append("ACTIVE SESSIONS:")
    report.append("-" * 60)
    
    for session in sessions:
        report.append(f"🔹 {session['key']}")
        report.append(f"   Model: {session['model']}")
        report.append(f"   Tokens: {session['used_tokens']} / {session['limit_tokens']} ({session['percent_used']}%)")
        
        if 'cost' in session:
            if session['cost'] > 0:
                report.append(f"   Estimated cost: ${session['cost']:.6f}")
                report.append(f"     Input: ${session['input_cost']:.6f} ({session['input_tokens']:.1f} tokens)")
                report.append(f"     Output: ${session['output_cost']:.6f} ({session['output_tokens']:.1f} tokens)")
            else:
                report.append(f"   Cost: FREE (using {session['pricing_model']})")
        report.append("")
    
    report.append("=" * 60)
    
    if total_cost > 0:
        report.append(f"💰 TOTAL ESTIMATED COST: ${total_cost:.6f}")
        report.append("")
        
        provider_costs = {}
        for session in sessions:
            if 'cost' in session and session['cost'] > 0:
                provider = session['model'].split('-')[0] if '-' in session['model'] else session['model']
                provider_costs[provider] = provider_costs.get(provider, 0) + session['cost']
        
        if provider_costs:
            report.append("PROVIDER BREAKDOWN:")
            report.append("-" * 60)
            for provider, cost in sorted(provider_costs.items(), key=lambda x: x[1], reverse=True):
                percentage = (cost / total_cost * 100) if total_cost > 0 else 0
                report.append(f"   {provider:20} ${cost:.6f} ({percentage:.1f}%)")
    else:
        report.append("💰 TOTAL COST: $0.00 (All free models!)")
    
    report.append("")
    report.append("💡 TIPS FOR COST OPTIMIZATION:")
    report.append("- Use free models (Qwen, Llama Scout) for simple tasks")
    report.append("- Use DeepSeek Chat for general tasks (good value)")
    report.append("- Reserve expensive models (GPT-4, Claude Opus) for complex problems")
    report.append("=" * 60)
    
    return "\n".join(report)

def main():
    print("🔍 Analyzing OpenClaw token usage...")
    
    status_output = run_openclaw_status()
    if not status_output:
        print("❌ Failed to get OpenClaw status")
        sys.exit(1)
    
    sessions = parse_session_tokens(status_output)
    
    if not sessions:
        print("⚠️  No active sessions found")
        sys.exit(0)
    
    sessions_with_costs, total_cost = calculate_costs(sessions)
    
    report = generate_report(sessions_with_costs, total_cost)
    print(report)
    
    # Save report
    report_file = Path.home() / ".openclaw" / "workspace" / "token-report-fixed.txt"
    with open(report_file, 'w') as f:
        f.write(report)
    print(f"\n📄 Report saved to: {report_file}")

if __name__ == "__main__":
    main()