import folder_paths
from comfy import samplers
from PIL import Image, ImageSequence, ImageOps
from io import BytesIO
import base64
import torch
import numpy as np
import node_helpers


def optional_models(folder_name):
    models = folder_paths.get_filename_list(folder_name)
    models.append("none")
    return models


class SimpleGenImageInterface:
    def __init__(self) -> None:
        pass

    @classmethod
    def INPUT_TYPES(cls):
        checkpoints = optional_models("checkpoints")
        return {
            "required": {
                "model": (checkpoints,),
                "prompt": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "",
                    },
                ),
                "negative_prompt": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "",
                    },
                ),
                "width": ("INT", {"default": 512, "min": 64, "max": 4096}),
                "height": ("INT", {"default": 512, "min": 64, "max": 4096}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xFFFFFFFFFFFFFFFF}),
                "steps": ("INT", {"default": 20, "min": 1, "max": 10000}),
                "cfg": (
                    "FLOAT",
                    {
                        "default": 8.0,
                        "min": 0.0,
                        "max": 100.0,
                        "step": 0.1,
                        "round": 0.01,
                    },
                ),
                "sampler_name": (samplers.KSampler.SAMPLERS,),
                "scheduler": (samplers.KSampler.SCHEDULERS,),
                "denoise": (
                    "FLOAT",
                    {"default": 1.0, "min": 0.0, "max": 1.0, "step": 0.01},
                ),
                "img2img_base64": (
                    "STRING",
                    {
                        "multiline": False,
                        "default": "",
                    },
                ),
            }
        }

    RETURN_TYPES = (
        "STRING",
        "STRING",
        "STRING",
        "INT",
        "INT",
        "INT",
        "INT",
        "FLOAT",
        "STRING",
        "STRING",
        "FLOAT",
        "IMAGE",
        "MASK",
    )
    RETURN_NAMES = (
        "model",
        "prompt",
        "negative_prompt",
        "width",
        "height",
        "seed",
        "steps",
        "cfg",
        "sampler_name",
        "scheduler",
        "denoise",
        "image",
        "mask",
    )

    CATEGORY = "extrapi"

    FUNCTION = "execute"

    def base64_to_pil(self, base64_string):
        image = Image.open(BytesIO(base64.b64decode(base64_string)))
        return image

    def extract_image(img: Image.Image):
        output_images = []
        output_masks = []
        for i in ImageSequence.Iterator(img):
            i = node_helpers.pillow(ImageOps.exif_transpose, i)

            if i.mode == "I":
                i = i.point(lambda i: i * (1 / 255))
            image = i.convert("RGB")
            image = np.array(image).astype(np.float32) / 255.0
            image = torch.from_numpy(image)[None,]
            if "A" in i.getbands():
                mask = np.array(i.getchannel("A")).astype(np.float32) / 255.0
                mask = 1.0 - torch.from_numpy(mask)
            else:
                mask = torch.zeros((64, 64), dtype=torch.float32, device="cpu")
            output_images.append(image)
            output_masks.append(mask.unsqueeze(0))

        if len(output_images) > 1:
            output_image = torch.cat(output_images, dim=0)
            output_mask = torch.cat(output_masks, dim=0)
        else:
            output_image = output_images[0]
            output_mask = output_masks[0]

        return output_image, output_mask

    def empty_image(self, width, height):
        return Image.new("RGB", (width, height), color="white")

    def execute(
        self,
        model,
        prompt,
        negative_prompt,
        width,
        height,
        seed,
        steps,
        cfg,
        sampler_name,
        scheduler,
        denoise,
        img2img_base64,
    ):
        if not model or model == 'none':
            model = folder_paths.get_filename_list("checkpoints")[0]

        img = self.empty_image(64, 64)
        if img2img_base64:
            img = self.base64_to_pil(img2img_base64)

        image, mask = self.extract_image(img)

        return (
            model,
            prompt,
            negative_prompt,
            width,
            height,
            seed,
            steps,
            cfg,
            sampler_name,
            scheduler,
            denoise,
            image,
            mask,
        )
