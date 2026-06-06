import os
import re
import sys
import json
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import requests


PROMPT_TEMPLATE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "prompts",
    "article_prompt.txt",
)


def read_prompt_template() -> str:
    with open(PROMPT_TEMPLATE_PATH, "r", encoding="utf-8") as f:
        return f.read()


FALLBACK_MODELS = [
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",
]


def _gemini_text(prompt: str, model: str = "") -> str:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")

    api_endpoint = os.environ.get(
        "GEMINI_API_ENDPOINT",
        "https://generativelanguage.googleapis.com/v1beta",
    )

    models_to_try = [model] if model else FALLBACK_MODELS[:]

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 8192,
        },
    }

    last_error = None
    for m in models_to_try:
        url = f"{api_endpoint}/models/{m}:generateContent?key={api_key}"
        max_retries = 5
        for attempt in range(max_retries):
            try:
                resp = requests.post(url, json=payload, timeout=180)
            except requests.Timeout:
                wait = min(10 * (2 ** attempt), 120)
                print(f"  Timeout on {m}. Retrying in {wait}s... (attempt {attempt+1}/{max_retries})")
                time.sleep(wait)
                continue
            except requests.ConnectionError as e:
                wait = min(10 * (2 ** attempt), 120)
                print(f"  Connection error on {m}. Retrying in {wait}s...")
                time.sleep(wait)
                continue

            if resp.status_code == 429:
                wait = min(5 * (2 ** attempt), 120)
                print(f"  Rate limited on {m}. Waiting {wait}s... (attempt {attempt+1}/{max_retries})")
                time.sleep(wait)
                continue
            if resp.status_code in (503, 500):
                if attempt < max_retries - 1:
                    wait = min(10 * (2 ** attempt), 60)
                    print(f"  {m} returned {resp.status_code}. Retrying in {wait}s... (attempt {attempt+1}/{max_retries})")
                    time.sleep(wait)
                    continue
                print(f"  {m} failed after {max_retries} retries. Trying next model...")
                last_error = f"Model {m} unavailable (503)"
                break
            if resp.status_code == 403:
                print("  API key invalid or forbidden. Check your key at https://aistudio.google.com/app/apikey")
                raise RuntimeError("Gemini API key invalid (403 Forbidden)")
            resp.raise_for_status()
            data = resp.json()
            try:
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                return text.strip()
            except (KeyError, IndexError):
                raise RuntimeError(
                    f"Gemini API error: {json.dumps(data, indent=2)[:500]}"
                )
        else:
            if not last_error:
                last_error = f"Model {m} rate limited after {max_retries} retries"

    raise RuntimeError(
        f"Gemini API failed. {last_error}. "
        f"All models exhausted. "
        f"Get a new key at https://aistudio.google.com/app/apikey"
    )

def generate_article(subtopic: str) -> dict:
    template = read_prompt_template()
    prompt = template.replace("{subtopic}", subtopic)

    raw = _gemini_text(prompt)

    lines = raw.split("\n")
    title = lines[0].strip().strip("#").strip()

    seo_marker = "----------------------------"
    seo_section_marker = "SEO METADATA"
    image_prompt_marker = "Image Prompt:"

    seo_start = raw.find(seo_section_marker)

    image_prompt_start = raw.find(image_prompt_marker)
    if image_prompt_start != -1:
        body = raw[len(lines[0]) : image_prompt_start].strip()
    elif seo_start != -1:
        body = raw[len(lines[0]) : seo_start].strip()
    else:
        body = raw[len(lines[0]) :].strip()

    image_prompt = ""
    alt_text = ""

    if image_prompt_start != -1:
        prompt_text = raw[image_prompt_start + len(image_prompt_marker):]
        next_sep = prompt_text.find(seo_marker)
        if next_sep != -1:
            image_prompt = prompt_text[:next_sep].strip()
        else:
            image_prompt = prompt_text.strip()

    word_count = len(body.split())

    focus_keyword = ""
    meta_description = ""
    slug = ""
    faq = ""

    seo_section = ""
    if seo_start != -1:
        seo_section = raw[seo_start:]

    kw_match = re.search(r"FOCUS KEYWORD:\s*(.+)", seo_section)
    if kw_match:
        focus_keyword = kw_match.group(1).strip()

    md_match = re.search(r"META DESCRIPTION:\s*(.+)", seo_section)
    if md_match:
        meta_description = md_match.group(1).strip()

    slug_match = re.search(r"SLUG:\s*(.+)", seo_section)
    if slug_match:
        slug = slug_match.group(1).strip()

    faq_match = re.search(r"FAQ:\s*(.+)", seo_section, re.DOTALL)
    if faq_match:
        faq = faq_match.group(1).strip()

    if not image_prompt:
        image_prompt = (
            f"Modern Islamic blog featured image about {subtopic}, "
            f"elegant green and gold gradient background, minimalist luxury design, "
            f"soft abstract layered shapes, clean editorial layout, "
            f"premium lighting, peaceful spiritual atmosphere, high-quality blog cover design"
        )

    if not alt_text:
        alt_text = f"Islamic guide blog post about {subtopic}"

    return {
        "title": title,
        "body": body,
        "image_prompt": image_prompt,
        "alt_text": alt_text,
        "focus_keyword": focus_keyword,
        "meta_description": meta_description,
        "slug": slug,
        "faq": faq,
        "word_count": word_count,
        "raw": raw,
    }


if __name__ == "__main__":
    import sys

    topic = sys.argv[1] if len(sys.argv) > 1 else "Hajj and Umrah pilgrimage steps"
    result = generate_article(topic)
    print(f"Title: {result['title']}\n")
    print(f"Words: {result['word_count']}\n")
    print(f"Image Prompt: {result['image_prompt'][:100]}...\n")
    print(f"Body preview: {result['body'][:200]}...")
