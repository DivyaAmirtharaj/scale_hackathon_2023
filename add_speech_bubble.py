import base64
import textwrap
from math import sqrt
from io import BytesIO
from typing import List, Dict
from string import ascii_letters
from PIL import ImageFont, Image as PILImage, ImageDraw

from modal import Image, Stub, method, web_endpoint


def download_weights():
    from lang_sam import LangSAM
    _ = LangSAM()


sam_image = (
    Image.from_dockerhub("pytorch/pytorch:2.0.1-cuda11.7-cudnn8-devel")
    .apt_install("git", "gcc", "build-essential", "wget", "unzip")
    .run_commands(
        "ln -fs /usr/share/zoneinfo/America/New_York /etc/localtime",
        "export DEBIAN_FRONTEND=noninteractive"
    ).apt_install("tzdata")
    .run_commands(
        "dpkg-reconfigure --frontend noninteractive tzdata"
    )
    .apt_install("ffmpeg", "libsm6", "libxext6")
    .pip_install(
        "torch",
        "torchvision",
        "torchaudio",
        "opencv-python-headless", gpu="any")
    .run_commands(
        "pip install -U git+https://github.com/luca-medeiros/lang-segment-anything.git", gpu="any"
    )
    .run_function(download_weights, gpu="any")
    .run_commands(
        "wget https://www.fontsquirrel.com/fonts/download/Action-Man -O ~/Action-Man.zip",
        "unzip ~/Action-Man.zip -d ~/Action-Man"
    )
)


stub = Stub(name="lang-SAM")

class Model:
    def __init__(self) -> None:
        from lang_sam import LangSAM
        self.model = LangSAM()

    def predict(self, x, y):
        import torch
        print(f"Got torch {torch.cuda.is_available()}")

        if self.model is None:
            print("is none")
            self.__enter__()
        else:
            print("found model")
        return self.model.predict_dino(x, y, box_threshold=0.3, text_threshold=0.25)
        # boxes, logits, _ = self.model.predict(x, y)
        #return boxes, logits, None


def add_text(img: PILImage, text: str, man: List[float]):
    font_path = "/root/Action-Man/Action_Man.ttf"
    margin = 10
    radius = 20
    outline = 5
    font_size = 20
    max_width = 250

    width_left = man[0]
    width_right = img.size[0] - man[2]

    if width_left > width_right:
        box_width = width_left - margin
        box_center = [box_width // 2, img.height // 2]
    else:
        box_width = width_right + margin
        box_center = [man[2] + box_width // 2, img.height // 2]

    box_center[1] = man[1] // 2 if man[1] > img.size[1] - man[3] else man[3] + (img.size[1] - man[3]) // 2

    box_width = min(box_width, max_width)

    font = ImageFont.truetype(font_path, font_size)
    draw = ImageDraw.Draw(im=img)

    avg_char_width = sum(font.getbbox(char)[2] for char in ascii_letters) / len(ascii_letters)
    # Translate this average length into a character count
    max_char_count = int(box_width / avg_char_width)
    # Create a wrapped text object using scaled character count
    text = textwrap.fill(text=text, width=max_char_count)
    # Add text to the image
    bbox = draw.textbbox(xy=box_center, text=text, font=font, anchor='mm')
    draw.rounded_rectangle(xy=[bbox[0] - margin, bbox[1] - margin, bbox[2] + margin, bbox[3] + margin], fill="white", radius=radius, outline="black", width=5)
    draw.text(xy=[ bbox[0], bbox[1]], text=text, font=font, fill='#000000')

    corners = [(bbox[0], bbox[1]), (bbox[0], bbox[3]), (bbox[2], bbox[1]), (bbox[2], bbox[3])]
    head_center = [(man[2] - man[0]) // 2 + man[0], (man[3] - man[1]) // 2 + man[1]]
    dists = [sqrt((corner[0] - head_center[0]) ** 2 + (corner[1] - head_center[1]) ** 2) for corner in corners]
    min_corner = corners[dists.index(min(dists))]

    line_vec = [min_corner[0] - head_center[0], min_corner[1] - head_center[1]]
    normal_vec = [-line_vec[0], line_vec[1]]
    normalized_vec = [normal_vec[0] / sqrt(normal_vec[0]**2 + normal_vec[1]**2), normal_vec[1] / sqrt(normal_vec[0]**2 + normal_vec[1]**2)]

    triang_1 = [min_corner[0] + 10 * normalized_vec[0], min_corner[1] + 10 * normalized_vec[1]]
    triang_2 = [min_corner[0] - 10 * normalized_vec[0], min_corner[1] - 10 * normalized_vec[1]]

    triang_3 = [head_center[0] - (man[3] - man[1]) * normalized_vec[0], head_center[1] + (man[2] - man[0]) * normalized_vec[1]]

    draw.polygon(xy=[tuple(triang_1), tuple(triang_2), tuple(triang_3)], fill="white", outline="black", width=2)


def get_bounding_boxes(model, img: Image):
    prompts = ["head"]
    boxes = []
    for prompt in prompts:
        bounding_boxes, logits, _ = model.predict(img, prompt)
        sorted_boxes = sorted(zip(bounding_boxes, logits), key=lambda obj: obj[1])
        top_box = sorted_boxes[-1][0]
        boxes.append(top_box)
    return boxes

@stub.function(image=sam_image, gpu="any", cpu=8)
@web_endpoint(method="POST")
def main(item: Dict):
    imgs = item["imgs"]
    text_messages = [m.strip() for m in item["text_messages"]]
    img_strs = []
    model = Model()
    for img, text_message in zip(imgs, text_messages):
      img = PILImage.open(BytesIO(base64.b64decode(img))).convert("RGB")
      boxes = get_bounding_boxes(model, img)
      print(f"Bounding boxes: {boxes}")
      person = boxes[0]
      add_text(img, text_message, person)
      buffered = BytesIO()
      img.save(buffered, format="PNG")
      img_str = base64.b64encode(buffered.getvalue())
      img_strs.append(img_str)
    return {"imgs": img_strs}
    