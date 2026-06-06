import os
import base64
import json
from pathlib import Path
from googleapiclient.http import MediaFileUpload

from scripts.auth_helper import get_blogger_service


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


def create_post(
    title: str,
    body_html: str,
    image_urls: list = None,
    labels: list = None,
    post_id_for_images: str = None,
) -> dict:
    service = get_blogger_service()
    blog_id = os.environ.get("BLOGGER_BLOG_ID")
    if not blog_id:
        raise ValueError("BLOGGER_BLOG_ID environment variable not set")

    if labels is None:
        labels = ["Islamic Guide", "Hajj", "Umrah", "Ramadan"]

    images_html = ""
    if image_urls:
        for url in image_urls:
            if url:
                images_html += f'<div style="text-align: center; margin-bottom: 20px;"><img src="{url}" style="max-width: 100%; height: auto; border-radius: 8px;" /></div>\n'

    content = images_html + body_html

    post_body = {
        "kind": "blogger#post",
        "title": title,
        "content": content,
        "labels": labels,
    }

    created_post = (
        service.posts().insert(blogId=blog_id, body=post_body, isDraft=False).execute()
    )

    return {
        "post_id": created_post.get("id", ""),
        "post_url": created_post.get("url", ""),
        "published": created_post.get("published", ""),
    }


def post_article_with_images(
    title: str, body: str, image_paths: list, alt_texts: list = None, labels: list = None
) -> dict:
    service = get_blogger_service()
    blog_id = os.environ.get("BLOGGER_BLOG_ID")

    if labels is None:
        labels = ["Islamic Guide"]

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
    if alt_texts is None:
        alt_texts = ["Featured image"] * len(image_urls)

    for i, url in enumerate(image_urls):
        alt = alt_texts[i] if i < len(alt_texts) else "Islamic guide blog image"
        images_html += (
            f'<div style="text-align:center;margin-bottom:20px;">'
            f'<img src="{url}" alt="{alt}" '
            f'style="max-width:100%;height:auto;border-radius:8px;" /></div>\n'
        )

    full_content = images_html + body

    updated_post = (
        service.posts()
        .update(
            blogId=blog_id,
            postId=post_id,
            body={
                "kind": "blogger#post",
                "title": title,
                "content": full_content,
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
