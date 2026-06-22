import argparse
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib.utils import require_tier, get_anthropic_client, get_claude_model, call_claude, read_file
from lib.utils import print_header, print_success, print_info, print_error, print_warning

def main():
    parser = argparse.ArgumentParser(description="Check proposed changes against decision-log.md")
    parser.add_argument("--proposal", type=str, help="The proposed change text")
    parser.add_argument("--file", type=str, help="Path to a file containing the proposed change")
    args = parser.parse_args()

    if not args.proposal and not args.file:
        print_error("Must provide either --proposal or --file")
        sys.exit(1)

    config = require_tier(['CORE', 'BEAST', 'BNDL'])
    print_header("Decision Checker")
    
    proposal_text = args.proposal
    if args.file:
        proposal_text = read_file(args.file)
        if not proposal_text:
            print_error(f"Could not read {args.file}")
            sys.exit(1)

    decisions_path = config.get("decisions_path", "free/templates/decision-log.md")
    decisions = read_file(decisions_path)
    
    if not decisions:
        print_warning(f"Could not read {decisions_path}. Assuming NO CONFLICTS.")
        print_success("NO CONFLICTS")
        sys.exit(0)

    print_info("Checking proposal against decision history...")
    
    client = get_anthropic_client(config)
    model = get_claude_model(config)

    system_prompt = "You are SML-RECALL Decision Checker. Compare the PROPOSAL against the DECISION LOG. Determine if the proposal conflicts with any past decisions. You MUST output exactly one of these phrases on the first line: 'CONFLICT DETECTED', 'NO CONFLICTS', or 'INSUFFICIENT HISTORY'. Then on the next lines, provide a brief 1-2 sentence explanation."
    
    user_prompt = f"DECISION LOG:\n{decisions}\n\nPROPOSAL:\n{proposal_text}\n\nAnalyze for conflicts."

    result = call_claude(client, model, system_prompt, user_prompt)
    
    first_line = result.split('\n')[0].strip().upper()
    
    if "CONFLICT DETECTED" in first_line:
        print_error("CONFLICT DETECTED")
        print(result)
    elif "NO CONFLICTS" in first_line:
        print_success("NO CONFLICTS")
        print(result)
    elif "INSUFFICIENT HISTORY" in first_line:
        print_warning("INSUFFICIENT HISTORY")
        print(result)
    else:
        # Fallback if Claude didn't follow format exactly
        print_info("ANALYSIS RESULT:")
        print(result)

if __name__ == "__main__":
    main()
