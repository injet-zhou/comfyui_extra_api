import logging
import os
import traceback

from aiohttp.web import Request, json_response
from server import PromptServer
import folder_paths

from .model_utils.refresh import refresh_folder
from .model_utils.lora import (
    list_available_networks,
    available_networks,
    create_lora_json,
)
from .utils.images import base64_decode_to_pil, extract_img_metadata

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
        data = refresh_folder("loras")
        list_available_networks()
        return success_resp(data=data)
    except Exception as e:
        return error_resp(500, str(e))


@routes.get("/comfyapi/v1/output-images")
async def get_output_images(request: Request):
    try:
        is_temp = request.rel_url.query.get("temp", "false") == "true"
        folder = (
            folder_paths.get_temp_directory()
            if is_temp
            else folder_paths.get_output_directory()
        )
        # iterate through the folder and get the list of images
        images = []
        for root, dirs, files in os.walk(folder):
            for file in files:
                if file.endswith(".png") or file.endswith(".jpg"):
                    image = {"name": file, "full_path": os.path.join(root, file)}
                    images.append(image)
        return success_resp(images=images)
    except Exception as e:
        return error_resp(500, str(e))


@routes.delete("/comfyapi/v1/output-images/{filename}")
async def delete_output_images(request: Request):
    try:
        filename = request.match_info.get("filename")
        if filename is None:
            return error_resp(400, "filename is required")

        if filename[0] == "/" or ".." in filename:
            return error_resp(400, "invalid filename")

        is_temp = request.rel_url.query.get("temp", "false") == "true"
        annotated_file = f"{filename} [{'temp' if is_temp else 'output'}]"
        if not folder_paths.exists_annotated_filepath(annotated_file):
            return error_resp(404, f"file {filename} not found")

        filepath = folder_paths.get_annotated_filepath(annotated_file)
        os.remove(filepath)
        return success_resp()
    except Exception as e:
        return error_resp(500, str(e))


@routes.post("/comfyapi/v1/pnginfo")
async def get_png_info(request: Request):
    try:
        data = await request.json()
        img_base64 = data.get("img_base64")
        if img_base64 is None:
            return error_resp(400, "img_base64 is required")

        img = base64_decode_to_pil(img_base64)
        metadata = extract_img_metadata(img)
        return success_resp(metadata=metadata)
    except Exception as e:
        err = traceback.format_exc()
        logging.error(err)
        return error_resp(500, str(e))


def run_comfyui_extra_api():
    print("extra API server started")
