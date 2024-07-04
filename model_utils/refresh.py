import folder_paths


def refresh_folder(folder_name: str) -> list:
    if not folder_name:
        raise ValueError("folder_name is required")
    
    if folder_name not in folder_paths.folder_names_and_paths:
        raise ValueError("invalid folder_name or folder_name not initialized")
    
    result = folder_paths.get_filename_list_(folder_name)
    folder_paths.filename_list_cache[folder_name] = result

    return result[0]