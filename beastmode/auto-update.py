import argparse
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib.utils import require_tier, get_anthropic_client, get_claude_model, call_claude, read_file, write_file
from lib.utils import print_header, print_success, print_info, print_error, print_warning

def main():
    parser = argparse.ArgumentParser(description="Detect stale projects and generate targeted update questions.")
    parser.add_argument("--days", type=int, default=7, help="Threshold in days to consider an entry stale")
    parser.add_argument("--save", action="store_true", help="Save questions to update-queue.md")
    args = parser.parse_args()

    config = require_tier(['BEAST', 'BNDL'])
    print_header("Auto Update (Beastmode)")
    
    master_path = config.get("master_path", "MASTER.md")
    master = read_file(master_path)
    if not master:
        print_error(f"Missing {master_path}.")
        sys.exit(1)

    print_info(f"Scanning for projects older than {args.days} days...")
    
    client = get_anthropic_client(config)
    model = get_claude_model(config)

    system_prompt = f"You are SML-RECALL Beastmode. Scan the provided MASTER.md. Identify projects or threads that have not been touched in >{args.days} days based on their dates. For each stale project, generate 1-2 highly targeted questions to prompt the user for an update. Output a clear list of projects and their questions."
    user_prompt = f"MASTER:\n{master}\n\nFind stale items and generate questions."

    result = call_claude(client, model, system_prompt, user_prompt)
    
    print("\n" + result + "\n")
    
    if args.save:
        write_file("update-queue.md", result)
        print_success("Saved targeted questions to update-queue.md.")

if __name__ == "__main__":
    main()
