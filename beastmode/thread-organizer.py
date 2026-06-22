import argparse
import sys
import os
import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib.utils import require_tier, get_anthropic_client, get_claude_model, call_claude, read_file, write_file
from lib.utils import print_header, print_success, print_info, print_error

def main():
    parser = argparse.ArgumentParser(description="Classify and organize threads.")
    parser.add_argument("--clean", action="store_true", help="Rewrite thread-tracker.md with only ACTIVE threads")
    parser.add_argument("--archive", action="store_true", help="Save closed entries to threads/archive-DATE.md")
    args = parser.parse_args()

    config = require_tier(['BEAST', 'BNDL'])
    print_header("Thread Organizer (Beastmode)")
    
    threads_path = config.get("threads_path", "free/templates/thread-tracker.md")
    threads = read_file(threads_path)
    
    if not threads:
        print_error(f"Missing {threads_path}.")
        sys.exit(1)

    print_info("Analyzing threads...")
    
    client = get_anthropic_client(config)
    model = get_claude_model(config)

    # Classify threads
    sys_classify = "You are SML-RECALL Beastmode. Look at the thread-tracker.md content. Separate the threads into two lists: 1) ACTIVE/BLOCKED threads 2) DONE/STALE threads. Format as raw markdown tables matching the original format."
    classified = call_claude(client, model, sys_classify, f"THREADS:\n{threads}")
    
    print("\n" + classified + "\n")

    if args.clean or args.archive:
        # Ask Claude to return JUST the ACTIVE ones for the clean file
        sys_active = "Extract ONLY the table of ACTIVE and BLOCKED threads from the content. Keep the markdown table format."
        active_only = call_claude(client, model, sys_active, f"CONTENT:\n{classified}")
        
        sys_done = "Extract ONLY the table of DONE and STALE threads from the content. Keep the markdown table format."
        done_only = call_claude(client, model, sys_done, f"CONTENT:\n{classified}")
        
        if args.clean:
            new_tracker = f"# THREAD TRACKER\n\n{active_only}"
            write_file(threads_path, new_tracker)
            print_success(f"Cleaned {threads_path} (kept only ACTIVE/BLOCKED).")
            
        if args.archive and "none" not in done_only.lower() and "|" in done_only:
            os.makedirs("threads", exist_ok=True)
            date_str = datetime.datetime.now().strftime("%Y-%m-%d")
            archive_path = f"threads/archive-{date_str}.md"
            write_file(archive_path, f"# ARCHIVED THREADS ({date_str})\n\n{done_only}")
            print_success(f"Archived DONE/STALE threads to {archive_path}.")

if __name__ == "__main__":
    main()
