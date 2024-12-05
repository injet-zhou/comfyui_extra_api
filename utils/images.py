import base64
import json
from io import BytesIO

from PIL import Image

def base64_decode_to_pil(img_base64: str) -> Image:
    img_data = base64.b64decode(img_base64)
    return Image.open(BytesIO(img_data))


def extract_img_metadata(img: Image.Image)-> dict:
    if not hasattr(img, 'text'):
        return {}

    if isinstance(img.text, str):
        metadata = {}
        try:
            metadata = json.loads(img.text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to extract metadata from image: {e}")
    else:
        metadata = img.text
    
    if prompt := metadata.get("prompt"):
        return prompt
    
    return metadata