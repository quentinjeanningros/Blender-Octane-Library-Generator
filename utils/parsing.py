import uuid
import bpy
import re
import os
from pathlib import Path
from .paths import match_files_to_socket_names

def format_material_name(name):
    scene = bpy.context.scene

    # Check if name formatting is enabled
    if not scene.format_name:
        return name

    # Replace specified characters with space
    for char in scene.replace_by_space:
        name = name.replace(char, " ")

    # Add space before capital letters if enabled
    if scene.add_space_by_caps:
        name = re.sub(r"(\B[A-Z])", r" \1", name)

    # Add space between words and numbers if enabled
    if scene.add_space_between_word_and_number:
        name = re.sub(r"(\d+)", r" \1", name)
        name = re.sub(r"(\D)(\d)", r"\1 \2", name)

    name = re.sub(r'\s+', ' ', name).strip()  # Normalize whitespace

    return name

def find_textures(directory):
    # Prepare sockets based on user settings
    sockets = [
        ['base_color', bpy.context.scene.base_color.split(), None],
        ['metallic', bpy.context.scene.metallic.split(), None],
        ['specular', bpy.context.scene.specular.split(), None],
        ['normal', bpy.context.scene.normal.split(), None],
        ['bump', bpy.context.scene.bump.split(), None],
        ['roughness', bpy.context.scene.roughness.split(), None],
        ['gloss', bpy.context.scene.gloss.split(), None],
        ['displacement', bpy.context.scene.displacement.split(), None],
        ['transmission', bpy.context.scene.transmission.split(), None],
        ['emission', bpy.context.scene.emission.split(), None],
        ['alpha', bpy.context.scene.alpha.split(), None],
        ['ambient_occlusion', bpy.context.scene.ambient_occlusion.split(), None]
    ]

    texture_files = {socket[0]: [] for socket in sockets}  # Initialize texture_files dictionary

    # Collect all files in the directory that match the supported image formats
    files = []
    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.exr', '.hdr', '.tiff')):
                files.append(type('obj', (object,), {'name': os.path.join(root, filename)}))

    # Match files to sockets
    match_files_to_socket_names(files, sockets)

    # Populate the texture_files dictionary based on matched sockets
    for socket in sockets:
        if socket[2]:  # If files were matched to this socket
            texture_type = socket[0]
            for matched_file_path in socket[2]:  # Iterate through matched files (now directly using the paths)
                texture_files[texture_type].append(matched_file_path)  # Append the file path directly

    return texture_files