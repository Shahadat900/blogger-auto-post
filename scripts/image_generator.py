import os
import io
import json
import base64
import time
from pathlib import Path
import requests
from PIL import Image


def generate_image(prompt: str, output_path: str, alt_text: str = "") -> str:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")

    model = "gemini-2.0-flash-exp-image-generation"
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={api_key}"
    )

    full_prompt = (
        f"Generate a realistic, high-quality blog featured image. "
        f"No text, no watermarks, no logos, no typography in the image. "
        f"Natural lighting, realistic details. "
        f"16:9 aspect ratio. "
        f"{prompt}"
    )

    payload = {
        "contents": [{"parts": [{"text": full_prompt}]}],
        "generationConfig": {
            "responseModalities": ["Text", "Image"],
            "temperature": 0.4,
        },
    }

    for attempt in range(3):
        resp = requests.post(url, json=payload, timeout=120)
        if resp.status_code == 429:
            wait = 15 * (attempt + 1)
            print(f"  Image generation rate limited. Waiting {wait}s...")
            time.sleep(wait)
            continue
        resp.raise_for_status()
        data = resp.json()
        break
    else:
        raise RuntimeError("Image generation rate limit exceeded after 3 retries.")



    image_data = None
    try:
        parts = data["candidates"][0]["content"]["parts"]
        for part in parts:
            if "inlineData" in part:
                image_data = base64.b64decode(part["inlineData"]["data"])
                break
    except (KeyError, IndexError) as e:
        raise RuntimeError(
            f"Gemini image API error: {json.dumps(data, indent=2)[:500]}"
        ) from e

    if not image_data:
        raise RuntimeError(
            "No image data in Gemini response. The model may not support image generation."
        )

    img = Image.open(io.BytesIO(image_data))
    img.save(output_path, "PNG")

    return output_path


def generate_and_save(prompt: str, alt_text: str, index: int = 1) -> tuple:
    ext = "png"
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "temp_images")
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, f"featured_{index}.{ext}")
    generate_image(prompt, output_path, alt_text)

    return output_path, alt_text


if __name__ == "__main__":
    import sys

    prompt = sys.argv[1] if len(sys.argv) > 1 else "A beautiful mosque at sunset"
    path, alt = generate_and_save(prompt, "test image")
    print(f"Image saved to: {path}")
    print(f"Alt text: {alt}")
