import os
import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import google.generativeai as genai

PROMPT_TEMPLATE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "prompts",
    "article_prompt.txt",
)


def read_prompt_template() -> str:
    with open(PROMPT_TEMPLATE_PATH, "r", encoding="utf-8") as f:
        return f.read()


def generate_article(subtopic: str) -> dict:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")

    genai.configure(api_key=api_key)

    template = read_prompt_template()
    prompt = template.replace("{subtopic}", subtopic)

    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)

    if not response.text:
        raise RuntimeError("Gemini returned empty response")

    raw = response.text.strip()

    lines = raw.split("\n")
    title = lines[0].strip().strip("#").strip()

    seo_marker = "----------------------------"
    images_marker = "UPDATED IMAGES REQUIREMENTS"
    seo_section_marker = "SEO METADATA"

    images_start = raw.find(images_marker)
    seo_start = raw.find(seo_section_marker)

    if images_start != -1:
        raw_body = raw[len(lines[0]) : images_start].strip()
        images_section = raw[images_start:]
    else:
        raw_body = raw[len(lines[0]) :].strip()
        images_section = ""

    body = raw_body
    if seo_start != -1 and images_start != -1:
        body = raw[len(lines[0]) : images_start].strip()
    elif seo_start != -1:
        body = raw[len(lines[0]) : seo_start].strip()

    image_prompt = ""
    alt_text = ""

    if images_section:
        prompt_match = re.search(
            r"IMAGE PROMPT:\s*(.+?)(?=ALT TEXT:|$)",
            images_section,
            re.DOTALL,
        )
        if prompt_match:
            image_prompt = prompt_match.group(1).strip()

        alt_match = re.search(
            r"ALT TEXT:\s*(.+?)(?=\n\n|\Z)", images_section, re.DOTALL
        )
        if alt_match:
            alt_text = alt_match.group(1).strip()

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
