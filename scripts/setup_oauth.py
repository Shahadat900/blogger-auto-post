import os
import json
import webbrowser
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = ["https://www.googleapis.com/auth/blogger"]
ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")


def save_to_env(client_id, client_secret, refresh_token):
    existing = {}
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH, "r") as f:
            for line in f:
                line = line.strip()
                if "=" in line:
                    k, v = line.split("=", 1)
                    existing[k.strip()] = v.strip()

    existing["BLOGGER_CLIENT_ID"] = client_id
    existing["BLOGGER_CLIENT_SECRET"] = client_secret
    existing["BLOGGER_REFRESH_TOKEN"] = refresh_token

    with open(ENV_PATH, "w") as f:
        for k, v in existing.items():
            if v:
                f.write(f"{k}={v}\n")

    print(f"  Saved to {ENV_PATH}")


def main():
    print("=" * 55)
    print("  Blogger OAuth Setup (One-Time)")
    print("=" * 55)
    print()
    print("This will generate a Refresh Token for automatic posting.")
    print()
    print("How to get Client ID and Client Secret:")
    print("  1. Go to https://console.cloud.google.com")
    print("  2. Select your project")
    print("  3. APIs & Services -> Credentials")
    print("  4. Create Credentials -> OAuth 2.0 Client ID")
    print("  5. Application type: Desktop app")
    print("  6. Download the JSON file")
    print()

    client_id = input("Client ID: ").strip()
    while not client_id:
        client_id = input("Client ID (required): ").strip()

    client_secret = input("Client Secret: ").strip()
    while not client_secret:
        client_secret = input("Client Secret (required): ").strip()

    print()
    print("Opening browser for authorization...")

    client_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost"],
        }
    }

    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)

    try:
        creds = flow.run_local_server(port=0, open_browser=True)
    except Exception:
        print()
        print("Browser didn't open automatically.")
        print("Run the following URL in your browser:")
        auth_url, _ = flow.authorization_url()
        print()
        print(auth_url)
        print()
        code = input("Paste the authorization code here: ").strip()
        flow.fetch_token(code=code)
        creds = flow.credentials

    refresh_token = creds.refresh_token

    if not refresh_token:
        print()
        print("No refresh token received. Trying again with access_type=offline...")
        flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
        creds = flow.run_local_server(
            port=0, open_browser=True, access_type="offline", prompt="consent"
        )
        refresh_token = creds.refresh_token

    if not refresh_token:
        print("Error: Could not obtain refresh token. Make sure you grant full access.")
        return

    print()
    print("=" * 55)
    print("  OAuth Setup Complete!")
    print("=" * 55)
    print()
    print("  Client ID:", client_id[:20] + "...")
    print("  Client Secret:", client_secret[:10] + "...")
    print("  Refresh Token:", refresh_token[:30] + "...")
    print()

    save_to_env(client_id, client_secret, refresh_token)

    print()
    print("Add these to your GitHub Secrets:")
    print()
    print(f"  BLOGGER_CLIENT_ID: {client_id}")
    print(f"  BLOGGER_CLIENT_SECRET: {client_secret}")
    print(f"  BLOGGER_REFRESH_TOKEN: {refresh_token}")
    print(f"  BLOGGER_BLOG_ID: (get from config.json)")
    print()


if __name__ == "__main__":
    main()
