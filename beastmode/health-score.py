import argparse
import sys
import os
import json
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib.utils import require_tier, get_anthropic_client, get_claude_model, call_claude, read_file
from lib.utils import print_header, print_success, print_info, print_error, Colors

def generate_health_score(config):
    master = read_file(config.get("master_path", "MASTER.md"))
    threads = read_file(config.get("threads_path", "free/templates/thread-tracker.md"))
    decisions = read_file(config.get("decisions_path", "free/templates/decision-log.md"))
    
    client = get_anthropic_client(config)
    model = get_claude_model(config)

    system_prompt = """You are SML-RECALL Beastmode Health Scorer. Evaluate the overall health of the user's RECALL setup based on the provided MASTER, THREADS, and DECISIONS files.
You must output a raw JSON object with exactly these fields:
{
  "completeness": 0-100 score,
  "freshness": 0-100 score,
  "actionability": 0-100 score,
  "clarity": 0-100 score,
  "decision_coverage": 0-100 score,
  "overall_grade": "A", "B", "C", "D", or "F",
  "summary": "1-2 sentence explanation"
}
Output ONLY the JSON, no markdown blocks, no other text."""
    
    user_prompt = f"MASTER:\n{master}\n\nTHREADS:\n{threads}\n\nDECISIONS:\n{decisions}\n\nProvide the JSON health report."

    try:
        raw_result = call_claude(client, model, system_prompt, user_prompt)
        # Clean up if Claude put markdown blocks
        if raw_result.startswith("```json"):
            raw_result = raw_result.replace("```json", "").replace("```", "").strip()
        elif raw_result.startswith("```"):
            raw_result = raw_result.replace("```", "").strip()
            
        return json.loads(raw_result)
    except Exception as e:
        print_error(f"Failed to generate health score: {e}")
        return None

def display_score(score_data):
    grade = score_data.get('overall_grade', 'N/A')
    color = Colors.GREEN if grade in ['A', 'B'] else Colors.GOLD if grade == 'C' else Colors.RED
    
    print(f"\n{color}{Colors.BOLD}OVERALL GRADE: {grade}{Colors.RESET}\n")
    print(f"Completeness:       {score_data.get('completeness', 0)}/100")
    print(f"Freshness:          {score_data.get('freshness', 0)}/100")
    print(f"Actionability:      {score_data.get('actionability', 0)}/100")
    print(f"Clarity:            {score_data.get('clarity', 0)}/100")
    print(f"Decision Coverage:  {score_data.get('decision_coverage', 0)}/100")
    print(f"\n{Colors.CYAN}Summary:{Colors.RESET} {score_data.get('summary', '')}\n")

def main():
    parser = argparse.ArgumentParser(description="AI-scored health report on the whole RECALL setup.")
    parser.add_argument("--json", action="store_true", help="Machine-readable output")
    parser.add_argument("--watch", action="store_true", help="Poll every 60s")
    args = parser.parse_args()

    config = require_tier(['BEAST', 'BNDL'])
    
    if not args.json:
        print_header("Health Score (Beastmode)")

    while True:
        if not args.json:
            print_info("Analyzing RECALL setup health...")
            
        score_data = generate_health_score(config)
        
        if score_data:
            if args.json:
                print(json.dumps(score_data, indent=2))
            else:
                display_score(score_data)
        
        if not args.watch:
            break
            
        if not args.json:
            print_info("Watching... next update in 60s. Press Ctrl+C to stop.")
            
        try:
            time.sleep(60)
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()
