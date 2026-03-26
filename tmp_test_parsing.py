
import json
import re

def _extract_json_from_llm_response_new(raw: str) -> str:
    """Robustly extracts JSON array from LLM output using regex."""
    raw = raw.strip()
    # Try to find the first '[' and last ']'
    match = re.search(r'(\[.*\])', raw, re.DOTALL)
    if match:
        return match.group(1).strip()
    return raw

def test_parsing():
    test_cases = [
        "```json\n[{\"q\":1}]\n```",
        "Here is the quiz:\n[{\"q\":1}]",
        "```\n[{\"q\":1}]\n```\nHope you like it!",
        "[{\"q\":1}]",
        "I cannot generate a quiz for that topic. []"
    ]
    
    for tc in test_cases:
        extracted = _extract_json_from_llm_response_new(tc)
        try:
            parsed = json.loads(extracted)
            print(f"PASS: {tc[:20]}... -> {parsed}")
        except json.JSONDecodeError:
            print(f"FAIL: {tc[:20]}... -> {extracted}")

if __name__ == "__main__":
    test_parsing()
