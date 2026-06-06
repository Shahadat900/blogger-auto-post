import os
import re
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

    images_section_marker = "----------------------------"
    images_start = raw.find(images_section_marker)
    if images_start != -1:
        body = raw[len(lines[0]) : images_start].strip()
        images_section = raw[images_start:]
    else:
        body = raw[len(lines[0]) :].strip()
        images_section = ""

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
