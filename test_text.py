import requests
from io import BytesIO
import base64
from PIL import Image
import json


def add_text(img_path, text_message):
    buffered = BytesIO()
    img = Image.open(img_path)
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    response = requests.post(
        "https://austrian-code-wizard--lang-sam-main-dev.modal.run",
        data=json.dumps({"img": img_str, "text_message": text_message}),
    )
    js = response
    img_response = js.json()["img"]
    img = Image.open(BytesIO(base64.b64decode(img_response))).convert("RGB")
    img.save(f"./prod/{str(hash(text_message))}.png")
