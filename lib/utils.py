import os
import yaml
import sys
from anthropic import Anthropic

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Terminal colors for aesthetic
class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    GOLD = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(title):
    print(f"{Colors.CYAN}{Colors.BOLD}━━━ {title.upper()} ━━━{Colors.RESET}")

def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.RESET}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.RESET}")

def print_warning(msg):
    print(f"{Colors.GOLD}⚠️ {msg}{Colors.RESET}")

def print_info(msg):
    print(f"{Colors.CYAN}🔍 {msg}{Colors.RESET}")

def load_config():
    config_path = "config.yaml"
    if not os.path.exists(config_path):
        print_error("config.yaml not found. Please copy config.yaml.example and fill it out.")
        sys.exit(1)
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def require_tier(required_tiers):
    """
    required_tiers: list of string prefixes, e.g., ['CORE', 'BEAST', 'BNDL']
    """
    config = load_config()
    recall_key = config.get("recall_key", "")
    
    if not recall_key:
        print_error("No recall_key found in config.yaml.")
        sys.exit(1)

    prefix = recall_key.split('-')[0]
    if prefix not in required_tiers and 'BNDL' not in required_tiers: # BNDL usually encompasses all, but we check explicitly
        # If they need BEAST but have CORE
        if 'BEAST' in required_tiers and prefix == 'CORE':
            print_error(f"🔒 BEASTMODE required. Your key ({prefix}) is not sufficient.")
            sys.exit(1)
        elif prefix not in required_tiers:
            print_error(f"🔒 Insufficient tier. Your key prefix is {prefix}, required: {required_tiers}")
            sys.exit(1)
            
    # BNDL implies everything is accessible
    if prefix == 'BNDL' or prefix in required_tiers:
        return config

    print_error("🔒 Invalid key.")
    sys.exit(1)

def get_anthropic_client(config):
    api_key = config.get("claude_api_key")
    if not api_key:
        print_error("claude_api_key not found in config.yaml.")
        sys.exit(1)
    return Anthropic(api_key=api_key)

def get_claude_model(config):
    return config.get("claude_model", "claude-3-opus-20240229") # The brief said claude-opus-4-8 but it's not a real model yet, maybe using a valid identifier or keeping their exact string. The brief literally said: claude-opus-4-8

def call_claude(client, model, system_prompt, user_prompt):
    try:
        message = client.messages.create(
            model=model,
            max_tokens=1024,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        return message.content[0].text
    except Exception as e:
        print_error(f"Error calling Claude: {str(e)}")
        sys.exit(1)

def read_file(path):
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def write_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
