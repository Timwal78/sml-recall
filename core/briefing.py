import argparse
import sys
import os
import pyperclip

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib.utils import require_tier, get_anthropic_client, get_claude_model, call_claude, read_file, write_file
from lib.utils import print_header, print_success, print_info, print_error

def main():
    parser = argparse.ArgumentParser(description="Generate a <200 word catch-up prompt for session starts.")
    parser.add_argument("--save", action="store_true", help="Save the briefing to briefing.md")
    parser.add_argument("--copy", action="store_true", help="Copy the briefing to clipboard")
    args = parser.parse_args()

    config = require_tier(['CORE', 'BEAST', 'BNDL'])
    
    print_header("Generate Session Briefing")
    
    master_path = config.get("master_path", "MASTER.md")
    threads_path = config.get("threads_path", "free/templates/thread-tracker.md")
    decisions_path = config.get("decisions_path", "free/templates/decision-log.md")
    
    # Read files
    master = read_file(master_path)
    threads = read_file(threads_path)
    decisions = read_file(decisions_path)
    
    if not master:
        print_error(f"Missing {master_path}.")
        sys.exit(1)

    print_info("Analyzing context files to generate briefing...")
    
    client = get_anthropic_client(config)
    model = get_claude_model(config)

    system_prompt = "You are SML-RECALL, generating a session-start briefing for Claude. You must output a highly condensed, <200 word prompt that the user can paste into a new Claude session. The prompt should instruct Claude on the current context, immediate blockers, and next actions, referencing the provided files. Output ONLY the raw briefing text, no conversational filler."
    
    user_prompt = f"MASTER:\n{master}\n\nTHREADS:\n{threads}\n\nDECISIONS:\n{decisions}\n\nGenerate the <200 word briefing prompt."

    briefing = call_claude(client, model, system_prompt, user_prompt)
    
    print_info("--- GENERATED BRIEFING ---")
    print(f"\n{briefing}\n")
    print_info("--------------------------")
    
    if args.save:
        write_file("briefing.md", briefing)
        print_success("Saved to briefing.md.")
        
    if args.copy:
        try:
            pyperclip.copy(briefing)
            print_success("Copied to clipboard.")
        except Exception as e:
            print_error(f"Failed to copy to clipboard: {e}")

if __name__ == "__main__":
    main()
