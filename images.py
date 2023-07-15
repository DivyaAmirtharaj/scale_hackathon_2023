import requests

API_URL = "https://api-inference.huggingface.co/models/ogkalu/Comic-Diffusion"
headers = {"Authorization": "Bearer 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"}


def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.content


image_bytes = query(
    {
        "inputs": "Natalie Portman as a 25 year old female scientist, (walking in a tunnel), blue hair, wispy bangs, (white lab coat), (pants), smiling, stunningly beautiful, zeiss lens, half length shot, ultra realistic, octane render, 8k",
    }
)
# You can access the image with PIL.Image for example
import io
from PIL import Image

image = Image.open(io.BytesIO(image_bytes))
# Save as JPEG
image.save("astronaut.jpg", "JPEG")
