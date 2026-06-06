import os
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from googleapiclient.http import MediaFileUpload

from scripts.auth_helper import get_blogger_service

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.json"
def _load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def upload_image(service, blog_id: str, image_path: str, post_id: str = None) -> str:
    media = MediaFileUpload(image_path, mimetype="image/png", resumable=True)

    if post_id:
        request = service.posts().media().insert(
            blogId=blog_id, postId=post_id, media_body=media
        )
    else:
        request = service.posts().media().insert(
            blogId=blog_id, media_body=media
        )

    result = request.execute()
    return result.get("url", "")


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

    post_id = created_post.get("id", "")

    image_urls = []
    for img_path in image_paths:
        if os.path.exists(img_path):
            url = upload_image(service, blog_id, img_path, post_id)
            image_urls.append(url)

    images_html = ""
    for i, url in enumerate(image_urls):
        alt = alt_texts[i] if i < len(alt_texts) else "Islamic guide blog image"
        images_html += (
            f'<div style="text-align:center;margin-bottom:20px;">'
            f'<img src="{url}" alt="{alt}" loading="lazy" '
            f'style="max-width:100%;height:auto;border-radius:8px;" /></div>\n'
        )

    full_html = images_html + body

    seo_html = build_seo_html(
        title=title,
        body_html=full_html,
        body_text=body_text or body,
        category=category or labels[1] if len(labels) > 1 else "Islam",
        blog_name=blog_name,
        blog_url=blog_url,
        focus_keyword=focus_keyword,
        meta_description=meta_description,
        faq_text=faq_text,
        image_urls=image_urls,
        word_count=word_count,
    )

    updated_post = (
        service.posts()
        .update(
            blogId=blog_id,
            postId=post_id,
            body={
                "kind": "blogger#post",
                "title": title,
                "content": seo_html,
                "labels": labels,
            },
            isDraft=False,
        )
        .execute()
    )

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
