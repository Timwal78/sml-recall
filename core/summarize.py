import argparse
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib.utils import require_tier, get_anthropic_client, get_claude_model, call_claude, read_file, write_file
from lib.utils import print_header, print_success, print_info, print_error

def main():
    parser = argparse.ArgumentParser(description="Summarize a Claude session into MASTER.md updates")
    parser.add_argument("--file", help="Path to transcript file. If omitted, reads from stdin.")
    args = parser.parse_args()

    # Authenticate Tier
    config = require_tier(['CORE', 'BEAST', 'BNDL'])
    
    print_header("Summarize Session")
    
    transcript = ""
    if args.file:
        print_info(f"Reading transcript from {args.file}...")
        transcript = read_file(args.file)
    else:
        print_info("Paste transcript below and press Ctrl-D (Unix) or Ctrl-Z (Windows) when done:")
        transcript = sys.stdin.read()

    if not transcript.strip():
        print_error("Empty transcript.")
        sys.exit(1)

    master_path = config.get("master_path", "MASTER.md")
    master_content = read_file(master_path)
    if not master_content:
        print_error(f"Could not read {master_path}.")
        sys.exit(1)

    print_info("Analyzing transcript and generating MASTER.md updates via Claude...")
    client = get_anthropic_client(config)
    model = get_claude_model(config)

    system_prompt = "You are SML-RECALL, an external brain system. Given the current MASTER.md and a session transcript, output the necessary changes to MASTER.md to capture new context, decisions, and progress. Return ONLY the new suggested MASTER.md content."
    
    user_prompt = f"CURRENT MASTER.md:\n\n{master_content}\n\nTRANSCRIPT:\n\n{transcript}\n\nProvide the updated MASTER.md content based on the transcript."

    updated_master = call_claude(client, model, system_prompt, user_prompt)
    
    print_info(f"Saving updates to {master_path}...")
    write_file(master_path, updated_master)
    print_success("MASTER.md updated successfully.")

if __name__ == "__main__":
    main()
