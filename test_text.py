import requests
from io import BytesIO
import base64
from PIL import Image
import json

buffered = BytesIO()
img = Image.open("./prod/output_0_0.png")
img.save(buffered, format="PNG")
img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
response = requests.post(
    "https://austrian-code-wizard--lang-sam-main-dev.modal.run",
    data=json.dumps({"img": img_str, "text_message": "Hi how are you?"}),
)
js = response
img_response = js.json()["img"]
img = Image.open(BytesIO(base64.b64decode(img_response))).convert("RGB")
img.save("output.png")
