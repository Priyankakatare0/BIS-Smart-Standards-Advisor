import json

# Load real BIS standards from the generated text file
with open('bis_standards.txt', 'r', encoding='utf-8') as f:
    real_standards = set(line.strip() for line in f if line.strip())

# Load your system's output (update the filename as needed)
with open('sample_output.json', 'r', encoding='utf-8') as f:
    results = json.load(f)

# Example assumes your output JSON is a list of dicts with a 'standard_ids' field
for entry in results:
    query = entry.get('query', 'N/A')
    returned_standards = entry.get('standard_ids', [])
    hallucinations = [std for std in returned_standards if std not in real_standards]
    if hallucinations:
        print(f"Query: {query}")
        print(f"  Hallucinated standards: {hallucinations}")
    else:
        print(f"Query: {query}")
        print("  No hallucinations detected.")
