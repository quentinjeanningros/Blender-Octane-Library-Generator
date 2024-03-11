import uuid
import bpy
import os
from .parsing import format_material_name
from pathlib import Path

def get_catalog_file_path():
    """
    Determines the path to the catalog file associated with the current Blender project.

    This function finds the directory of the current Blender file and constructs the
    path to the catalog file, named 'blender_assets.cats.txt', located in the same directory.
    If the Blender file has not been saved, an error is raised.

    Returns:
    - pathlib.Path: The path to the catalog file.

    Raises:
    - FileNotFoundError: If the Blender file hasn't been saved or the directory doesn't exist.
    """

    # Get the directory of the current Blender file
    blend_file_path = Path(bpy.data.filepath)
    if not blend_file_path:
        # Handle the case where the .blend file hasn't been saved yet
        raise FileNotFoundError("Blender file has not been saved. Please save your work before running this script.")

    # Ensure the .blend file's directory exists (it should, but this is for safety)
    if not blend_file_path.parent.exists():
        raise FileNotFoundError("Directory of the Blender file does not exist.")

    # Define the path to the catalog file next to the Blender file
    catalog_file_path = blend_file_path.parent / "blender_assets.cats.txt"
    return catalog_file_path

def get_or_create_catalog(full_path, base_path):
    """
    Retrieves or creates a catalog entry for a given path within a base path.

    This function checks for the existence of a catalog entry for the specified path.
    If the entry does not exist, a new one is created with a unique UUID. The function
    manages catalog entries by maintaining a simple text file, where each line represents
    a catalog entry in the format 'UUID:path'.

    Parameters:
    - full_path (str): The full path to the item for which a catalog entry is sought.
    - base_path (str): The base path of the Blender project's assets.

    Returns:
    - str: The UUID of the catalog entry, either retrieved or newly created.
    """
    try:
        catalog_file = get_catalog_file_path()
    except FileNotFoundError as e:
        print(e)
        return None

    if not catalog_file.exists():
        catalog_file.touch()

    # Trim the base path from the full path and exclude the material's own directory
    trimmed_path_parts = Path(full_path).relative_to(base_path).parts[:-1]  # Excludes the last directory
    if not trimmed_path_parts:
        # If there are no directories left after trimming, return None to indicate no catalog should be created
        return None

    with open(catalog_file, "r+", encoding="utf-8") as file:
        existing_catalogs = {line.split(":", 1)[1].strip(): line.split(":", 1)[0] for line in file if ":" in line}
        formatted_path = "/".join([format_material_name(part) for part in trimmed_path_parts])

        if formatted_path in existing_catalogs:
            return existing_catalogs[formatted_path]
        else:
            new_uuid = str(uuid.uuid4())
            file.write(f"{new_uuid}:{formatted_path}\n")
            return new_uuid

def set_material_preview_with_operator(context, material, image_path):
    """
    Sets a custom preview image for a material using a Blender operator.

    This function prepares an override context for the specified material and executes
    a Blender operator to load a custom preview image from the given path. This is used
    to visually represent materials within Blender's asset browser.

    Parameters:
    - context (bpy.types.Context): The current Blender context.
    - material (bpy.types.Material): The material for which the preview is set.
    - image_path (str): The path to the image file to use as the preview.
    """

    # Prepare the override context for the material
    override = context.copy()
    override["id"] = material
    with context.temp_override(**override):
        bpy.ops.ed.lib_id_load_custom_preview( filepath=image_path)
