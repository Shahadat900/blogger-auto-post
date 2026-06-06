import os
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.auth_helper import verify_blog_with_api_key

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")


def load_config() -> dict:
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    return {}


def save_config(config: dict):
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)


def main():
    print("=" * 55)
    print("  Connect Your Blogger Blog")
    print("=" * 55)
    print()
    print("How to get these credentials:")
    print("  1. Go to https://console.cloud.google.com")
    print("  2. Create a project or select existing")
    print("  3. Enable Blogger API v3")
    print("  4. Credentials -> Create API Key")
    print("  5. Restrict the key to Blogger API v3")
    print("  6. Get your Blog ID from Blogger Settings page")
    print()

    config = load_config()

    blog_name = input("Blog Name [My Awesome Blog]: ").strip()
    if not blog_name:
        blog_name = "My Awesome Blog"

    blog_url = input("Blog URL [https://myblog.blogspot.com]: ").strip()
    if not blog_url:
        blog_url = "https://myblog.blogspot.com"

    blog_id = input("Blog ID: ").strip()
    while not blog_id:
        blog_id = input("Blog ID (required): ").strip()

    api_key = input("API Key (AIzaSy...): ").strip()
    while not api_key:
        api_key = input("API Key (required, starts with AIzaSy): ").strip()

    print()
    print("Verifying blog connection...")

    try:
        blog_info = verify_blog_with_api_key(blog_id, api_key)
        print()
        print("  Blog Name:", blog_info.get("name", blog_name))
        print("  Blog URL:", blog_info.get("url", blog_url))
        print("  Total Posts:", blog_info.get("posts", "?"))
        print()
        print("  Connection successful!")
    except Exception as e:
        print(f"  Warning: Could not verify via API ({e})")
        print("  Saving anyway. Make sure the API Key and Blog ID are correct.")
        blog_info = {}

    config["blog_name"] = blog_name
    config["blog_url"] = blog_url
    config["blog_id"] = blog_id
    config["api_key"] = api_key

    if blog_info.get("name"):
        config["blog_name"] = blog_info["name"]
    if blog_info.get("url"):
        config["blog_url"] = blog_info["url"]

    save_config(config)
    print()
    print("  Saved to config.json")
    print()
    print("Next step: Run 'python scripts/setup_oauth.py' to get OAuth tokens for posting.")


if __name__ == "__main__":
    main()
