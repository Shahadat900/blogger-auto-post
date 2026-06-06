import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

SCOPES = ["https://www.googleapis.com/auth/blogger"]


def get_credentials():
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request

    client_id = os.environ.get("BLOGGER_CLIENT_ID")
    client_secret = os.environ.get("BLOGGER_CLIENT_SECRET")
    refresh_token = os.environ.get("BLOGGER_REFRESH_TOKEN")

    missing = []
    if not client_id:
        missing.append("BLOGGER_CLIENT_ID")
    if not client_secret:
        missing.append("BLOGGER_CLIENT_SECRET")
    if not refresh_token:
        missing.append("BLOGGER_REFRESH_TOKEN")

    if missing:
        raise ValueError(
            f"Missing OAuth environment variables: {', '.join(missing)}. "
            f"Run 'python scripts/setup_oauth.py' to generate them."
        )

    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        client_id=client_id,
        client_secret=client_secret,
        token_uri="https://oauth2.googleapis.com/token",
        scopes=SCOPES,
    )

    if not creds.valid:
        creds.refresh(Request())

    return creds


def get_blogger_service():
    from googleapiclient.discovery import build

    creds = get_credentials()
    service = build("blogger", "v3", credentials=creds)
    return service


def verify_blog_with_api_key(blog_id: str, api_key: str) -> dict:
    import requests

    url = f"https://www.googleapis.com/blogger/v3/blogs/{blog_id}?key={api_key}"
    resp = requests.get(url)
    if resp.status_code != 200:
        raise ConnectionError(
            f"Blogger API error: {resp.status_code} - {resp.text}"
        )
    data = resp.json()
    return {
        "name": data.get("name", ""),
        "url": data.get("url", ""),
        "posts": data.get("posts", {}).get("totalItems", 0),
        "id": data.get("id", ""),
    }


if __name__ == "__main__":
    creds = get_credentials()
    print("Credentials OK, token valid:", creds.valid)
