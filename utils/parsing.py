import os
import re
import bpy
from pathlib import Path
from os import path

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


def split_into_components(fname):
    """
    Split filename into components
    'WallTexture_diff_2k.002.jpg' -> ['Wall', 'Texture', 'diff', 'k']
    """
    # Remove extension
    fname = path.splitext(fname)[0]
    # Remove digits
    fname = "".join(i for i in fname if not i.isdigit())
    # Separate CamelCase by space
    fname = re.sub(r"([a-z])([A-Z])", r"\g<1> \g<2>", fname)
    # Replace common separators with SPACE
    separators = ["_", ".", "-", "__", "--", "#"]
    for sep in separators:
        fname = fname.replace(sep, " ")

    components = fname.split(" ")
    components = [c.lower() for c in components]
    return components


def remove_common_prefix(names_to_key_lists):
    """
    Accepts a mapping of file names to key lists that should be used for socket
    matching.

    This function modifies the provided mapping so that any common prefix
    between all the key lists is removed.

    Returns true if some prefix was removed, false otherwise.
    """
    if not names_to_key_lists:
        return False
    sample_keys = next(iter(names_to_key_lists.values()))
    if not sample_keys:
        return False

    common_prefix = sample_keys[0]
    for key_list in names_to_key_lists.values():
        if key_list[0] != common_prefix:
            return False

    for name, key_list in names_to_key_lists.items():
        names_to_key_lists[name] = key_list[1:]
    return True


def remove_common_suffix(names_to_key_lists):
    """
    Accepts a mapping of file names to key lists that should be used for socket
    matching.

    This function modifies the provided mapping so that any common suffix
    between all the key lists is removed.

    Returns true if some suffix was removed, false otherwise.
    """
    if not names_to_key_lists:
        return False
    sample_keys = next(iter(names_to_key_lists.values()))
    if not sample_keys:
        return False

    common_suffix = sample_keys[-1]
    for key_list in names_to_key_lists.values():
        if key_list[-1] != common_suffix:
            return False

    for name, key_list in names_to_key_lists.items():
        names_to_key_lists[name] = key_list[:-1]
    return True


def match_files_to_keys(files, keys):
    """
    Returns a mapping from file names to key lists that should be used for
    classification.

    A file is something that we can do x.name on to figure out the file name.

    A socket is a tuple containing:
    * name
    * list of keys
    * a None field where the selected file name will go later. Ignored by us.
    """

    names_to_key_lists = {}
    for file in files:
        names_to_key_lists[file] = split_into_components(file)

    while len(names_to_key_lists) > 1:
        something_changed = False

        # Common prefixes / suffixes provide zero information about what file
        # should go to which socket, but they can confuse the mapping. So we get
        # rid of them here.
        something_changed |= remove_common_prefix(names_to_key_lists)
        something_changed |= remove_common_suffix(names_to_key_lists)

        # Names matching zero keys provide no value, remove those
        names_to_remove = set()
        for name, key_list in names_to_key_lists.items():
            match_found = False
            for key in key_list:
                if key in keys:
                    match_found = True

            if not match_found:
                names_to_remove.add(name)

        for name_to_remove in names_to_remove:
            del names_to_key_lists[name_to_remove]
            something_changed = True

        if not something_changed:
            break

    return names_to_key_lists


def fetch_files_at_path(path, valid_extensions):
    all_files = os.listdir(path)
    filtered_files = [
        file for file in all_files
        if file.lower().endswith(valid_extensions)
    ]
    return filtered_files
