import os
from aiohttp.web import Request, json_response
from server import PromptServer
import folder_paths

from .model_utils.refresh import refresh_folder
from .model_utils.lora import (
    list_available_networks,
    available_networks,
    create_lora_json,
)

routes = PromptServer.instance.routes


def success_resp(**kwargs):
    return json_response({"code": 200, "message": "success", **kwargs})


def error_resp(code, message, **kwargs):
    return json_response({"code": code, "message": message, **kwargs})


@routes.get("/comfyapi/v1/checkpoints")
async def get_checkpoints(request: Request):
    try:
        checkpoints = folder_paths.get_filename_list("checkpoints")
        result = [
            {
                "name": os.path.basename(ckpt),
                "path": ckpt,
                "full_path": folder_paths.get_full_path("checkpoints", ckpt) or ckpt,
            }
            for ckpt in checkpoints
        ]
        return success_resp(result=result)
    except Exception as e:
        return error_resp(500, str(e))


@routes.post("/comfyapi/v1/refresh-checkpoints")
async def refresh_checkpoints(request: Request):
    """Refresh the checkpoints list and return the updated list(maybe useful for models that stored in a network storage)"""
    try:
        data = refresh_folder("checkpoints")
        return success_resp(data=data)
    except Exception as e:
        return error_resp(500, str(e))


@routes.get("/comfyapi/v1/loras")
async def get_loras(request: Request):
    try:
        loras = loras = [
            create_lora_json(obj=obj) for obj in available_networks.values()
        ]
        return success_resp(loras=loras)
    except Exception as e:
        return error_resp(500, str(e))


@routes.post("/comfyapi/v1/refresh-loras")
async def refresh_loras(request: Request):
    try:
        list_available_networks()
        return success_resp()
    except Exception as e:
        return error_resp(500, str(e))


def run_comfyui_extra_api():
    print("extra API server started")
