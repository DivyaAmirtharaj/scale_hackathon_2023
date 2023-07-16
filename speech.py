import modal
from typing import List
from string import ascii_letters
import textwrap
from PIL import ImageFont, Image, ImageDraw

# playwright_image = modal.Image.from_dockerhub("bitnami/pytorch").apt_install("git", "build-essential", "ffmpeg", "libsm6", "libxext6").pip_install("torch", "torchvision", "opencv-python-headless").run_commands("pip install -U git+https://github.com/luca-medeiros/lang-segment-anything.git")
playwright_image = (
    modal.Image.from_dockerhub("nvcr.io/nvidia/pytorch:22.12-py3")
    .run_commands(
        "ln -fs /usr/share/zoneinfo/America/New_York /etc/localtime",
        "export DEBIAN_FRONTEND=noninteractive",
    )
    .apt_install("tzdata")
    .run_commands("dpkg-reconfigure --frontend noninteractive tzdata")
    .apt_install("git", "build-essential", "ffmpeg", "libsm6", "libxext6")
    .pip_install(
        "torch==2.0.1",
        "torchvision",
        index_url="https://download.pytorch.org/whl/cu118",
    )
    .pip_install("opencv-python-headless")
    .run_commands(
        "pip install -U git+https://github.com/luca-medeiros/lang-segment-anything.git"
    )
)

stub = modal.Stub(name="lang-SAM")


def add_text(img: Image, text: str, person: List[float]):
    font_path = "Action-Man/Action_Man.ttf"

    margin = 10
    radius = 20
    outline = 5
    font_size = 20
    max_width = 250

    width_left = person[0]
    width_right = img.size[0] - person[2]

    if width_left > width_right:
        box_width = width_left - margin
        box_center = [box_width // 2, img.height // 2]
    else:
        box_width = width_right + margin
        box_center = [person[2] + box_width // 2, img.height // 2]

    box_center[1] = (
        person[1] // 2
        if person[1] > img.size[1] - person[3]
        else person[3] + (img.size[1] - person[3]) // 2
    )

    box_width = min(box_width, max_width)

    font = ImageFont.truetype(font_path, font_size)
    draw = ImageDraw.Draw(im=img)

    avg_char_width = sum(font.getbbox(char)[2] for char in ascii_letters) / len(
        ascii_letters
    )
    # Translate this average length into a character count
    max_char_count = int(box_width / avg_char_width)
    # Create a wrapped text object using scaled character count
    text = textwrap.fill(text=text, width=max_char_count)
    # Add text to the image
    # draw.text(xy=(img.size[0]/2, img.size[1] / 2), text=text, font=font, fill='#000000', anchor='mm')
    bbox = draw.textbbox(xy=box_center, text=text, font=font, anchor="mm")

    draw.rounded_rectangle(
        xy=[bbox[0] - margin, bbox[1] - margin, bbox[2] + margin, bbox[3] + margin],
        fill="white",
        radius=radius,
        outline="black",
        width=5,
    )
    draw.text(xy=box_center, text=text, font=font, fill="#000000", anchor="mm")


@stub.function(image=playwright_image)
async def get_bounding_boxes(img: Image, gpu="any"):
    prompts = ["head"]
    from lang_sam import LangSAM

    model = LangSAM()
    boxes = []
    for prompt in prompts:
        _, bounding_boxes, _, logits = model.predict(img, prompt)
        sorted_boxes = sorted(zip(bounding_boxes, logits), key=lambda obj: obj[1])
        top_box = sorted_boxes[-1][0]
        boxes.append(top_box)
    return boxes


@stub.local_entrypoint()
def main(img_path, text_message):
    img = Image.open(img_path).convert("RGB")
    boxes = get_bounding_boxes.call(img)
    print(f"Bounding boxes: {boxes}")
    person = boxes[0]
    add_text(img, text_message, person)
    img.save(f"{img_path.split('.')[0]}_processed_{img_path.split('.')[-1]}")
