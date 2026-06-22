import argparse
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib.utils import require_tier, get_anthropic_client, get_claude_model, call_claude, read_file, write_file
from lib.utils import print_header, print_success, print_info, print_error

def main():
    parser = argparse.ArgumentParser(description="Map out what breaks across projects for a given change.")
    parser.add_argument("--change", type=str, required=True, help="Description of the proposed change")
    parser.add_argument("--save", action="store_true", help="Save the analysis to impact-analysis.md")
    args = parser.parse_args()

    config = require_tier(['BEAST', 'BNDL'])
    print_header("Impact Analysis (Beastmode)")
    
    master = read_file(config.get("master_path", "MASTER.md"))
    threads = read_file(config.get("threads_path", "free/templates/thread-tracker.md"))
    decisions = read_file(config.get("decisions_path", "free/templates/decision-log.md"))
    
    print_info(f"Analyzing impact of: {args.change}")
    
    client = get_anthropic_client(config)
    model = get_claude_model(config)

    system_prompt = "You are SML-RECALL Beastmode Impact Analyzer. Assess the provided CHANGE against the MASTER, THREADS, and DECISIONS. Return a structured report: 1. Direct Impact 2. Indirect Impact 3. Safe Items 4. Risk Level (LOW/MEDIUM/HIGH/CRITICAL) 5. Pre-change Checklist."
    
    user_prompt = f"CHANGE:\n{args.change}\n\nMASTER:\n{master}\n\nTHREADS:\n{threads}\n\nDECISIONS:\n{decisions}\n\nProvide the impact report."

    report = call_claude(client, model, system_prompt, user_prompt)
    
    print("\n" + report + "\n")
    
    if args.save:
        write_file("impact-analysis.md", report)
        print_success("Saved report to impact-analysis.md.")

if __name__ == "__main__":
    main()
