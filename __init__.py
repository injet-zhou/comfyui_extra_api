from .api_server import run_comfyui_extra_api
from .nodes import SimpleGenImageInterface

NODE_CLASS_MAPPINGS = {
    "SimpleGenImageInterface": SimpleGenImageInterface,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SimpleGenImageInterface": "Simple Gen Image Interface",
}

run_comfyui_extra_api()