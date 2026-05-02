"""
Usage:
  python inference.py --input hidden_private_dataset.json --output team_results.json
"""
import argparse, json, sys

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input",  required=True, help="Path to input JSON")
    parser.add_argument("--output", required=True, help="Path to output JSON")
    args = parser.parse_args()

    # Import after arg parse (avoids slow model load on --help)
    from src.pipeline import run_pipeline

    print(f"Reading: {args.input}")
    with open(args.input) as f:
        items = json.load(f)

    results = []
    for i, item in enumerate(items):
        query = item["query"]
        print(f"[{i+1}/{len(items)}] {query[:70]}")
        try:
            recs, latency = run_pipeline(query)
            std_ids       = [r["standard_id"] for r in recs]
        except Exception as e:
            print(f"  ERROR: {e}")
            std_ids = []
            latency = 0.0

        results.append({
            "id":                  item["id"],         # exact key
            "retrieved_standards": std_ids,            # exact key
            "latency_seconds":     latency,            # exact key
        })
        print(f"  {std_ids}  ({latency}s)")

    with open(args.output, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nDone. Saved to {args.output}")

if __name__ == "__main__":
    main()