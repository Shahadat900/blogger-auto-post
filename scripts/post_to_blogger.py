import os
import json
import sys
import base64
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.auth_helper import get_blogger_service

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.json"
def _load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def image_to_data_uri(image_path: str) -> str:
    with open(image_path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    return f"data:image/png;base64,{data}"


def post_article_with_images(
    title: str,
    body: str,
    image_paths: list,
    alt_texts: list = None,
    labels: list = None,
    body_text: str = "",
    focus_keyword: str = "",
    meta_description: str = "",
    faq_text: str = "",
    category: str = "",
    word_count: int = 0,
) -> dict:
    from scripts.seo_optimizer import build_seo_html

    cfg = _load_config()
    service = get_blogger_service()
    blog_id = os.environ.get("BLOGGER_BLOG_ID") or cfg.get("blog_id", "")
    blog_url = cfg.get("blog_url", "https://quranflow.blogspot.com")
    blog_name = cfg.get("blog_name", "Islamic Guide")

    if labels is None:
        labels = ["Islamic Guide"]
    if alt_texts is None:
        alt_texts = ["Featured image"] * len(image_paths)

    post_body = {
        "kind": "blogger#post",
        "title": title,
        "content": body,
        "labels": labels,
    }

    created_post = (
        service.posts().insert(blogId=blog_id, body=post_body, isDraft=True).execute()
    )

    images_html = ""
    for i, img_path in enumerate(image_paths):
        alt = alt_texts[i] if i < len(alt_texts) else "Islamic guide blog image"
        src = image_to_data_uri(img_path) if os.path.exists(img_path) else ""
        pos = "" if i > 0 else "position:relative;display:inline-block;max-width:100%;"
        title_overlay = ""
        if i == 0:
            title_overlay = (
                f'<div style="position:absolute;bottom:20px;left:20px;right:20px;'
                f'background:linear-gradient(transparent,rgba(0,0,0,.7));'
                f'padding:30px 20px 15px;border-radius:0 0 8px 8px;">'
                f'<h1 style="margin:0;color:#fff;font-size:clamp(18px,4vw,36px);'
                f'text-shadow:1px 1px 4px rgba(0,0,0,.5);">{title}</h1></div>'
            )
        images_html += (
            f'<div style="text-align:center;margin-bottom:20px;{pos}">'
            f'<img src="{src}" alt="{alt}" loading="lazy" '
            f'style="max-width:100%;height:auto;border-radius:8px;display:block;" />'
            f'{title_overlay}</div>\n'
        )

    full_html = images_html + body

    seo_html = build_seo_html(
        title=title,
        body_html=full_html,
        body_text=body_text or body,
        category=category or (labels[1] if len(labels) > 1 else "Islam"),
        blog_name=blog_name,
        blog_url=blog_url,
        focus_keyword=focus_keyword,
        meta_description=meta_description,
        faq_text=faq_text,
        image_urls=image_paths,
        word_count=word_count,
    )

    service.posts().update(
        blogId=blog_id,
        postId=created_post.get("id", ""),
        body={
            "kind": "blogger#post",
            "title": title,
            "content": seo_html,
            "labels": labels,
        },
    ).execute()

    updated_post = service.posts().publish(
        blogId=blog_id,
        postId=created_post.get("id", ""),
    ).execute()

    return {
        "post_id": updated_post.get("id", ""),
        "post_url": updated_post.get("url", ""),
        "published": updated_post.get("published", ""),
    }


if __name__ == "__main__":
    result = post_article_with_images(
        title="Test Post",
        body="<p>This is a test post from the auto-poster.</p>",
        image_paths=[],
    )
    print(json.dumps(result, indent=2))
