from __future__ import annotations

import io
import os
import time
from pathlib import Path
from process_text import (
    gpt_output_to_diffusion_prompt,
    dialogue_to_gpt_input,
    dialogue_cleaned,
)
from test_text import add_text

from modal import Image, Secret, Stub, method

stub = Stub("kachow-image-gen")

model_id = "ogkalu/Comic-Diffusion"
cache_path = "/vol/cache"


def download_models():
    import diffusers
    import torch

    hugging_face_token = os.environ["HUGGINGFACE_TOKEN"]

    # Download scheduler configuration. Experiment with different schedulers
    # to identify one that works best for your use-case.
    scheduler = diffusers.DPMSolverMultistepScheduler.from_pretrained(
        model_id,
        subfolder="scheduler",
        use_auth_token=hugging_face_token,
        cache_dir=cache_path,
    )
    scheduler.save_pretrained(cache_path, safe_serialization=True)

    # Downloads all other models.
    pipe = diffusers.DiffusionPipeline.from_pretrained(
        model_id,
        use_auth_token=hugging_face_token,
        torch_dtype=torch.float16,
        cache_dir=cache_path,
    )
    pipe.save_pretrained(cache_path, safe_serialization=True)


image = (
    Image.debian_slim(python_version="3.10")
    .pip_install(
        "accelerate",
        "diffusers[torch]>=0.15.1",
        "ftfy",
        "torchvision",
        "transformers~=4.25.1",
        "triton",
        "safetensors",
    )
    .pip_install(
        "torch==2.0.1+cu117",
        find_links="https://download.pytorch.org/whl/torch_stable.html",
    )
    .pip_install("xformers", pre=True)
    .run_function(
        download_models,
        secrets=[Secret.from_name("my-huggingface-secret")],
    )
)
stub.image = image


@stub.cls(gpu="A10G")
class ComicDiffusion:
    def __enter__(self):
        import diffusers
        import torch

        torch.backends.cuda.matmul.allow_tf32 = True

        scheduler = diffusers.DPMSolverMultistepScheduler.from_pretrained(
            cache_path,
            subfolder="scheduler",
            solver_order=2,
            prediction_type="epsilon",
            thresholding=False,
            algorithm_type="dpmsolver++",
            solver_type="midpoint",
            denoise_final=True,  # important if steps are <= 10
            low_cpu_mem_usage=True,
            device_map="auto",
        )
        self.pipe = diffusers.StableDiffusionPipeline.from_pretrained(
            cache_path,
            scheduler=scheduler,
            low_cpu_mem_usage=True,
            device_map="auto",
        )
        self.pipe.enable_xformers_memory_efficient_attention()

    @method()
    def run_inference(
        self, prompt: str, steps: int = 20, batch_size: int = 4
    ) -> list[bytes]:
        import torch

        with torch.inference_mode():
            with torch.autocast("cuda"):
                images = self.pipe(
                    [prompt] * batch_size,
                    num_inference_steps=steps,
                    guidance_scale=12.0,
                ).images

        # Convert to PNG bytes
        image_output = []
        for image in images:
            with io.BytesIO() as buf:
                image.save(buf, format="PNG")
                image_output.append(buf.getvalue())
        return image_output


@stub.local_entrypoint()
def entrypoint(samples: int = 1, steps: int = 40, batch_size: int = 1):
    with open("dialogue.txt", "r") as f:
        # Read the file
        dialogue = f.read()
    dialogue_only = dialogue_cleaned(dialogue)
    gpt_output = dialogue_to_gpt_input(dialogue)
    diffusion_prompts = gpt_output_to_diffusion_prompt(gpt_output)

    dir = Path("./prod")
    if not dir.exists():
        dir.mkdir(exist_ok=True, parents=True)

    sd = ComicDiffusion()
    for k, prompt in enumerate(diffusion_prompts[1:]):
        for i in range(samples):
            t0 = time.time()
            images = sd.run_inference.call(prompt, steps, batch_size)
            total_time = time.time() - t0
            print(
                f"Sample {i} took {total_time:.3f}s ({(total_time)/len(images):.3f}s / image)."
            )
            for j, image_bytes in enumerate(images):
                output_path = dir / f"output_{k}_{i}.png"
                print(f"Saving it to {output_path}")
                path_str = str(output_path.absolute())
                with open(path_str, "wb") as f:
                    f.write(image_bytes)

                dialogue_k = dialogue_only[k]
                add_text(path_str, dialogue_k)
