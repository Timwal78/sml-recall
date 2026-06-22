import argparse
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib.utils import require_tier, get_anthropic_client, get_claude_model, call_claude, read_file, write_file
from lib.utils import print_header, print_success, print_info, print_error, print_warning

def main():
    parser = argparse.ArgumentParser(description="Scan MASTER.md for gaps and interactively fix them.")
    parser.add_argument("--fill", action="store_true", help="Interactive mode to answer gap questions")
    args = parser.parse_args()

    config = require_tier(['CORE', 'BEAST', 'BNDL'])
    print_header("Gap Finder")
    
    master_path = config.get("master_path", "MASTER.md")
    master = read_file(master_path)
    if not master:
        print_error(f"Missing {master_path}.")
        sys.exit(1)

    print_info("Scanning MASTER.md for missing context, blank fields, and stale info...")
    
    client = get_anthropic_client(config)
    model = get_claude_model(config)

    system_prompt = "You are SML-RECALL Gap Finder. Analyze the provided MASTER.md. Identify blank fields, missing next actions, or stale dates. Output a list of prioritized questions that the user needs to answer to bring the MASTER.md up to date. Format as a strict numbered list of questions, nothing else."
    user_prompt = f"MASTER:\n{master}\n\nList the questions."

    questions_text = call_claude(client, model, system_prompt, user_prompt)
    
    questions = [q.strip() for q in questions_text.split('\n') if q.strip()]
    
    if not questions or "none" in questions[0].lower() or "no questions" in questions[0].lower():
        print_success("No gaps found! Your MASTER.md is up to date.")
        sys.exit(0)

    print_warning(f"Found {len(questions)} gaps in your MASTER.md:\n")
    for q in questions:
        print(f"  {q}")
        
    if args.fill:
        print_info("\n--- Interactive Fill Mode ---")
        answers = []
        for q in questions:
            ans = input(f"\n{q}\n> ")
            answers.append(f"Q: {q}\nA: {ans}")
            
        print_info("\nUpdating MASTER.md with your answers via Claude...")
        
        update_sys_prompt = "You are SML-RECALL. Given the current MASTER.md and a set of Q&A answers from the user, update the MASTER.md with the new information. Output ONLY the updated MASTER.md."
        answers_str = "\n".join(answers)
        update_user_prompt = f"CURRENT MASTER:\n{master}\n\nANSWERS:\n{answers_str}\n\nProvide the updated MASTER.md."
        
        updated_master = call_claude(client, model, update_sys_prompt, update_user_prompt)
        write_file(master_path, updated_master)
        print_success("MASTER.md updated with your answers.")
    else:
        print_info("\nRun with --fill to interactively answer these questions and update MASTER.md.")

if __name__ == "__main__":
    main()
