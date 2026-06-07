import os
import sys
import json
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

CONFIG_PATH = PROJECT_ROOT / "config.json"
POSTED_LOG_PATH = PROJECT_ROOT / "posted_log.json"

env_path = PROJECT_ROOT / ".env"
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def load_json(path: Path) -> dict:
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_json(path: Path, data: dict):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def body_to_html(body: str) -> str:
    paragraphs = body.strip().split("\n\n")
    html_parts = []
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        if p.startswith("## ") or p.startswith("# "):
            heading = p.lstrip("#").strip()
            html_parts.append(f"<h2>{heading}</h2>")
        elif p.startswith("- ") or p.startswith("* "):
            items = []
            for line in p.split("\n"):
                line = line.strip().lstrip("-").lstrip("*").strip()
                if line:
                    items.append(f"<li>{line}</li>")
            html_parts.append(f"<ul>{''.join(items)}</ul>")
        else:
            html_parts.append(f"<p>{p}</p>")
    return "\n".join(html_parts)





def main():
    print("=" * 50)
    print("  Islamic Guide - Auto Post System")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    config = load_json(CONFIG_PATH)
    posted_log = load_json(POSTED_LOG_PATH)

    subtopics = config.get("subtopics", [])
    if not subtopics:
        print("ERROR: No subtopics defined in config.json")
        sys.exit(1)

    current_index = config.get("current_index", 0)
    if current_index >= len(subtopics):
        current_index = 0

    entry = subtopics[current_index]
    if isinstance(entry, dict):
        subtopic = entry["topic"]
        category = entry.get("category", "Islam")
    else:
        subtopic = entry
        category = "Islam"

    print(f"\nTopic #{current_index + 1}: {subtopic}")
    print(f"Category: {category}")

    posted_key = subtopic.lower().strip()
    if posted_key in posted_log:
        print(f"SKIPPED: Already posted '{subtopic}' on {posted_log[posted_key]['date']}")
        current_index = (current_index + 1) % len(subtopics)
        config["current_index"] = current_index
        save_json(CONFIG_PATH, config)
        print(f"Advanced to next topic (index: {current_index})")
        sys.exit(0)

    from scripts.gemini_writer import generate_article

    print("\n[1/4] Generating article with Gemini...")
    article = generate_article(subtopic)

    title = article["title"]
    body = article["body"]
    word_count = article["word_count"]

    print(f"  Title: {title}")
    print(f"  Words: {word_count}")

    print(f"\n[2/4] Skipping images...")

    image_paths = []
    alt_texts = []

    print("\n[3/4] Posting to Blogger with SEO...")
    body_html = body_to_html(body)

    from scripts.post_to_blogger import post_article_with_images

    labels = ["Islamic Guide", category]
    result = post_article_with_images(
        title=title,
        body=body_html,
        image_paths=image_paths,
        alt_texts=alt_texts,
        labels=labels,
        body_text=body,
        focus_keyword=article.get("focus_keyword", ""),
        meta_description=article.get("meta_description", ""),
        faq_text=article.get("faq", ""),
        category=category,
        word_count=word_count,
    )

    post_id = result.get("post_id", "")
    post_url = result.get("post_url", "")
    published = result.get("published", "")

    print(f"  Post ID: {post_id}")
    print(f"  URL: {post_url}")
    print(f"  Published: {published}")

    posted_log[posted_key] = {
        "title": title,
        "subtopic": subtopic,
        "category": category,
        "post_id": post_id,
        "url": post_url,
        "date": published or datetime.now().isoformat(),
        "word_count": word_count,
    }
    save_json(POSTED_LOG_PATH, posted_log)



    current_index = (current_index + 1) % len(subtopics)
    config["current_index"] = current_index
    save_json(CONFIG_PATH, config)

    print(f"\n[4/4] Advanced to next topic (index: {current_index})")
    print(f"\nDONE: '{title}' posted successfully!")

    return result


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
