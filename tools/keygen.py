import argparse
import random
import string
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib.utils import print_header, print_success, print_info

def generate_key_segment():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))

def generate_key(prefix):
    return f"{prefix}-{generate_key_segment()}-{generate_key_segment()}-{generate_key_segment()}-{generate_key_segment()}"

def main():
    parser = argparse.ArgumentParser(description="SML-RECALL Bulk Key Generator")
    parser.add_argument("--tier", choices=["CORE", "BEAST", "BNDL"], help="Generate keys for a specific tier")
    parser.add_argument("--all", type=int, help="Generate N keys for ALL tiers (Core, Beastmode, Bundle)", metavar="N")
    parser.add_argument("--count", type=int, default=10, help="Number of keys to generate (default: 10)")
    
    args = parser.parse_args()

    print_header("SML-RECALL Key Generator")

    if args.all:
        print_info(f"Generating {args.all} keys per tier...")
        tiers = ["CORE", "BEAST", "BNDL"]
        for t in tiers:
            print(f"\n--- {t} TIER KEYS ---")
            for _ in range(args.all):
                print(generate_key(t))
        print_success(f"\nGenerated {args.all * 3} keys total.")
        
    elif args.tier:
        print_info(f"Generating {args.count} {args.tier} keys...")
        for _ in range(args.count):
            print(generate_key(args.tier))
        print_success(f"\nGenerated {args.count} {args.tier} keys.")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
