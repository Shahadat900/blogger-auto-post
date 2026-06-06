import re
import uuid
from datetime import datetime


def extract_headings(body_text: str) -> list:
    headings = []
    for line in body_text.split("\n"):
        line = line.strip()
        if line.startswith("## ") or line.startswith("# "):
            h = line.lstrip("#").strip()
            if h:
                headings.append(h)
    return headings


def build_toc_html(headings: list) -> str:
    if len(headings) < 3:
        return ""
    items = "".join(
        f'<li><a href="#{_slugify(h)}">{h}</a></li>' for h in headings
    )
    return (
        f'<div style="background:#f9f9f9;padding:15px 20px;border-radius:8px;'
        f'margin-bottom:25px;">'
        f'<h3 style="margin-top:0;">In This Article</h3>'
        f'<ul style="margin:0;padding-left:20px;">{items}</ul></div>'
    )


def _slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def build_schema_jsonld(
    title: str,
    body_text: str,
    blog_url: str,
    category: str,
    blog_name: str,
    word_count: int,
    image_url: str = "",
) -> str:
    schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "description": body_text[:160],
        "articleSection": category,
        "wordCount": word_count,
        "inLanguage": "en-US",
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": blog_url,
        },
        "publisher": {
            "@type": "Organization",
            "name": blog_name,
        },
        "datePublished": datetime.now().strftime("%Y-%m-%d"),
        "dateModified": datetime.now().strftime("%Y-%m-%d"),
        "author": {
            "@type": "Person",
            "name": blog_name,
        },
    }
    if image_url:
        schema["image"] = {"@type": "ImageObject", "url": image_url}
    return f'<script type="application/ld+json">{__import__("json").dumps(schema, indent=2)}</script>'


def build_faq_schema(faq_text: str) -> str:
    if not faq_text or faq_text.strip() in ("", "N/A", "none", "empty"):
        return ""
    items = []
    pairs = [p.strip() for p in faq_text.split("|") if p.strip()]
    for pair in pairs:
        if "Q:" in pair and "A:" in pair:
            q = pair.split("A:")[0].replace("Q:", "").strip()
            a = pair.split("A:", 1)[1].strip()
            items.append({
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a},
            })
    if not items:
        return ""
    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": items,
    }
    return f'<script type="application/ld+json">{__import__("json").dumps(schema, indent=2)}</script>'


def build_seo_html(
    title: str,
    body_html: str,
    body_text: str,
    category: str,
    blog_name: str,
    blog_url: str,
    focus_keyword: str = "",
    meta_description: str = "",
    faq_text: str = "",
    image_urls: list = None,
    word_count: int = 0,
) -> str:
    keyword = focus_keyword or category
    meta_desc = meta_description or body_text[:155]

    slug = _slugify(title)
    canonical = f"{blog_url.rstrip('/')}/{slug}.html"

    headings = extract_headings(body_text)
    toc_html = build_toc_html(headings)

    if image_urls:
        schema = build_schema_jsonld(
            title, body_text, canonical, category, blog_name, word_count, image_urls[0]
        )
    else:
        schema = build_schema_jsonld(
            title, body_text, canonical, category, blog_name, word_count
        )

    faq_schema = build_faq_schema(faq_text)

    html_parts = []

    html_parts.append(
        f'<div style="display:none;">'
        f'<meta itemprop="name" content="{title}"/>'
        f'<meta itemprop="description" content="{meta_desc}"/>'
        f'<meta itemprop="keywords" content="{keyword},{category}"/>'
        f'<meta property="article:tag" content="{category}"/>'
        f'<meta property="article:section" content="{category}"/>'
        f'<meta name="description" content="{meta_desc}"/>'
        f'<link rel="canonical" href="{canonical}"/>'
        f'</div>'
    )

    if toc_html:
        html_parts.append(toc_html)

    headings_in_html = re.findall(r"<h2>(.*?)</h2>", body_html)
    for h in headings_in_html:
        h_id = _slugify(h)
        html_parts.append(
            f'<div style="display:none;">'
            f'<meta property="article:tag" content="{h}"/>'
            f'</div>'
        )

    html_parts.append(schema)
    if faq_schema:
        html_parts.append(faq_schema)

    body_with_ids = body_html
    for h in headings_in_html:
        h_id = _slugify(h)
        old = f"<h2>{h}</h2>"
        new = f'<h2 id="{h_id}">{h}</h2>'
        body_with_ids = body_with_ids.replace(old, new)

    html_parts.append(body_with_ids)

    blog_link = blog_url.rstrip("/")
    html_parts.append(
        f'<div style="margin-top:30px;padding-top:15px;border-top:1px solid #eee;'
        f'font-size:14px;color:#666;">'
        f'<p><em>Originally published on <a href="{blog_link}">{blog_name}</a></em></p>'
        f'</div>'
    )

    return "\n".join(html_parts)
