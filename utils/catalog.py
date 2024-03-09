import uuid
import bpy
import os
from .parsing import format_material_name
from pathlib import Path

def get_catalog_file_path():
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
    # Prepare the override context for the material
    override = context.copy()
    override["id"] = material
    with context.temp_override(**override):
        bpy.ops.ed.lib_id_load_custom_preview( filepath=image_path)
