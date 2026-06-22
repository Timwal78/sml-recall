import argparse
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib.utils import require_tier, get_anthropic_client, get_claude_model, call_claude, read_file
from lib.utils import print_header, print_success, print_info, print_error

def main():
    parser = argparse.ArgumentParser(description="Picks the right context and produces the optimal session-start prompt.")
    parser.add_argument("--task", type=str, required=True, help="Task you are about to start")
    args = parser.parse_args()

    config = require_tier(['BEAST', 'BNDL'])
    print_header("Thread Router (Beastmode)")
    
    master = read_file(config.get("master_path", "MASTER.md"))
    threads = read_file(config.get("threads_path", "free/templates/thread-tracker.md"))
    decisions = read_file(config.get("decisions_path", "free/templates/decision-log.md"))
    
    print_info(f"Routing task: {args.task}")
    
    client = get_anthropic_client(config)
    model = get_claude_model(config)

    system_prompt = "You are SML-RECALL Beastmode Thread Router. Analyze the user's TASK against all provided RECALL files. Determine the most critical context needed. Synthesize a maximum signal, <200 word prompt that the user can paste into a brand new Claude session to start this task perfectly. Output ONLY the raw prompt."
    
    user_prompt = f"TASK:\n{args.task}\n\nMASTER:\n{master}\n\nTHREADS:\n{threads}\n\nDECISIONS:\n{decisions}\n\nProvide the optimal <200 word start prompt."

    prompt = call_claude(client, model, system_prompt, user_prompt)
    
    print_info("--- OPTIMAL SESSION-START PROMPT ---")
    print(f"\n{prompt}\n")
    print_success("Ready to copy to your clipboard.")

if __name__ == "__main__":
    main()
