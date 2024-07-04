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
