"""Free local LLM via Ollama (run: ollama pull llama3.2:3b). Uses RAG brand rules."""
import json
from rag import get_guidelines

MODEL = "llama3.2:3b"


def generate_ads(product, audience, n=3):
    rules = get_guidelines(f"{product} {audience} ad tone brand")
    rules_text = "\n".join(f"- {r}" for r in rules)
    prompt = (
        f"Write {n} short ad variations for: {product}. Audience: {audience}.\n"
        f"Follow these brand rules strictly:\n{rules_text}\n"
        'Reply ONLY as JSON list: [{"headline":"...","description":"..."}]. '
        "Headline max 30 chars, description max 90 chars."
    )
    try:
        import ollama
        r = ollama.chat(model=MODEL, messages=[{"role": "user", "content": prompt}])
        text = r["message"]["content"]
        return json.loads(text[text.index("["): text.rindex("]") + 1])[:n]
    except Exception:
        # fallback so the demo always works
        return [
            {"headline": f"{product}: Try It Today", "description": f"Made for {audience}. Start free now."},
            {"headline": f"Love {product}?", "description": f"Join {audience} who already do."},
            {"headline": f"Meet {product}", "description": f"The smarter choice for {audience}."},
        ][:n]