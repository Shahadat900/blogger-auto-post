import os
import io
import base64
import google.generativeai as genai
from PIL import Image


def generate_image(prompt: str, output_path: str, alt_text: str = "") -> str:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")

    genai.configure(api_key=api_key)

    model = genai.GenerativeModel("gemini-2.0-flash-exp-image-generation")

    full_prompt = (
        f"Generate a realistic, high-quality blog featured image. "
        f"No text, no watermarks, no logos, no typography in the image. "
        f"Natural lighting, realistic details. "
        f"16:9 aspect ratio. "
        f"{prompt}"
    )

    response = model.generate_content(
        full_prompt,
        generation_config={"response_modalities": ["Text", "Image"]},
    )

    image_data = None
    for part in response._result.candidates[0].content.parts:
        if hasattr(part, "inline_data") and part.inline_data:
            image_data = part.inline_data.data
            break

    if not image_data:
        text_response = response.text if hasattr(response, "text") else ""
        raise RuntimeError(
            f"No image data in Gemini response. Response: {text_response[:200]}"
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
