import argparse
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib.utils import require_tier, get_anthropic_client, get_claude_model, call_claude, read_file
from lib.utils import print_header, print_success, print_info, print_error

def main():
    parser = argparse.ArgumentParser(description="Extract relevant context slice for a project or task.")
    parser.add_argument("--project", type=str, help="Project name")
    parser.add_argument("--task", type=str, help="Task description")
    args = parser.parse_args()

    if not args.project and not args.task:
        print_error("Must provide either --project or --task")
        sys.exit(1)

    config = require_tier(['BEAST', 'BNDL'])
    print_header("Context Engine (Beastmode)")
    
    master = read_file(config.get("master_path", "MASTER.md"))
    threads = read_file(config.get("threads_path", "free/templates/thread-tracker.md"))
    decisions = read_file(config.get("decisions_path", "free/templates/decision-log.md"))
    
    print_info("Slicing context across all RECALL files...")
    
    client = get_anthropic_client(config)
    model = get_claude_model(config)

    focus = f"Project: {args.project}" if args.project else f"Task: {args.task}"
    
    system_prompt = f"You are SML-RECALL Beastmode Context Engine. Extract a <300 word focused context blob that is hyper-relevant to the user's focus. Ignore anything unrelated to the focus. Combine relevant info from MASTER, THREADS, and DECISIONS into a cohesive summary ready to paste to a new Claude session."
    
    user_prompt = f"FOCUS:\n{focus}\n\nMASTER:\n{master}\n\nTHREADS:\n{threads}\n\nDECISIONS:\n{decisions}\n\nProvide the focused context blob."

    blob = call_claude(client, model, system_prompt, user_prompt)
    
    print_info("--- FOCUSED CONTEXT BLOB ---")
    print(f"\n{blob}\n")
    print_success("Context sliced successfully.")

if __name__ == "__main__":
    main()
