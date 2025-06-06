# ComfyUI Extra API

This is a collection of extra API functions that are not included in the default ComfyUI API.

## Get started
1. go to custom_nodes
   ```bash
    cd custom_nodes
   ```
2. clone the repository
   ```bash
    git clone https://github.com/injet-zhou/comfyui_extra_api.git
    cd comfyui_extra_api
   ```
3. install the dependencies
   
   use poetry(Recommended)
   ```bash
    poetry install
   ```
    or use pip
   ```bash
    pip install -r requirements.txt
   ```
   start using the extra API functions in your ComfyUI project.

## Endpoints
1. `/comfyapi/v1/checkpoints`

   Method: Get

   Description: Get all the checkpoints.

2. `/comfyapi/v1/refresh-checkpoints`

    Method: Post

    Description: Refresh the list of checkpoints and return the updated list.

3. `/comfyapi/v1/loras`

   Method: Get

   Description: Get all the LoRa.

4. `/comfyapi/v1/refresh-loras`

    Method: Post

    Description: Refresh the list of LoRa and return the updated list.

5. `/comfyapi/v1/output-images`

    Method: Get

    Query: `temp`  true or false

    Description: List all the output images, if `temp` is true, only list the temporary output images which are generated in `PreviewImage` node.

6. `comfyapi/v1/output-images/{filename}`

    Method: Delete

    Query: `temp`  true or false

    Description: Delete the output image with the given filename, if `temp` is true, only delete the temporary output image which is generated in `PreviewImage` node.

7. `/comfyapi/v1/pnginfo`
   
   Method: Post
   
   Body: `{"img_base64": "base64 string of the image"}`

   Description: Get the metadata of the PNG image. If the image is generated by ComfyUI, it's a workflow json.

8. `/comfyapi/v1/input-images/{filename}`

   Method: Delete

   Description: Delete the input image with the given filename.
